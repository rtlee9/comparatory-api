# coding: utf-8
from pymongo import MongoClient
from elasticsearch import Elasticsearch
import copy

es_aws = Elasticsearch(
    '***REMOVED***', verify_certs=True)

es_aws.indices.get_aliases().keys()
es_aws.indices.get_field_mapping('dets.COMPANY CONFORMED NAME', 'comparatory', 'company')
es_aws.count('comparatory')

# Connect to MongoDB document store
client = MongoClient()
db = client.industry
ten_k = db.dataset

# Get all
docs_orig = list(ten_k.find())

# Doc-by-doc upload to AWS elasticseach node
# AWS has batch limit of 10MB
docs = copy.deepcopy(docs_orig)
print len(docs)

for d in docs:
    _id = d.pop('_id')
    es_local.index(index='comparatory', doc_type='company', body=d, id=_id)
    es_aws.index(index='comparatory', doc_type='company', body=d, id=_id)
