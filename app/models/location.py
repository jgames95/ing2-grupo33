from sqlalchemy import Column, Integer, String
from app.db import db


class Location(db.Model):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True)
    address = Column(String(100), unique=True)

    def __init__(self, name=None, address=None):
        self.name = name
        self.address = address

    @classmethod
    def get_name(cls, id):
        loc = Location.query.filter_by(id=id).first()
        return loc.name
    
    @classmethod
    def get_id(cls, loc_name):
        loc = Location.query.filter_by(name=loc_name).first()
        return loc.id