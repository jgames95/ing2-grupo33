
from flask import redirect, render_template, request, url_for, session, flash, Flask
from app.models.appointment import Appointment
from app.models.vaccine import Vaccine
from app.helpers.validations import validate
from app.helpers.pag import PDF
from app.models.user import User

app = Flask(__name__)


def new():
    return render_template("appointment/new.html")


def index():
    return render_template("appointment/list.html", appoint_list=Appointment.appoint_list_filter("Todos", session["user_id"]))


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
            flash(mssg)
        return render_template("appointment/new.html")

    user_id = session["user_id"]
    user = User.search_user_by_id(user_id)

    Appointment.create(request.form["vaccine"], user_id,
                       user.first_name, user.last_name, **request.form)

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

    print('/////')
    print(lista[0])
    print(lista[1])
    print(lista[2])

    return render_template("appointment/list.html", appoint_list=lista)


def download():
    PDF.run()


def cancel(appointment_id):
    Appointment.cancel_appointment(appointment_id)
    return redirect(url_for("appointments"))
