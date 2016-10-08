import os
from flask import Flask, render_template, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from flask_bootstrap import Bootstrap
import auth.http_basic as auth
import re
import pandas as pd
import matplotlib as mpl
import matplotlib.cm as cmx
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.embed import components


app = Flask(__name__)
Bootstrap(app)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

AWS_RDS_HOST = os.environ['AWS_RDS_HOST']
AWS_RDS_USER = os.environ['AWS_RDS_USER']
AWS_RDS_PASSWORD = os.environ['AWS_RDS_PASSWORD']
AWS_ES_ACCESS_KEY = os.environ['***REMOVED***']
AWS_ES_SECRET_KEY = os.environ['AWS_SECRET_ACCESS_KEY']


def set_scatter_data():
    cursor = get_db()
    cursor.execute(
        'select E.X1, E.X2, C.sic_cd, C.name, C.id '
        'from embedded E '
        'inner join company_dets C on E.id = C.id')
    SNE_vecs = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    return pd.DataFrame(SNE_vecs, columns=colnames)


def get_scatter_data():
    if not hasattr(g, 'vecs'):
        g.vecs = set_scatter_data()
    return g.vecs


# Connect to AWS RDS
def _connect_db():
    conn_string = "host='" + AWS_RDS_HOST + \
                  "' dbname='comparatory' user='" + AWS_RDS_USER + \
                  "' password='" + AWS_RDS_PASSWORD + "'"
    conn = psycopg2.connect(conn_string)
    return conn.cursor()


# Connect to local RDS
def _connect_db_local():
    conn_string = "host='localhost' dbname='ind'"
    conn = psycopg2.connect(conn_string)
    return conn.cursor()


# Connnect to AWS elasticsearch
def _connect_es():
    host = os.environ['ES_HOST']
    awsauth = AWS4Auth(AWS_ES_ACCESS_KEY, AWS_ES_SECRET_KEY,
                       'us-east-1', 'es')
    es = Elasticsearch(
        hosts=[host],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    return es


# Connnect to local elasticsearch
def _connect_es_local():
    es = Elasticsearch()
    return es


# Opens a new elasticsearch connection if there is none yet for the
# current application context
def get_es():
    if not hasattr(g, 'es_node'):
        g.es_node = _connect_es()
    return g.es_node


# Opens a new database connection if there is none yet for the
# current application context
def get_db():
    if not hasattr(g, 'psql_db'):
        g.psql_db = _connect_db()
    return g.psql_db


# Closes the database again at the end of the request
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'psql_db'):
        g.psql_db.close()


@app.route('/autocomplete', methods=['GET'])
def autocomplete(max_results=10):
    es = get_es()
    target_name = request.args.get('q')
    query = {"query": {"match": {
        "NAME": target_name}},
        "_source": "NAME", "size": max_results}
    resp = es.search('comparatory', 'company', query)['hits']['hits']
    assert len(resp) <= max_results

    names = [comp_case(d['_source']['NAME']) for d in resp]
    return jsonify(matching_results=names)


def comp_case(name):
    return " ".join(w.capitalize() for w in name.split())


def decomp_case(name):
    return name.upper().replace("'", "''")


@app.route('/explore', methods=['GET'])
def graph():
    plot = get_scatter()
    script, div = components(plot)
    return render_template(
        'explore.html', page='explore', script=script, div=div)


