from app.db import db
from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.sql.schema import ForeignKey
from app.models.role import Role
from app.models.permission import Permission
from app.models.appointment import Appointment
from app.models.vaccine import Vaccine
from sqlalchemy.orm import relationship
import hashlib
#import random


class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(30), unique=True)
    password = Column(String(254))
    active = Column(Boolean)
    first_name = Column(String(30))
    last_name = Column(String(30))
    dni = Column(String(30))
    telephone = Column(String(30))
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship(Role)
    #Only Pacients
    date_of_birth = Column(Date)
    list_vaccines = db.relationship(
        "Vaccines", secondary="user_vaccines", lazy="dynamic"
    )
    list_appointments = db.relationship(
        "Appointments", secondary="user_appointments", lazy="dynamic"
    )

    def __init__(
        self,
        email=None,
        password=None,
        active=None,
        first_name=None,
        last_name=None,
        date_of_birth=None,
        dni=None,
        telephone=None,
        list_vaccines=None,
        list_appointments=None,
        role_id=None
    ):
        self.email = email
        self.password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        self.active = active
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth=date_of_birth,
        self.dni=dni,
        self.telephone=telephone,
        self.list_vaccines=list_vaccines,
        self.role_id=role_id
        self.list_appointments=list_appointments

    @classmethod
    def create_pacient(cls, **kwargs):
        user = User(active=False, role_id=2, **kwargs)
        '''rol = Role.query.filter_by(id=2).first()
        user.role = rol'''
        db.session.add(user)
        db.session.commit()

    @classmethod
    def confirm_account(cls, user_id):
        user = User.query.filter_by(id=user_id).first()
        user.active = True
        db.session.commit()

    @classmethod
    def create_nurse(cls, **kwargs):
        user = User(active=True, **kwargs)
        rol = Role.query.filter_by(id=3).first()
        user.role = rol
        db.session.add(user)
        db.session.commit()

    @classmethod
    def search_user_by_id(cls, user_id):
        usuario = User.query.filter_by(id=user_id).first()
        return usuario
    
    @classmethod
    def get_role(cls, user_id):
        user = cls.search_user_by_id(user_id)
        return user.role

    '''@classmethod
    def create_pending_user(cls, email, name, id):
        if not cls.valid_email(email):
            return False
        auxname = name.strip(" ")
        while not cls.valid_username(auxname):
            auxname = auxname + str(random.randint(0, 9))
        user = User(
            email=email, active=True, username=auxname, first_name=name, password=id
        )
        db.session.add(user)
        db.session.commit()

        return user'''

    @classmethod
    def has_permission(cls, user_id, permission):
        consulta = (
            db.session.query(User, Role, Permission)
            .join(User.role)
            .join(Role.permissions)
            .where(Permission.name == permission)
            .where(User.id == user_id)
            .where(User.active == 1)
            .first()
        )
        return consulta is not None


    '''def __repr__(self):
        return "<User %r>" % self.username'''

    @classmethod
    def valid_email(cls, email):
        exist = User.query.filter_by(email=email).scalar()
        return exist is None

    '''@classmethod
    def valid_email_modify(cls, email, user_id):

        exist = User.query.filter_by(email=email).first()
        if not (exist is None) and (int(exist.id) == int(user_id)):
            return True
        return exist is None'''

    @classmethod
    def update(cls, user_id, kwargs):
        user = User.query.filter_by(id=user_id).first_or_404()
        form = kwargs
        user.first_name = form.get("first_name", user.first_name)
        user.last_name = form.get("last_name", user.last_name)
        db.session.commit()

    '''@classmethod
    def filter(cls, page, form):

        users = User.query.order_by(User.first_name.asc()).paginate(
                page, 5, False
            )

        if form["search_username"] != "":
            if form["active"] == "Activo":
                users = (
                        User.query.filter(
                            (
                                User.username.contains(form["search_username"])
                                & (User.active is True)
                            )
                        )
                        .order_by(User.first_name.asc())
                        .paginate(page, 5, False)
                    )

            elif form["active"] == "Bloqueado":
                users = (
                        User.query.filter(
                            (
                                User.username.contains(form["search_username"])
                                & (User.active is False)
                            )
                        )
                        .order_by(User.first_name.asc())
                        .paginate(page, 5, False)
                    )
            
            else:
                users = (
                        User.query.filter(
                            User.username.contains(form["search_username"])
                        )
                        .order_by(User.first_name.asc())
                        .paginate(page, 5, False)
                    )
                
        elif form["active"] == "Activo":
            users = (
                    User.query.filter(User.active is True)
                    .order_by(User.first_name.asc())
                    .paginate(page, 5, False)
                )
            
        elif form["active"] == "Bloqueado":
            users = (
                    User.query.filter(User.active is False)
                    .order_by(User.first_name.asc())
                    .paginate(page, 5, False)
                )

        return users'''

class UserVaccines(db.Model):
    __tablename__ = "user_vaccines"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    vaccine_id = db.Column(
        db.Integer(), db.ForeignKey("vaccines.id", ondelete="CASCADE")
    )
    applicated_date = Column(Date)

    def __init__(cls, user_id=None, vaccine_id=None, applicated_date=None):
        cls.user_id = user_id
        cls.vaccine_id = vaccine_id
        cls.applicated_date = applicated_date

class UserAppointments(db.Model):
    __tablename__ = "user_appointments"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    appointment_id = db.Column(
        db.Integer(), db.ForeignKey("appointments.id", ondelete="CASCADE")
    )
