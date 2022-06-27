from flask import redirect, render_template, request, url_for, session, flash, Flask
from app.models.appointment import Appointment
from app.models.user import User
from app.models.role import Role
from app.models.vaccine import Vaccine
from app.models.location import Location
from app.helpers.validations import validate
from app.helpers.decorators import login_required, has_permission
import json
import random
import sys


app = Flask(__name__)

def index_all():
    locations = Location.query.all()

    return render_template("location/list.html", location_list=locations)

def nurses_from_location(location_id):
    nurses = User.nurse_from(location_id)
    return nurses

def appointments_from_location(location_id):
    appointments = Appointment.appointments_from_location(location_id)
    return appointments

def change_address(location_id):
    address = request.form["address"]
    Location.set_address(location_id, address)

    nurses = User.nurse_from(location_id)
    for nurse in nurses:
        message_nurse = ('Subject: Cambio de direccion de sede asignada\n\n Hola Enfermero/a ' +
               (nurse.first_name).capitalize() + ' ' + (nurse.last_name).capitalize() + '. ' +
               'Enviamos este correo para avisar que la sede que tiene asignada ' + User.get_location(nurse.id) + ' cambio de direccion.\n\n' +
               'La nueva direccion es: ' + address +
               '\n\nGracias,\nVacunassist' + '\n\n****' +
               '\nSi no tiene una cuenta en nuestro sitio, por favor ignore este e-mail.').encode('utf-8')
        User.send_plaintext_email(nurse.email, message_nurse)
    
    users = User.user_from(location_id)
    for user in users:
        message_user = ('Subject: Cambio de direccion de sede asignada\n\n Hola ' +
               (user.first_name).capitalize() + ' ' + (user.last_name).capitalize() + '. ' +
               'Enviamos este correo para avisar que la sede que tiene como preferencia ' + User.get_location(user.id) + ' cambio de direccion.\n\n' +
               'La nueva direccion es: ' + address +
               '\n\nGracias,\nVacunassist' + '\n\n****' +
               '\nSi no tiene una cuenta en nuestro sitio, por favor ignore este e-mail.').encode('utf-8')
        User.send_plaintext_email(user.email, message_user)

    return redirect(url_for("location_list"))