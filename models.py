from app import db


class Company(db.Model):
    __tablename__ = 'company_dets'
    __searchable__ = ['company_conformed_name']

    id = db.Column(db.Integer, primary_key=True)
    sic_cd = db.Column(db.String(4))
    company_conformed_name = db.Column(db.String())
    business_description = db.Column(db.String())

    def __init__(self, id, sic_cd, company_conformed_name,
                 business_description):
        self.id = id
        self.sic_cd = sic_cd
        self.company_conformed_name = company_conformed_name
        self.business_description = business_description

    def __repr__(self):
        return '<id {}: {}>'.format(self.id, self.company_conformed_name)


class Sim(db.Model):
    __tablename__ = 'sims'

    id = db.Column(db.String(), primary_key=True)
    sim_id = db.Column(db.String(), db.ForeignKey('sim.id'))
    sim_score = db.Column(db.Integer())

    def __init__(self, id, sim_id, sim_score):
        self.id = id
        self.sim_id = sim_id
        self.sim_score = sim_score

    def __repr__(self):
        return '<id {}: sim_id {}>'.format(self.id, self.sim_id)
