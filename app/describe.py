from flask import request
from flask_restful import Resource
import boto
import zipfile

from app import api
from connect import get_es
import config


def search_name_ticker(target, max_results=5):
    es = get_es()
    query = {
        "query": {"match": {"description": target}}
    }
    resp = es.search(
        index='company_profile',
        doc_type='company',
        size=max_results,
        filter_path=[
            'hits.hits._score',
            'hits.hits._id',
            'hits.hits._source'],
        body=query)
    try:
        hits = resp['hits']['hits']
        return hits
    except KeyError:
        pass


def download_modelzip(zip_path):
    conn = boto.connect_s3(
        config.AWS_ACCESS_KEY_ID, config.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(config.modelzip_bucket, validate=False)
    key = bucket.get_key(config.modelzip_filename)
    key.get_contents_to_filename(zip_path)

def unzip_model(zip_path):
    zip_ref = zipfile.ZipFile(zip_path, 'r')
    zip_ref.extractall(config.path_base)
    zip_ref.close()


class Describe(Resource):
    def get(self):
        hits = DescribeDesc().get()
        for hit in hits:
            hit.pop('business_desc')
        return hits


class DescribeDesc(Resource):
    def get(self):
        desc = request.args['description']
        hits = search_name_ticker(desc)
        top_sims = [
            dict(
                id=hit['_id'],
                name=hit['_source']['name'],
                rank=rank + 1,
                business_desc=hit['_source']['description'],
                sim_score=hit['_score']
            )
            for rank, hit in enumerate(hits)]
        return top_sims


api.add_resource(Describe, '/companies/describe')
api.add_resource(DescribeDesc, '/companies/describe/desc')
