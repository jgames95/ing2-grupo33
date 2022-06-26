
from flask import redirect, render_template, request, url_for, session, flash, Flask
from app.models.appointment import Appointment
from app.models.vaccine import Vaccine
from app.helpers.validations import validate
from app.models.user import User

app = Flask(__name__)


def new():
    return render_template("appointment/new.html")


def index():
    return render_template("appointment/list.html", appoint_list=Appointment.appoint_list_filter("Todos", session["user_id"]))

def index_location():
    user = User.search_user_by_id(session["user_id"])

    dict_activity = Appointment.activity_list(
        session["user_id"])

    lista_canceled = dict_activity['canceled']
    lista_closed = dict_activity['closed']

    return render_template("appointment/list_location.html", appoint_list=Appointment.appointments_from_location_today(user.location_id), activity_canceled=lista_canceled, activity_closed=lista_closed)


def create():
    message = []
    condition = validate(request.form["vaccine"], "Vacuna", required=True)

    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["date"], "Fecha", required=True, futuredate=True, appointmentdate=True
    )
    if condition is not True:
        message.append(condition)

    if message:
        for mssg in message:
            flash(mssg, "warning")
        return render_template("appointment/new.html")

    user_id = session["user_id"]
    user = User.search_user_by_id(user_id)

    Appointment.create(request.form["vaccine"], user_id,
                       user.location_id, **request.form)

    if (request.form["vaccine"] != "Fiebre Amarilla"):
        flash("Su turno ha sido registrado.")
    else:
        flash("Su solicitud de turno ha sido registrada, los administradores se comunicarán con usted a la brevedad.")
    return redirect(url_for("appointments"))


def have_active_appointment(user_id, vac_name):
    consulta = Appointment.have_active_appointment(user_id, vac_name)
    return consulta


def filter():
    lista = Appointment.appoint_list_filter(
        request.form["estado"], session["user_id"]) 

    return render_template("appointment/list.html", appoint_list=lista)

def cancel(appointment_id):
    Appointment.cancel_appointment(appointment_id, session["user_id"])
    rol = User.get_role(session["user_id"])
    if rol == 3:
        return redirect(url_for("appointments_location"))
    else:
        return redirect(url_for("appointments"))

def close(appointment_id, user_id):
    user = User.query.filter_by(id=user_id).first()
    lote = request.form["lote"]
    Appointment.close_appointment(appointment_id, lote, user, session["user_id"])
    return redirect(url_for("appointments_location"))
