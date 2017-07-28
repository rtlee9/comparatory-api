from flask import Flask
from config import set_config
from flask_restful import Api
from flat import extract_flat

extract_flat()
app = Flask(__name__)
set_config(app)

api = Api(app)

from app import search, visualizations, describe
