from datetime import date
from sqlalchemy import Column, Integer, DateTime
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
    creation_date = Column(DateTime)
    closed_date = Column(DateTime)

    def __init__(self, name=None, vaccine_id=None):
        self.name = name
        self.vaccine_id = vaccine_id
        self.state_id = 1
        self.creation_date = date.today()

    @classmethod
    def create(cls, **kwargs):
        appointment = Appointment(**kwargs)
        if (appointment.vaccine_id != 1):
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

    



