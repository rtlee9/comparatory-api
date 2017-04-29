import os
import psycopg2
from elasticsearch import Elasticsearch, RequestsHttpConnection
from flask import g
from requests_aws4auth import AWS4Auth
from flask import current_app as app


# Connect to AWS RDS
def _connect_db():
    conn_str = "host='{}' dbname='comparatory' user='{}' password='{}'".format(
        app.config['AWS_RDS_HOST'],
        app.config['AWS_RDS_USER'],
        app.config['AWS_RDS_PASSWORD'])
    conn = psycopg2.connect(conn_str)
    return conn.cursor()


# Connect to local RDS
def _connect_db_local():
    conn_string = "host='localhost' dbname='ind'"
    conn = psycopg2.connect(conn_string)
    return conn.cursor()


# Connnect to AWS elasticsearch
def _connect_es():
    host = os.environ['ES_HOST']
    awsauth = AWS4Auth(
        app.config['AWS_ES_ACCESS_KEY'],
        app.config['AWS_ES_SECRET_KEY'],
        'us-east-1',
        'es')
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
