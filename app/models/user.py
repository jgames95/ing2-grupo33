from app.db import db
from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.sql.schema import ForeignKey
from app.models.role import Role
from app.models.state import State
from app.models.vaccine import Vaccine
from app.models.appointment import Appointment
from app.models.location import Location
from sqlalchemy.orm import relationship
import hashlib
import random
import datetime
import smtplib

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
    location_id = Column(Integer, ForeignKey("locations.id"))
    location = relationship(Location)
    # Only Pacients
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
        token=None,
        location_id=None
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
        self.token=token,
        self.location_id=location_id

    @classmethod
    def create_pacient(cls, **kwargs):
        token = random.randrange(1,500)
        user = User(active=False, role_id=2, token=token,
            email=kwargs["email"],
            password=kwargs["password"],
            first_name=kwargs["first_name"],
            last_name=kwargs["last_name"],
            date_of_birth=kwargs["date_of_birth"],
            dni=kwargs["dni"],
            telephone=kwargs["telephone"],
            location_id=int(kwargs["location"]))
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
        user = User(active=True, role_id=3, 
            email=kwargs["email"],
            password=kwargs["password"],
            first_name=kwargs["first_name"],
            last_name=kwargs["last_name"],
            date_of_birth=kwargs["date_of_birth"],
            dni=kwargs["dni"],
            telephone=kwargs["telephone"],
            location_id=1)
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
    def get_location(cls, user_id):
        user = cls.search_user_by_id(user_id)
        name = Location.get_name(user.location_id)
        return name
    
    @classmethod
    def user_from(cls, location_id):
        lista = User.query.filter_by(role_id=2, location_id=location_id).all()
        return lista

    @classmethod
    def get_token(cls, user_id):
        user = User.query.filter_by(id=user_id).first()
        return user.token

    @classmethod
    def get_role(cls, user_id):
        user = cls.search_user_by_id(user_id)
        return user.role_id

    @classmethod
    def has_role(cls, role_id, user_id):
        return cls.get_role(user_id) == role_id

    @classmethod
    def get_age(cls, user_id):
        user = cls.search_user_by_id(user_id)
        date = user.date_of_birth
        today = datetime.date.today()
        one_or_zero = int((today.month, today.day) < (date.month, date.day))
        difference = today.year - date.year
        age = difference - one_or_zero
        return age

    @classmethod
    def add_vaccines(cls, dict, user):
        #user = cls.search_user_by_email(dict["email"])
        if (dict["covid1"] == "Si"):
            Vaccine.create("Covid 19 Primera Dosis",
                           dict["covid1_date"], user.id)
        if (dict["covid2"] == "Si"):
            Vaccine.create("Covid 19 Segunda Dosis",
                           dict["covid2_date"], user.id)
        if (dict["gripe"] == "Si"):
            Vaccine.create("Gripe", dict["gripe_date"], user.id)
        if (dict["fiebre"] == "Si"):
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
                Appointment.create("Gripe", user_id=(
                    user.id), first_name=user.first_name, last_name=user.last_name, location_id=(user.location_id), **dict)
        if ("Covid 19 Primera Dosis" in vaccines):
            if ("Covid 19 Segunda Dosis" in vaccines):
                pass
            else:
                print("Turno Automatico para segunda dosis de covid19")
                Appointment.create("Covid 19 Segunda Dosis",
                                   user_id=(user.id), first_name=user.first_name, last_name=user.last_name, location_id=(user.location_id), **dict)
        else:
            print("Turno Automatico para primera dosis de covid19")
            Appointment.create("Covid 19 Primera Dosis",
                               user_id=(user.id), first_name=user.first_name, last_name=user.last_name, location_id=(user.location_id), **dict)

    @classmethod
    def twoweeks_fromnow(cls):
        today = datetime.date.today()
        after_15days = today + datetime.timedelta(days=15)
        print(after_15days)
        return after_15days

    @classmethod
    def valid_email(cls, email):
        exist = User.query.filter_by(email=email).scalar()
        return exist is None

    @classmethod
    def valid_pacient_dni(cls, dni):
        users = User.query.filter_by(dni=dni).all()
        ok = True
        if users is not None:
            if isinstance(users, list):
                for user in users:
                    if (user.role_id != 2):
                        ok = True
                    elif (user.role_id == 2):
                        ok = False
                        break
                return ok
            elif isinstance(users, User):
                if (user.role_id != 2):
                        ok = True
                elif (user.role_id == 2):
                    ok = False
                return ok
        else:
            return True

    @classmethod
    def valid_nurse_dni(cls, dni):
        users = User.query.filter_by(dni=dni).all()
        ok = True
        if users is not None:
            if isinstance(users, list):
                for user in users:
                    if (user.role_id != 3):
                        ok = True
                    elif (user.role_id == 3):
                        ok = False
                        break
                return ok
            elif isinstance(users, User):
                if (user.role_id != 3):
                        ok = True
                elif (user.role_id == 3):
                    ok = False
                return ok
        else:
            return True
        
    @classmethod
    def update(cls, user_id, kwargs):
        user = User.query.filter_by(id=user_id).first_or_404()
        form = kwargs
        user.first_name = form.get("first_name", user.first_name)
        user.last_name = form.get("last_name", user.last_name)
        user.telephone = form.get("telephone", user.telephone)
        user.location_id = form.get("location", user.location_id)
        db.session.commit()

    @classmethod
    def update_nurse(cls, user_id, kwargs):
        user = User.query.filter_by(id=user_id).first_or_404()
        form = kwargs
        user.first_name = form.get("first_name", user.first_name)
        user.last_name = form.get("last_name", user.last_name)
        user.telephone = form.get("telephone", user.telephone)
        db.session.commit()

    @classmethod
    def is_elder(cls, user_id):
        age = cls.get_age(user_id)
        consulta = False
        if (age >= 60):
            consulta = True
        return consulta

    @classmethod
    def send_plaintext_email(cls, receiver_email, message):
        conn = smtplib.SMTP('smtp.gmail.com', 587)
        sender_email = "infinityloop33.help@gmail.com"
        password = "vuiosiqvpwburvni"
        type(conn)
        conn.ehlo()
        conn.starttls()
        conn.login(sender_email, password)
        conn.sendmail(sender_email, receiver_email, message)
        conn.quit()

    @classmethod
    def get_fullname(cls, user_id):
        u = cls.search_user_by_id(user_id)
        full_name = (u.first_name).title() + ' ' + (u.last_name).title()
        return full_name

    @classmethod
    def get_email(cls, user_id):
        u = cls.search_user_by_id(user_id)
        return u.email
    
    @classmethod
    def nurse_list(cls):
        lista = User.query.filter_by(role_id=3).all()
        return lista

    @classmethod
    def nurse_from(cls, location_id):
        lista = User.query.filter_by(role_id=3, location_id=location_id).all()
        return lista

    @classmethod
    def nurse_list_filter(cls, sede):
        nurses = User.nurse_list()
        lista = []

        if sede == "Sin Asignar":
            for n in nurses:
                if (n.location_id == 1):
                    lista.append(n)
        elif sede == "Terminal":
            for n in nurses:
                if (n.location_id == 2):
                    lista.append(n)
        elif sede == "Palacio Municipal":
            for n in nurses:
                if (n.location_id == 3):
                    lista.append(n)
        elif sede == "Cementerio":
            for n in nurses:
                if (n.location_id == 4):
                    lista.append(n)
        elif sede == "Todos":
            lista = nurses

        return lista

    @classmethod
    def change_location(cls, location, user_id):
        user = User.query.filter_by(id=user_id).first()
        user.location_id = Location.get_id(location)
        db.session.commit()
    
    @classmethod
    def rango_edad(cls, date_start, date_end, att):
        lista = []
        vaccines = Vaccine.between_dates(date_start, date_end)
        if vaccines:
            for v in vaccines:
                age = User.get_age(v.user_id)
                if ((age>=int(att[0]))and(age<=int(att[1]))):
                    lista.append(v)
            return lista
        else:
            lista.append("null")
            return lista
    
    '''Desde aca es todo comentarios'''
    
    '''def __repr__(self):
        return "<User %r>" % self.username'''

    '''@classmethod
    def get_list_appointments(cls, location_id):
        appointments = (db.session.query(User, Appointment)
            .join(Appointment.user_id)
            .where(User.active == True)
            .where(Appointment.location_id == location_id)
            .where(Appointment.state_id == 2)
            .all())
        return appointments'''
    
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