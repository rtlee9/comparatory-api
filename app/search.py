import pandas as pd
import json
from os import path
from flask import request
from flask_restful import Resource

from app import api
from connect import get_db, get_es
from utils import decomp_case, comp_case, clean_desc, get_desc
from config import path_models


class CompaniesPeers(Resource):
    def get(self):
        top_sims, match, target, results, sim_ids = get_sim_results()
        match.pop('business_desc')
        for v in results.values():
            v.pop('business_desc')
        return {
            'match': dict(id=target, **match),
            'results': [
                dict(rank=k, id=sim_ids[k - 1], **v)
                for k, v in results.items()
            ],
        }


class CompaniesPeersDesc(Resource):
    def get(self):
        response = CompaniesPeers().get()
        match = response['match']
        match['business_desc'] = get_desc(match['id'])
        for v in response['results']:
            v['business_desc'] = get_desc(v['id'])
        return response


def get_top_sims():
    es = get_es()
    cursor = get_db()
    cname = request.args['company-name']
    es_query = {"query": {"match": {
        "NAME": cname}},
        "_source": "NAME", "size": 1}
    resp = es.search(
        'comparatory', 'company', es_query)['hits']['hits']
    assert len(resp) == 1, resp
    name_match = [d['_source']['NAME'].upper() for d in resp][0]

    # Find next most similar
    query = """
    select
        d.id as primary_id
        ,d.name as primary_name
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
        ,s.name as next_name
        ,s.sic_cd as next_sic_cd
        ,s.zip as next_zip
        ,s.city as next_city
        ,s.state as next_state
        ,s.state_of_incorporation as next_state_inc
        ,s.irs_number as next_irs_number
        ,s.filed_as_of_date as next_filed_dt
        ,s.business_description as next_bus_desc
        ,d.raw_description as primary_raw_desc
        ,s.raw_description as next_raw_desc
    from company_dets d
    inner join sims n
        on d.id = n.id
    inner join company_dets s
        on n.sim_id = s.id
    where d.NAME =
        \'""" + decomp_case(name_match) + """\'
    """

    cursor.execute(query)
    return(cursor.fetchall())


def parse_matches(top_sims):
    """Parse target company details based on SQL query
    """
    match = {}
    match['name'] = comp_case(str(top_sims[0][1]))
    match['sic_cd'] = str(top_sims[0][2])
    match['business_desc'] = clean_desc(top_sims[0][22])
    return match


def parse_sims(top_sims, num_sims=5):
    """Parse list of most similar companies based on SQL query
    """

    results = {}
    sim_ids = []

    for i in range(num_sims):
        next_b = top_sims[i]
        results[i + 1] = {
            'name': comp_case(str(next_b[13])),
            'sic_cd': str(next_b[14]),
            'sim_score': str('{0:2.0f}%'.format(next_b[10] * 100)),
            'business_desc': clean_desc(next_b[23])
        }
        sim_ids.append(next_b[12])
    return results, sim_ids


def get_sim_results():
    top_sims = get_top_sims()
    match = parse_matches(top_sims)
    target = top_sims[0][0]
    results, sim_ids = parse_sims(top_sims)
    return top_sims, match, target, results, sim_ids


api.add_resource(CompaniesPeers, '/companies/peers')
api.add_resource(CompaniesPeersDesc, '/companies/peers/desc')
similarity_scores = pd.read_pickle(
    path.join(path_models, 'similarity_scores_df.pk'))
with open(path.join(path_models, 'company_profiles.json'), 'r') as f:
    company_profiles = json.load(f)
