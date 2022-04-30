from app.db import db


class Permission(db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
