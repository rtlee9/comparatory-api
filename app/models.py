from app import db
import datetime


class Sim_search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String())
    search_string = db.Column(db.String())
    datetime = db.Column(
        db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, user_id, search_string):
        self.user_id = user_id
        self.search_string = search_string

    def __repr__(self):
        return '<{}: {}>'.format(self.user_id, self.search_string)
