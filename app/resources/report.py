from inspect import Attribute
from flask import redirect, render_template, request, url_for, session, flash, Flask
from app.helpers.decorators import login_required, has_permission

from app.models.report import Report
from app.models.vaccine import Vaccine
from app.models.appointment import Appointment
from app.helpers.validations import validate

app = Flask(__name__)

@login_required
@has_permission(1)
def create():
    tipo = request.form["tipo"]
    dates = []
    dates.append(request.form["date_start"])
    dates.append(request.form["date_end"])

    message = []
    condition = validate(request.form["date_start"], "fecha inicial", required=True, yesterday=True)
    if condition is not True:
        message.append(condition)
    condition = validate(request.form["date_end"], "fecha final", required=True, yesterday=True)
    if condition is not True:
        message.append(condition)
    condition = validate(dates, "fechas", valid_period=True)
    if condition is not True:
        message.append(condition)
    if message:
            for mssg in message:
                flash(mssg, "warning")
            return (redirect(url_for("report_new")))
    else:
        resp = Report.create(tipo, dates[0], dates[1])
        if resp == 0:
            return (redirect(url_for("reports")))
        else:
            path = Report.get_path(resp)
            report = Report.get_report(resp)
            return (render_template("report/existente.html", report=report, path=path))


@login_required
@has_permission(1)
def report_list_index():
    lista = Report.report_list()
    return (render_template("report/list.html", report_list=lista))

@login_required
@has_permission(1)
def new():
    return (render_template("report/new.html"))

@login_required
@has_permission(1)
def report_list():
    return (Report.report_list())

@login_required
@has_permission(1)
def get_path(report_id):
    return (Report.get_path(report_id))