@app.route('/search', methods=['GET', 'POST'])
@auth.requires_auth
def index():

    es = get_es()
    cursor = get_db()

    errors = []
    match = {}
    results = {}
    target = None
    sim_ids = []

    if request.method == "POST":

        try:
            # User entry: get company name
            cname = request.form['company-name']

            es_query = {"query": {"match": {
                "NAME": cname}},
                "_source": "NAME", "size": 1}
            resp = es.search(
                'comparatory', 'company', es_query)['hits']['hits']
            assert len(resp) == 1
            name_match = [d['_source']['NAME'].upper() for d in resp][0]

            # Find next most similar
            query = """
            select
                d.id as primary_id
                ,d.name as primary_name
                ,d.sic_cd as primary_sic_cd
                ,d.zip as primary_zip
                ,d.city as primary_city
                ,d.state as primary_state
                ,d.state_of_incorporation as primary_state_inc
                ,d.irs_number as primary_irs_number
                ,d.filed_as_of_date as primary_filed_dt
                ,d.business_description as primary_bus_desc
                ,n.sim_score
                ,n.sim_rank
                ,s.id as next_id
                ,s.name as next_name
                ,s.sic_cd as next_sic_cd
                ,s.zip as next_zip
                ,s.city as next_city
                ,s.state as next_state
                ,s.state_of_incorporation as next_state_inc
                ,s.irs_number as next_irs_number
                ,s.filed_as_of_date as next_filed_dt
                ,s.business_description as next_bus_desc
                ,d.raw_description as primary_raw_desc
                ,s.raw_description as next_raw_desc
            from company_dets d
            inner join sims n
                on d.id = n.id
            inner join company_dets s
                on n.sim_id = s.id
            where d.NAME =
                \'""" + decomp_case(name_match) + """\'
            """

            cursor.execute(query)

            top_sims = cursor.fetchall()
            match['name'] = comp_case(str(top_sims[0][1]))
            match['sic_cd'] = str(top_sims[0][2])
            match['business_desc'] = clean_desc(top_sims[0][22])
            target = top_sims[0][0]

            for i in range(5):
                next_b = top_sims[i]
                results[i + 1] = {
                    'name': comp_case(str(next_b[13])),
                    'sic_cd': str(next_b[14]),
                    'sim_score': str('{0:2.0f}%'.format(next_b[10] * 100)),
                    'business_desc': clean_desc(next_b[23])
                }
                sim_ids.append(next_b[12])

        except:
            errors.append(
                "Unable to find similar companies -- please try again"
            )

    div = None
    script = ''
    if target is not None:
        plot = get_scatter(target, sim_ids)
        script, div = components(plot)
    return render_template(
        'search.html', page='search', errors=errors, match=match,
        results=results, div=div, script=script)


def clean_desc(raw):
    despaced = ' '.join(filter(lambda x: x != '', raw.split(' ')))
    item1 = re.compile('(\ *)ITEM 1(\.*) BUSINESS(\.*)', re.IGNORECASE)
    desc = item1.sub('', despaced).strip()
    return filter(lambda x: x != '', desc.split('\n'))


def get_scatter(target=None, sim_ids=None):
    vecs = get_scatter_data()
    theme = cmx.get_cmap('viridis')
    cNorm = mpl.colors.Normalize(vmin=0, vmax=9999)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=theme)

    colors = []

    if target is not None:
        dot_size = []
        alpha = []
        # Color based on proximity to target
        for i in vecs['id']:
            if i == target:
                colors.append("#e844d4")
                dot_size.append([9])
                alpha.append([.9])
            elif i in sim_ids:
                colors.append("#44e858")
                dot_size.append([8])
                alpha.append([.8])
            else:
                colors.append("#acacac")
                dot_size.append([7])
                alpha.append([.5])
    else:
        dot_size = 3
        alpha = .5
        # Color based on SIC code
        for s in vecs['sic_cd']:
            try:
                colorVal = scalarMap.to_rgba(int(s))
                colors.append("#%02x%02x%02x" % (
                    colorVal[0] * 255, colorVal[1] * 255, colorVal[2] * 255))
            except:
                colors.append("#d3d3d3")

    source = ColumnDataSource(
        data=dict(
            x=list(vecs['x1']),
            y=list(vecs['x2']),
            desc=list(vecs['sic_cd']),
            name=list([comp_case(v) for v in vecs['name']]),
        )
    )

    hover = HoverTool(
        tooltips=[
            ("Name", "@name"),
            ("SIC", "@desc"),
        ]
    )

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    plot = figure(tools=[hover, TOOLS])
    plot.scatter(
        'x', 'y', source=source, color=colors, alpha=.5, size=dot_size)
    plot.toolbar.logo = None
    plot.axis.visible = False
    plot.grid.visible = False
    plot.sizing_mode = 'scale_width'

    # Zoom in on specified company
    if target is not None:
        zoom = 0.1
        margin = 0.05
        t_point = vecs[vecs['id'] == target].iloc[0]
        joint = sim_ids + [target]
        joint_df = vecs[vecs['id'].isin(joint)]
        x_min = joint_df['x1'].min()
        x_max = joint_df['x1'].max()
        y_min = joint_df['x2'].min()
        y_max = joint_df['x2'].max()
        max_diff = max(
            t_point['x1'] - x_min,
            x_max - t_point['x1'],
            t_point['x2'] - y_min,
            y_max - t_point['x2'],
        )
        z = max(zoom, max_diff + margin)

        plot.x_range.start = t_point['x1'] - z
        plot.x_range.end = t_point['x1'] + z
        plot.y_range.start = t_point['x2'] - z
        plot.y_range.end = t_point['x2'] + z

    return plot


@app.errorhandler(401)
def custom_401(error):
    return render_template('401.html'), 401


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run()
