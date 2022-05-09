from app.db import db
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.sql.schema import ForeignKey

class Vaccine(db.Model):
    __tablename__ = "vaccines"
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    application_date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))

    def __init__(self, name=None, application_date=None, user_id=None):
        self.name = name
        self.application_date = application_date
        self.user_id = user_id

    @classmethod
    def get_id(cls, name):
        state = Vaccine.query.filter_by(name=name).first()
        return state.id

    @classmethod
    def create(cls, name, date, user_id):
        vaccine = Vaccine(name=name,
        application_date=date,
        user_id=user_id)
        db.session.add(vaccine)
        db.session.commit()

    @classmethod
    def get_vaccines(cls, user_id):
        list = Vaccine.query.filter_by(user_id=user_id).all()
        return list

    @classmethod
    def get_vaccines_names(cls, user_id):
        list = Vaccine.query.filter_by(user_id=user_id).all()
        list_names = list(map(lambda v: v.name, list))
        return list_names