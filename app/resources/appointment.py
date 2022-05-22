from io import BytesIO

from flask import redirect, render_template, request, url_for, session, flash, Flask, send_file
from sqlalchemy import true
from app.models.appointment import Appointment
from app.models.vaccine import Vaccine
from app.helpers.validations import validate
import urllib.request


app = Flask(__name__)


def new():
    return render_template("appointment/new.html")


def index():
    return render_template("appointment/list.html")


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

    if (request.form["vaccine"] == "Gripe"):
        Vaccine.update_date(request.form["date"], user_id)
    else:
        Vaccine.create(request.form["vaccine"], request.form["date"], user_id)

    vac = Vaccine.search_vaccine(request.form["vaccine"], user_id)

    Appointment.create(vac, user_id, **request.form)
    if (request.form["vaccine"] != "Fiebre Amarilla"):
        flash("Su solicitud de turno ha sido registrada.")
    else:
        flash("Su solicitud de turno ha sido registrada, aguardando aprobación de los administradores.")
    return redirect(url_for("appointments"))


def preview():
    return render_template("appointment/preview_pdf.html")


def download():

    return send_file(BytesIO('/ing2-grupo33/app/static/PDFs/out.pdf'), attachment_filename='out.pdf', as_attachment=true)
    '''pdf_path = "/ing2-grupo33/app/static/PDFs"
    response = urllib.request.urlopen(pdf_path)
    file = open("out" + ".pdf", 'wb')
    file.write(response.read())
    file.close()'''


def print_pdf():
    Appointment.print_pdf()
