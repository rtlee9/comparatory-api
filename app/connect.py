import os
from elasticsearch import Elasticsearch
from flask import g


# Connnect to elasticsearch
def _connect_es():
    host = os.environ['ES_HOST']
    es = Elasticsearch(host)
    return es


# Opens a new elasticsearch connection if there is none yet for the
# current application context
def get_es():
    if not hasattr(g, 'es_node'):
        g.es_node = _connect_es()
    return g.es_node
