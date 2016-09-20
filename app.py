import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import psycopg2

app = Flask(__name__)
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


@app.route('/', methods=['GET', 'POST'])
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
            where replace(upper(d.COMPANY_CONFORMED_NAME), \' \', \'\') like
                \'%""" + cname.upper().replace(' ', '') + """%\'
            """

            cursor.execute(query)

            top_sims = cursor.fetchall()
            primary_name = top_sims[0][1].upper().replace('&AMP;', '&')
            results.append(
                'Showing results for ' +
                primary_name + ' [' + top_sims[0][2] + ']')

            for i in range(3):
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


if __name__ == '__main__':
    app.run()
