from os import path
from flask import request
import numpy as np
import json
from sklearn.externals import joblib
from sklearn.metrics.pairwise import cosine_similarity
from flask_restful import Resource
from urllib import urlretrieve
import zipfile
from utils import clean_desc

from connect import get_db
from app import api
from utils import load_sparse_csr
from config import path_models, path_app, path_modelzip


# load TF-IDF model
def load_tfidf():
    tfidf_vecs = load_sparse_csr(path.join(path_models, 'tfidf_weights.npz'))
    vectorizer = joblib.load(path.join(path_models, 'tfidf_vectorizer.pkl'))
    with open(path.join(path_models, 'tfidf_dets.json'), 'r') as f:
        tfidf_dets = json.loads(json.load(f))
    with open(path.join(path_models, 'tfidf_ordered_keys.txt'), 'r') as f:
        tfidf_keys = [l.rstrip() for l in f.readlines()]
    return tfidf_vecs, vectorizer, tfidf_dets, tfidf_keys

try:
    tfidf_vecs, vectorizer, tfidf_dets, tfidf_keys = load_tfidf()
except:
    zip_path = path.join(path_app, 'models.zip')
    urlretrieve(path_modelzip, zip_path)
    zip_ref = zipfile.ZipFile(zip_path, 'r')
    zip_ref.extractall(path_app)
    zip_ref.close()
    tfidf_vecs, vectorizer, tfidf_dets, tfidf_keys = load_tfidf()


class Describe(Resource):
    def get(self):
        desc = request.args['company-description']
        target_vec = vectorizer.transform([desc])
        cs = cosine_similarity(target_vec, tfidf_vecs)[0]
        if cs.sum() < .0001:
            return {}
        top_n = 5
        ind = np.argpartition(cs, -top_n)[-top_n:]
        ind = ind[np.argsort(-cs[ind])]
        top_sims = []
        for rank, i in enumerate(ind):
            key = tfidf_keys[i]
            dets = tfidf_dets[key]
            top_sims.append(dict(
                id=key,
                rank=rank + 1,
                name=comp_case(dets['COMPANY CONFORMED NAME']),
                sic_cd=dets['SIC_CD'],
                sim_score='{:.0f}%'.format(cs[i] * 100),
                ))
        return top_sims


class DescribeDesc(Resource):
    def get(self):
        top_sims = Describe().get()
        for v in top_sims:
            v['business_desc'] = get_desc(v['id'])
        return top_sims


def get_desc(id):
    cursor = get_db()
    cursor.execute("""
    select business_description
    from company_dets
    where id = '{}'
    """.format(id))
    try:
        return clean_desc(cursor.fetchone()[0])
    except TypeError as e:
        print('No description found for {}'.format(id))
        return ''

api.add_resource(Describe, '/describe')
api.add_resource(DescribeDesc, '/describe/desc')
