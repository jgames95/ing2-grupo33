from app.db import db
from sqlalchemy import Column, Integer, String

class Vaccine(db.Model):
    __tablename__ = "vaccines"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True)

    def __init__(self, name=None, applicated_date=None):
        self.name = name
        self.applicated_date = applicated_date

    @classmethod
    def get_id(cls, name):
        state = Vaccine.query.filter_by(name=name).first()
        return state.id

    @classmethod
    def create(cls, **kwargs):
        vaccine = Vaccine(**kwargs)
        db.session.add(vaccine)
        db.session.commit()