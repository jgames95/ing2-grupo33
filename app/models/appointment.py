from datetime import date
from sqlalchemy import Column, Integer, Date
from app.db import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from app.models.vaccine import Vaccine
from app.models.state import State

class Appointment(db.Model):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    vaccine_id = Column(Integer, ForeignKey("vaccines.id"))
    vaccine = relationship(Vaccine)
    state_id = Column(Integer, ForeignKey("states.id"))
    state = relationship(State)
    creation_date = Column(Date)
    closed_date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))

    def __init__(self, user_id=None, vaccine_id=None, creation_date=None):
        self.user_id = user_id
        self.vaccine_id = vaccine_id
        self.state_id = 1
        self.creation_date = creation_date

    @classmethod
    def create(cls, vac, user_id, **kwargs):
        appointment = Appointment(vaccine_id = vac.id,  
            creation_date = kwargs["date"],
            user_id = user_id)
        if (kwargs["vaccine"] != "Fiebre Amarilla"):
            appointment.state_id = 2
        db.session.add(appointment)
        db.session.commit()

    @classmethod
    def change_status(cls, appointment_id, state_id):
        appointment = Appointment.query.filter_by(id=appointment_id).first()
        appointment.state_id = state_id
        if (state_id == 5):
            appointment.closed_date = date.today()
        db.session.commit()

    def approve_appointment(cls, appointment_id):
        cls.change_status(appointment_id, 2)

    def reject_appointment(cls, appointment_id):
        cls.change_status(appointment_id, 3)

    def cancel_appointment(cls, appointment_id):
        cls.change_status(appointment_id, 4)
    
    def close_appointment(cls, appointment_id):
        cls.change_status(appointment_id, 5)

    



