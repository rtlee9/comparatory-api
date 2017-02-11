from flask import Flask
from config import set_config


app = Flask(__name__)
db = set_config(app)
from app import views, models
db.create_all()
db.session.commit()
