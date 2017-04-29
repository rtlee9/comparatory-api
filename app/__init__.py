from flask import Flask
from config import set_config
from flask_restful import Api


app = Flask(__name__)
db = set_config(app)

api = Api(app)

from app import models, search, visualizations
db.create_all()
db.session.commit()
