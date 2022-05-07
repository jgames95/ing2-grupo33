from app.db import db
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.sql.schema import ForeignKey

class Vaccine(db.Model):
    __tablename__ = "vaccines"
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    application_date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))

    def __init__(self, name=None, application_date=None):
        self.name = name
        self.application_date = application_date

    @classmethod
    def get_id(cls, name):
        state = Vaccine.query.filter_by(name=name).first()
        return state.id

    @classmethod
    def create(cls, **kwargs):
        vaccine = Vaccine(**kwargs)
        db.session.add(vaccine)
        db.session.commit()