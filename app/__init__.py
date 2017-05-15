from flask import Flask
from config import set_config
from flask_restful import Api


app = Flask(__name__)
db = set_config(app)

api = Api(app)

from app import search, visualizations, describe
db.create_all()
db.session.commit()
