from flask import Flask, render_template, request, jsonify, g
from flask_stormpath import login_required, user
from bokeh.embed import components

from connect import get_es
from config import set_config
from utils import comp_case
from visualizations import get_scatter
from search import get_sim_results

app = Flask(__name__)
set_config(app)

@app.context_processor
def inject_user():
    return dict(is_authenticated=user.is_authenticated)


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


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/model', methods=['GET'])
@login_required
def model():
    return render_template('model.html')


@app.route('/describe', methods=['GET'])
@login_required
def describe():
    return render_template('describe.html')


@app.route('/explore', methods=['GET'])
@login_required
def graph():
    plot = get_scatter()
    script, div = components(plot)
    return render_template(
        'explore.html', page='explore', script=script, div=div)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():

    # Initialize variables to empty to prevent runtime errors
    # if no hits are found
    errors = []
    results = {}
    match = {}
    target = None
    sim_ids = []
    div = None
    script = ''

    if request.method == "POST":
        # Try getting results from SQL table, otherwise raise error
        try:
            top_sims, match, target, results, sim_ids = get_sim_results()
        except:
            errors.append(
                "Unable to find similar companies -- please try again"
            )

    if target is not None:
        # Get scatter plot if results were found
        plot = get_scatter(target, sim_ids)
        script, div = components(plot)

    return render_template(
        'search.html', page='search', errors=errors, match=match,
        results=results, div=div, script=script)


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
