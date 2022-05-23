from app.db import db
from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.sql.schema import ForeignKey
from app.models.role import Role
from app.models.permission import Permission
from app.models.state import State
from app.models.vaccine import Vaccine
from app.models.appointment import Appointment
from sqlalchemy.orm import relationship
import hashlib
import random
import datetime
import smtplib, ssl



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
    list_vaccines = db.relationship("Vaccine")
    list_appointments = db.relationship("Appointment")
    token = Column(Integer)

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
        role_id=None,
        token=None
    ):
        self.email = email
        self.password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        self.active = active
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth=date_of_birth,
        self.dni=dni,
        self.telephone=telephone,
        self.role_id=role_id,
        self.token=token

    @classmethod
    def create_pacient(cls, **kwargs):
        token = random.randrange(1,500)
        user = User(active=False, 
            role_id=2, 
            token=token,
            email=kwargs["email"],
            password=kwargs["password"],
            first_name=kwargs["first_name"],
            last_name=kwargs["last_name"],
            date_of_birth=kwargs["date_of_birth"],
            dni=kwargs["dni"],
            telephone=kwargs["telephone"])
        #Mandar email con el token
        db.session.add(user)
        db.session.commit()

    @classmethod
    def activate_account(cls, user_id):
        user = User.query.filter_by(id=user_id).first()
        user.active = True
        db.session.commit()

    @classmethod
    def is_active(cls, user_id):
        user = User.query.filter_by(id=user_id).first()
        return user.active

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
    def search_user_by_email(cls, user_email):
        usuario = User.query.filter_by(email=user_email).first()
        return usuario

    @classmethod
    def get_token(cls, user_id):
        user = User.query.filter_by(id=user_id).first()
        return user.token
    
    @classmethod
    def get_role(cls, user_id):
        user = cls.search_user_by_id(user_id)
        return user.role_id

    @classmethod
    def get_age(cls, user_id):
        user = cls.search_user_by_id(user_id)
        date = user.date_of_birth
        today = datetime.date.today()
        one_or_zero = int ((today.month, today.day) < (date.month, date.day))
        difference = today.year - date.year
        age = difference - one_or_zero
        return age

    @classmethod
    def add_vaccines(cls, dict, user):
        #user = cls.search_user_by_email(dict["email"])
        if (dict["covid1"]=="Si"):
            Vaccine.create("Covid 19 Primera Dosis", dict["covid1_date"], user.id)
        if (dict["covid2"]=="Si"):
            Vaccine.create("Covid 19 Segunda Dosis", dict["covid2_date"], user.id)
        if (dict["gripe"]=="Si"):
            Vaccine.create("Gripe", dict["gripe_date"], user.id)
        if (dict["fiebre"]=="Si"):
            Vaccine.create("Fiebre Amarilla", dict["fiebre_date"], user.id)

    @classmethod
    def add_automatic_appointments(cls, user):
        #user = cls.search_user_by_email(dict["email"])
        vaccines = Vaccine.get_vaccines_names(user.id)
        dict = {
            "date": cls.twoweeks_fromnow()
        }
        if (cls.is_elder(user.id)):
            if ("Gripe" in vaccines):
                pass
            else:
                print("Turno automatico para gripe")
                Appointment.create("Gripe", user_id=(user.id), **dict) 
        if ("Covid 19 Primera Dosis" in vaccines):
            if ("Covid 19 Segunda Dosis" in vaccines):
                pass
            else:
                print("Turno Automatico para segunda dosis de covid19")
                Appointment.create("Covid 19 Segunda Dosis", user_id=(user.id), **dict) 
        else:
            print("Turno Automatico para primera dosis de covid19")
            Appointment.create("Covid 19 Primera Dosis", user_id=(user.id), **dict) 
        
    @classmethod
    def twoweeks_fromnow(cls):
        today = datetime.date.today()
        after_15days = today + datetime.timedelta(days = 15)
        print(after_15days)
        return after_15days

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

    @classmethod
    def update(cls, user_id, kwargs):
        user = User.query.filter_by(id=user_id).first_or_404()
        form = kwargs
        user.first_name = form.get("first_name", user.first_name)
        user.last_name = form.get("last_name", user.last_name)
        user.telephone = form.get("telephone", user.telephone)
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

    @classmethod
    def is_elder(cls, user_id):
        age = cls.get_age(user_id)
        consulta = False
        if (age >= 60):
            consulta = True
        return consulta

    @classmethod
    def send_plaintext_email(cls, receiver_email, message, email_type):
        sender_email = "infinityloop_33@hotmail.com"
        password = "Grupo33ing2"
        if (email_type=="hotmail"):
            conn = smtplib.SMTP('smtp-mail.outlook.com',587)
        if (email_type=="gmail"):
            conn = smtplib.SMTP('smtp.gmail.com',587)
        type(conn)  
        conn.ehlo()  
        conn.starttls()  
        conn.login(sender_email,password)  
        conn.sendmail(sender_email,receiver_email,message)  
        conn.quit()
