from os import path
from flask import request
import numpy as np
import json
from sklearn.externals import joblib
from sklearn.metrics.pairwise import cosine_similarity
from flask_restful import Resource
import boto
import zipfile

from app import api
from utils import load_sparse_csr, get_desc, comp_case, clean_name
import config


# load TF-IDF model
def load_tfidf():
    path_models = config.path_models
    tfidf_vecs = load_sparse_csr(path.join(path_models, 'tfidf_weights.npz'))
    vectorizer = joblib.load(path.join(path_models, 'tfidf_vectorizer.pkl'))
    with open(path.join(path_models, 'tfidf_dets.json'), 'r') as f:
        tfidf_dets = json.loads(json.load(f))
    with open(path.join(path_models, 'tfidf_ordered_keys.txt'), 'r') as f:
        tfidf_keys = [l.rstrip() for l in f.readlines()]
    return tfidf_vecs, vectorizer, tfidf_dets, tfidf_keys


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

try:
    tfidf_vecs, vectorizer, tfidf_dets, tfidf_keys = load_tfidf()
except:
    zip_path = path.join(config.path_base, 'models.zip')
    download_modelzip(zip_path)
    unzip_model(zip_path)
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
                name=comp_case(clean_name(dets['COMPANY CONFORMED NAME'])),
                sic_cd=str(dets['SIC_CD']),
                sim_score='{:.0f}%'.format(cs[i] * 100),
                ))
        return top_sims


class DescribeDesc(Resource):
    def get(self):
        top_sims = Describe().get()
        for v in top_sims:
            v['business_desc'] = get_desc(v['id'])
        return top_sims

api.add_resource(Describe, '/companies/describe')
api.add_resource(DescribeDesc, '/companies/describe/desc')
