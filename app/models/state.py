from sqlalchemy import Column, Integer, String
from app.db import db


class State(db.Model):
    __tablename__ = "states"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True)

    def __init__(self, name=None):
        self.name = name

    @classmethod
    def get_id(cls, name):
        state = State.query.filter_by(name=name).first()
        return state.id
