import datetime
from app.db import db
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.sql.schema import ForeignKey
import datetime 

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
    def search_vaccine(cls, name, user_id):
        resul = Vaccine.query.filter_by(name=name,user_id = user_id).first()
        return resul

    @classmethod
    def get_vaccines(cls, user_id):
        list = Vaccine.query.filter_by(user_id=user_id).all()
        return list

    @classmethod
    def get_applicatedvaccines(cls, user_id):
        today = datetime.date.today()
        list_vac = cls.get_vaccines(user_id)
        applicated = list(filter(lambda v: v.application_date<today, list_vac))
        return applicated

    @classmethod
    def get_vaccines_names(cls, user_id):
        list_vac = Vaccine.query.filter_by(user_id=user_id).all()
        list_names = list(map(lambda v: v.name, list_vac))
        return list_names
    
    @classmethod
    def have_vaccine(cls, user_id, vaccine_name):
        list_vac = cls.get_vaccines_names(user_id)
        resul = False
        if vaccine_name in list_vac:
            resul = True
        return resul
    
    @classmethod
    def have_gripe_thisyear(cls, user_id):
        consulta = False
        today = datetime.date.today()
        vac = cls.search_vaccine("Gripe",user_id)
        if (vac != None):
            if (vac.application_date.year==today.year):
                consulta = True
        return consulta
    
    @classmethod
    def covid2_avalaible(cls, user_id):
        consulta = True
        today = datetime.date.today()
        vac = cls.search_vaccine("Covid 19 Primera Dosis",user_id)
        if (vac != None):
            diff = today - vac.application_date
            if(diff.days < 21):
                consulta = False
        return consulta
