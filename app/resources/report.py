from inspect import Attribute
from flask import redirect, render_template, request, url_for, session, flash, Flask
from app.helpers.decorators import login_required, has_permission

from app.models.report import Report
from app.helpers.validations import validate

app = Flask(__name__)

@login_required
@has_permission(1)
def create():
    tipo = request.form["tipo"]
    dates = (request.form["date_start"], request.form["date_end"])

    message = []
    condition = validate(request.form["date_start"], "Fecha inicial", required=True, date=True)
    if condition is not True:
        message.append(condition)
    condition = validate(request.form["date_end"], "Fecha final", required=True, date=True)
    if condition is not True:
        message.append(condition)
    condition = validate(dates, "fechas", valid_period=True)
    if condition is not True:
        message.append(condition)
    if message:
            for mssg in message:
                flash(mssg)
            return (redirect(url_for("report_new")))
    else:
        if (tipo == "total"):
            att = ""
            resp = Report.create(tipo, dates, att)
        elif (tipo == "cancelados"):
            att = ""
            resp = Report.create(tipo, dates, att)
        elif (tipo == "rango_edad"):
            condition = validate(request.form["edad_start"], "Edad inicial", required=True)
            if condition is not True:
                message.append(condition)
            condition = validate(request.form["edad_end"], "Edad final", required=True)
            if condition is not True:
                message.append(condition)
            att = (request.form["edad_start"], request.form["edad_end"])
            condition = validate(att, "edades", range=True)
            if condition is not True:   
                message.append(condition)
            if message:
                for mssg in message:
                    flash(mssg)
                return (redirect(url_for("report_new")))
            else:
                resp = Report.create(tipo, dates, att)
        elif (tipo == "enfermedad"):
            att = request.form["selection"]
            condition = validate(att, "Enfermedad", required=True)
            if condition is not True:   
                flash(condition)
                return (redirect(url_for("report_new")))
            else:
                resp = Report.create(tipo, dates, att)
        elif (tipo == "sede"):
            att = request.form["selection"]
            condition = validate(att, "Enfermedad", required=True)
            if condition is not True:   
                flash(condition)
                return (redirect(url_for("report_new")))
            else:
                resp = Report.create(tipo, dates, att)
        if resp[0] == "actualizar":
            return (render_template("report/confirmation_update.html", report_id=resp[1], tipo=resp[2], dates=resp[3], campo_1=resp[4], campo_2=resp[5], campo_string=resp[6]))
        else:    
            return (render_template("report/list.html", report_list=report_list()))


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
def update(id, campo_1, campo_2):
    Report.update(id, campo_1, campo_2)
    return (redirect(url_for("reports")))

@login_required
@has_permission(1)
def report_list():
    return (Report.report_list())