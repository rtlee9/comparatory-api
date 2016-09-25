# coding: utf-8
from pymongo import MongoClient
from elasticsearch import Elasticsearch, RequestsHttpConnection
import os
from requests_aws4auth import AWS4Auth

# Load login info from config
AWS_RDS_HOST = os.environ['AWS_RDS_HOST']
AWS_RDS_USER = os.environ['AWS_RDS_USER']
AWS_RDS_PASSWORD = os.environ['AWS_RDS_PASSWORD']
AWS_ES_ACCESS_KEY = os.environ['***REMOVED***']
AWS_ES_SECRET_KEY = os.environ['AWS_SECRET_ACCESS_KEY']


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

es_aws = _connect_es()
es_local = Elasticsearch('localhost')

assert 'comparatory' in es_aws.indices.get_aliases().keys()
assert es_aws.indices.get_field_mapping(
    'dets.COMPANY CONFORMED NAME', 'comparatory', 'company') is not None
assert es_aws.count('comparatory') > 5000

# Connect to MongoDB document store
client = MongoClient()
db = client.industry
ten_k = db.dataset

# Get all
docs = list(ten_k.find())
assert len(docs) > 5000

# Doc-by-doc upload to AWS elasticseach node
# AWS has batch limit of 10MB

for d in docs:
    _id = d.pop('_id')
    es_local.index(index='comparatory', doc_type='company', body=d, id=_id)
    es_aws.index(index='comparatory', doc_type='company', body=d, id=_id)
