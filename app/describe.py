from os import path
from flask import request
import numpy as np
import json
from sklearn.externals import joblib
from sklearn.metrics.pairwise import cosine_similarity
from flask_restful import Resource
from urllib import urlretrieve
import zipfile

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
        top_sims = {}
        for rank, i in enumerate(ind):
            key = tfidf_keys[i]
            dets = tfidf_dets[key]
            top_sims[key] = dict(
                rank=rank + 1,
                name=dets['COMPANY CONFORMED NAME'],
                sic_cd=dets['SIC_CD'],
                sim_score=cs[i],
                )
        return top_sims

api.add_resource(Describe, '/describe')
