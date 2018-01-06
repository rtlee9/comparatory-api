from flask import request
from flask_restful import Resource

from app import api
from connect import get_es


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
