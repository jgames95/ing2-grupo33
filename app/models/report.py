from sqlalchemy import Column, Integer, String, Date
from flask import redirect, url_for, flash, render_template
from app.db import db
import os

from app.models.vaccine import Vaccine
from app.resources import report
from app.models.user import User
from app.models.appointment import Appointment

class Report(db.Model):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    campo_1 = Column(Integer)
    campo_2 = Column(Integer)
    campo_string = Column(String(40))
    date_start = Column(Date)
    date_end = Column(Date)
    path = Column(String(100))

    def __init__(
            self,
            name=None,
            campo_1=None,
            campo_2=None,
            campo_string=None,
            date_start=None,
            date_end=None,
            path=None
        ):
            self.name = name,
            self.campo_1 = campo_1,
            self.campo_2 = campo_2,
            self.campo_string = campo_string,
            self.date_start = date_start,
            self.date_end = date_end,
            self.path = path
    
    @classmethod
    def create(cls, tipo, dates, att):
        path = os.getcwd()
        path = path.replace("\\", "/") 
        fechas = str(dates[0]) + "_" + str(dates[1])
        fechas = fechas.replace("/", "-")
        resp = []

        if (tipo == "total"):
            name = "T--" + fechas
            path = path + "/" + name
            vaccines = Vaccine.between_dates(dates[0], dates[1])
            aux = cls.search(name)
            if vaccines:
                campo_1 = len(vaccines)
                campo_2 = len(vaccines)
                campo_string = ""
                if (aux):
                    resp.append("actualizar")
                    resp.append(aux.id)
                    resp.append(tipo)
                    resp.append(dates)
                    resp.append(campo_1)
                    resp.append(campo_2)
                    resp.append(campo_string)
                    return (resp)
                else:
                    report = Report(name=name, campo_1=campo_1, date_start=dates[0], date_end=dates[1], path=path)
                    db.session.add(report)
                    db.session.commit()
                    flash("El reporte ha sido creado con éxito.", "info")

        if (tipo == "cancelados"):
            name = "C--" + fechas
            path = path + "/" + name
            app = Appointment.get_cancelled(dates[0], dates[1])
            total = Appointment.between_dates(dates[0], dates[1])
            aux = cls.search(name)
            if app:
                campo_1 = len(vaccines)
                campo_2 = len(total)
                campo_string = ""
                if (aux):
                    resp.append("actualizar")
                    resp.append(aux.id)
                    resp.append(tipo)
                    resp.append(dates)
                    resp.append(campo_1)
                    resp.append(campo_2)
                    resp.append(campo_string)
                    return (resp)
                else:
                    report = Report(name=name, campo_1=campo_1, campo_2=campo_2, date_start=dates[0], date_end=dates[1], path=path)
                    db.session.add(report)
                    db.session.commit()
                    flash("El reporte ha sido creado con éxito.", "info")  
            else:
                flash("No existen turnos cancelados para el periodo de tiempo ingresado.", "error")  

        if (tipo == "rango_edad"):
            name = "RE--" + fechas + "--" + att[0] + "_" + att[1]
            path = path + "/" + name
            vaccines = User.rango_edad(dates[0], dates[1], att)
            total = Vaccine.between_dates(dates[0], dates[1])
            aux = cls.search(name)
            if vaccines:
                if vaccines[0]=="null":
                    flash("No existen vacunas registradas para el rango de edad ingresado.", "error")
                else:
                    campo_1 = len(vaccines)
                    campo_2 = len(total)
                    campo_string = ("De " + att[0] + " a " + att[1] + " años de edad.")
                    if (aux):
                        resp.append("actualizar")
                        resp.append(aux.id)
                        resp.append(tipo)
                        resp.append(dates)
                        resp.append(campo_1)
                        resp.append(campo_2)
                        resp.append(campo_string)
                        return (resp)
                    else:
                        report = Report(name=name, campo_1=campo_1, campo_2=campo_2, campo_string=campo_string, date_start=dates[0], date_end=dates[1], path=path)
                        db.session.add(report)
                        db.session.commit()
                        flash("El reporte ha sido creado con éxito.", "info") 

        if (tipo == "enfermedad"):
            name = "E--" + fechas + "--" + att
            path = path + "/" + name
            vaccines = Vaccine.enfermedad(dates[0], dates[1], att)
            total = Vaccine.between_dates(dates[0], dates[1])
            aux = cls.search(name)
            if vaccines:
                campo_1 = len(vaccines)
                campo_2 = len(total)
                campo_string = att
                if (aux):
                    resp.append("actualizar")
                    resp.append(aux.id)
                    resp.append(tipo)
                    resp.append(dates)
                    resp.append(campo_1)
                    resp.append(campo_2)
                    resp.append(campo_string)
                    return (resp)
                else:
                    report = Report(name=name, campo_1=campo_1, campo_2=campo_2, campo_string=campo_string, date_start=dates[0], date_end=dates[1], path=path)
                    db.session.add(report)
                    db.session.commit()
                    flash("El reporte ha sido creado con éxito.", "info") 
            else:
                flash("No existen vacunas registradas para la enfermedad ingresada.", "error")
        
        if (tipo == "sede"):
            name = "S--" + fechas + "--" + att
            path = path + "/" + name
            vaccines = Appointment.appoint_sede(dates[0], dates[1], att)
            total = Vaccine.between_dates(dates[0], dates[1])
            aux = cls.search(name)
            if vaccines:
                campo_1 = len(vaccines)
                campo_2 = len(total)
                campo_string = att
                if (aux):
                    resp.append("actualizar")
                    resp.append(aux.id)
                    resp.append(tipo)
                    resp.append(dates)
                    resp.append(campo_1)
                    resp.append(campo_2)
                    resp.append(campo_string)
                    return (resp)
                else:
                    report = Report(name=name, campo_1=campo_1, campo_2=campo_2, campo_string=campo_string, date_start=dates[0], date_end=dates[1], path=path)
                    db.session.add(report)
                    db.session.commit()
                    flash("El reporte ha sido creado con éxito.", "info") 
            else:
                flash("No existen vacunas registradas para la sede ingresada.", "error")
    
    @classmethod
    def search(cls, name):
        report = Report.query.filter_by(name=name).first()
        return report
    
    @classmethod
    def update(cls, id, campo_1, campo_2):
        report = db.session.query(Report).where(Report.id==id).first()
        report.campo_1 = campo_1
        report.campo_2 = campo_2
        db.session.commit()
        redirect(url_for("reports"))
        flash("El reporte ha sido actualizado con éxito.", "info")
    
    @classmethod
    def report_list(cls):
        return (Report.query.all())