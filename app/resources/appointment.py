from flask import redirect, render_template, request, url_for, session, flash, Flask
from app.models.user import User
from app.models.role import Role
from app.helpers.validations import validate
from app.helpers.decorators import login_required, has_permission
import json
import random
import sys

app = Flask(__name__)

def new():
    return render_template("appointment/new.html")

def index():
    return render_template("appointment/list.html")

def create():
    message = []
    condition = validate(request.form["email"], "Correo", required=True, email=True)
    valid_mail = condition
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["password"], "Clave", required=True, min_length="6"
    )
    if condition is not True:
        message.append(condition)

    condition = validate(request.form["first_name"], "Nombre", required=True, text=True)
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["last_name"], "Apellido", required=True, text=True
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["dni"], "DNI", required=True, min_length=8
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["telephone"], "Telefono", required=True
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["date_of_birth"], "Fecha de Nacimiento", required=True
    )
    if condition is not True:
        message.append(condition)
    
    if valid_mail is True and not User.valid_email(request.form["email"]):
        message.append(
            "Ya existe un usuario con ese email, por favor\
            ingrese uno nuevo"
        )

    if message:
        for mssg in message:
            flash(mssg)
        return render_template("user/new.html")

    print("////////////////////////////////////")
    print(request.form)
    print("////////////////////////////////////")
    '''print(request.form["covid1"])
    print(request.form["covid1_date"])
    print(request.form["covid2"])
    print(request.form["covid2_date"])
    print(request.form["gripe"])
    print(request.form["gripe_date"])
    print(request.form["fiebre"])
    print(request.form["fiebre_date"])
    print("////////////////////////////////////")'''

    User.create_pacient(**request.form)
    #user = User.search_user_by_email(request.form["email"])
    return redirect(url_for("auth_login"))
