import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from elasticsearch import Elasticsearch
from flask_bootstrap import Bootstrap
import auth.http_basic as auth


app = Flask(__name__)
Bootstrap(app)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Connect to AWS RDS
try:
    conn_string = """
        host='***REMOVED***'
        dbname='comparatory' user='***REMOVED***' password='***REMOVED***'"""
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

except psycopg2.DatabaseError:
    if conn:
        conn.rollback()

# Connnect to AWS elasticsearch
es_local = Elasticsearch('localhost')
es_aws = Elasticsearch(
    '***REMOVED***'
    'amazonaws.com/', verify_certs=True)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    max_results = 10
    target_name = "american internatonal group"
    target_name = request.args.get('q')
    query = {"query": {"match": {
        "dets.COMPANY CONFORMED NAME": target_name}},
        "_source": "dets.COMPANY CONFORMED NAME", "size": max_results}
    resp = es_aws.search('comparatory', 'company', query)['hits']['hits']
    assert len(resp) <= max_results

    names = [d['_source']['dets']
             ['COMPANY CONFORMED NAME'].upper() for d in resp]
    return jsonify(matching_results=names)


@app.route('/', methods=['GET', 'POST'])
@auth.requires_auth
def index():
    errors = []
    results = []
    if request.method == "POST":

        try:

            # User entry: get company name
            cname = request.form['company-name']

            # Find next most similar
            query = """
            select
                d.id as primary_id
                ,d.company_conformed_name as primary_name
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
                ,s.company_conformed_name as next_name
                ,s.sic_cd as next_sic_cd
                ,s.zip as next_zip
                ,s.city as next_city
                ,s.state as next_state
                ,s.state_of_incorporation as next_state_inc
                ,s.irs_number as next_irs_number
                ,s.filed_as_of_date as next_filed_dt
                ,s.business_description as next_bus_desc
            from company_dets d
            inner join sims n
                on d.id = n.id
            inner join company_dets s
                on n.sim_id = s.id
            where replace(upper(d.COMPANY_CONFORMED_NAME), \' \', \'\') =
                \'""" + cname.upper().replace(' ', '') + """\'
            """

            cursor.execute(query)

            top_sims = cursor.fetchall()
            primary_name = top_sims[0][1].upper().replace('&AMP;', '&')
            results.append(
                'Showing results for ' +
                primary_name + ' [' + top_sims[0][2] + ']')

            for i in range(5):
                next_b = top_sims[i]
                next_name = next_b[13].upper().replace('&AMP;', '&')
                results.append(
                    str(next_b[11]) + '. ' + next_name + ' [' +
                    next_b[14] + ']')
                results.append(
                    '{0:2.0f}% similarity score'.format(next_b[10] * 100))
                # results.append(next_b[21])

        except:
            errors.append(
                "Unable to find similar companies -- please try again"
            )

    return render_template('index.html', errors=errors, results=results)


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
        return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
