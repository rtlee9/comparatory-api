import json
from os import path
from flask import request
from flask_restful import Resource

from app import api
from config import path_models


class CompaniesPeers(Resource):
    def get(self):
        return top_sims.get(request.args['ticker'])

class CompaniesPeersDesc(Resource):
    def get(self):
        response = CompaniesPeers().get()
        response['match'] = dict(
            response['match'],
            business_desc=company_profiles[response['match']['id']].get('description'))
        response['results'] = [
            dict(
                result,
                business_desc=company_profiles[result['id']].get('description'))
            for result in response['results']]
        return response


api.add_resource(CompaniesPeers, '/companies/peers')
api.add_resource(CompaniesPeersDesc, '/companies/peers/desc')
with open(path.join(path_models, 'company_profiles.json'), 'r') as f:
    company_profiles = json.load(f)
with open(path.join(path_models, 'top_sims.json'), 'r') as f:
    top_sims = json.load(f)
