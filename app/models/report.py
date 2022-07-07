from ctypes import alignment
from sqlalchemy import Column, Integer, String, Date
from flask import redirect, url_for, flash, render_template
from app.db import db
import os
from fpdf import FPDF
import matplotlib.pyplot as plt

from app.models.vaccine import Vaccine
from app.resources import report
from app.models.user import User
from app.models.appointment import Appointment

class Report(db.Model):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(20))
    campo_1 = Column(Integer)
    campo_2 = Column(Integer)
    campo_3 = Column(Integer)
    campo_4 = Column(Integer)
    date_start = Column(Date)
    date_end = Column(Date)

    def __init__(
            self,
            name=None,
            type=None,
            campo_1=None,
            campo_2=None,
            campo_3=None,
            campo_4=None,
            date_start=None,
            date_end=None
        ):
            self.name = name,
            self.type = type,
            self.campo_1 = campo_1,
            self.campo_2 = campo_2,
            self.campo_3 = campo_3,
            self.campo_4 = campo_4,
            self.date_start = date_start,
            self.date_end = date_end
    
    @classmethod
    def create(cls, tipo, start, end):

        aux = cls.search_existente(tipo, start, end)
        if aux != None:
            return (aux.id)
        else:    
            if (tipo == "cancelados"):
                    name = "Turnos cancelados"
                    total = Appointment.between_dates(start, end)
                    cancelados_total = Appointment.get_cancelled(start, end)
                    cancelados_nurse = User.get_cancelled_bynurse(cancelados_total)
                    app = len(cancelados_total) - len(cancelados_nurse)
                    campo_1 = app
                    campo_2 = len(cancelados_nurse)
                    campo_3 = len(cancelados_total)
                    campo_4 = len(total)
                    report = Report(name=name, type=tipo, campo_1=campo_1, campo_2=campo_2, campo_3=campo_3, campo_4=campo_4, date_start=start, date_end=end)
                    db.session.add(report)
                    db.session.commit()
                    cls.create_pdf(report, "turnos cancelados", start, end)
                    flash("El reporte ha sido creado con éxito.", "info")
                    return 0

            if (tipo == "rango_edad"):
                    name = "Por Rango de edades"
                    total = Vaccine.between_dates(start, end)
                    vaccines = User.rango_edad(start, end, 0, 18)
                    campo_1 = len(vaccines)
                    vaccines = User.rango_edad(start, end, 18, 60)
                    campo_2 = len(vaccines)
                    vaccines = User.rango_edad(start, end, 60, 200)
                    campo_3 = len(vaccines)
                    campo_4 = len(total)
                    report = Report(name=name, type=tipo, campo_1=campo_1, campo_2=campo_2, campo_3=campo_3, campo_4=campo_4, date_start=start, date_end=end)
                    db.session.add(report)
                    db.session.commit()
                    cls.create_pdf(report, "vacunas por rango de edad", start, end)
                    flash("El reporte ha sido creado con éxito.", "info")
                    return 0

            if (tipo == "enfermedad"):
                    name = "Por Enfermedades"
                    vaccines = Vaccine.enfermedad(start, end, "Fiebre Amarilla")
                    campo_1 = len(vaccines)
                    vaccines = Vaccine.enfermedad(start, end, "Gripe")
                    campo_2 = len(vaccines)
                    vaccines = Vaccine.enfermedad(start, end, "Covid 19 Primera Dosis")
                    campo_3 = len(vaccines)
                    vaccines = Vaccine.enfermedad(start, end, "Covid 19 Segunda Dosis")
                    campo_4 = len(vaccines)
                    report = Report(name=name, type=tipo, campo_1=campo_1, campo_2=campo_2, campo_3=campo_3, campo_4=campo_4, date_start=start, date_end=end)
                    db.session.add(report)
                    db.session.commit()
                    cls.create_pdf(report, "vacunas por enfermedad", start, end)
                    flash("El reporte ha sido creado con éxito.", "info")
                    return 0
            
            if (tipo == "sede"):
                    name = "Por Sedes"
                    total = Vaccine.between_dates(start, end)
                    vaccines = Appointment.appoint_sede(start, end, "Terminal")
                    campo_1 = len(vaccines)
                    vaccines = Appointment.appoint_sede(start, end, "Palacio Municipal")
                    campo_2 = len(vaccines)
                    vaccines = Appointment.appoint_sede(start, end, "Cementerio")
                    campo_3 = len(vaccines)
                    campo_4 = len(total)
                    report = Report(name=name, type=tipo, campo_1=campo_1, campo_2=campo_2, campo_3=campo_3, campo_4=campo_4, date_start=start, date_end=end)
                    db.session.add(report)
                    db.session.commit()
                    cls.create_pdf(report, "vacunas por sede", start, end)
                    flash("El reporte ha sido creado con éxito.", "info")
                    return 0 

    @classmethod
    def search_existente(cls, tipo, start, end):
        report = Report.query.filter(cls.type==tipo, cls.date_start==start, cls.date_end==end).first()
        return report
    
    @classmethod
    def get_path(cls, id):
        report = Report.query.filter_by(id=id).first()
        path = "..//static/uploads/" + report.name + " " + str(report.id) + ".pdf"
        return path
    
    @classmethod
    def get_report(cls, id):
        report = Report.query.filter_by(id=id).first()
        return report

    @classmethod
    def report_list(cls):
        return (Report.query.all())

    @classmethod
    def create_pdf(cls, report, titulo, start, end):
        # path depende de donde tienen el repositorio localmente
        path = os.getcwd()
        path = path.replace("\\", "/")

        pdf = FPDF('P', 'mm', 'A4')

        # Add a page
        pdf.add_page()

        # logo
        pdf.image(
            (path + '/app/static/Logo_VacunAssist_1_chico.png'), 10, 8, 25)
        # font
        pdf.set_font('helvetica', 'B', 20)
        # text color
        pdf.set_text_color(150, 206, 122)
        
        # title
        pdf.cell(0, 25, 'Reporte de ' + str(titulo), border=0, ln=1, align='C')
        # line break
        pdf.ln(10)
        # Specify font
        pdf.set_font('helvetica', '', 15)
        pdf.set_text_color(10, 10, 10)

        chart_path = path + '/app/static/uploads/chart_' + str(report.id) + '.png'

        line1 = "Para el periodo de tiempo entre las fechas: " + str(start) + " // " + str(end) + "."
        line2 = "Se recolectó la siguiente información:"
        if (report.type=="cancelados"):
            line3 = "Turnos cancelados: " + str(report.campo_3) + " de " + str(report.campo_4) + " turnos registrados."
            line4 = "- Turnos cancelados por el paciente: " + str(report.campo_1)
            line5 = "- Turnos cancelados por un enfermero: " + str(report.campo_2)
            line6 = ""
            line7 = ""
            line8 = ""
            if (report.campo_3 > 0):
                names='Por paciente', 'Inasistencia'
                values=[report.campo_1, report.campo_2]
                colors = ['#96ce7a', '#DD7596']
                plt.pie(values, labels=names, labeldistance=1.15, wedgeprops = { 'linewidth' : 1, 'edgecolor' : 'white' }, colors=colors);
                plt.savefig(chart_path);
                pdf.image(chart_path, x=2, y=130, w=200)
        if (report.type=="rango_edad"):
            line3 = "Total de vacunas aplicadas: " + str(report.campo_4)
            line4 = "- A menores de 18 años: " + str(report.campo_1) + " vacunas aplicadas."
            line5 = "- De 18 a 60 años: " + str(report.campo_2) + " vacunas aplicadas."
            line6 = "- A mayores de 60 años: " + str(report.campo_3) + " vacunas aplicadas."
            line7 = ""
            line8 = ""
            if (report.campo_4 > 0):
                names='-18', '18 - 60', '+60'
                values=[report.campo_1, report.campo_2, report.campo_3]
                colors = ['#96ce7a', '#DD7596', '#949492']
                plt.pie(values, labels=names, labeldistance=1.15, wedgeprops = { 'linewidth' : 1, 'edgecolor' : 'white' }, colors=colors);
                plt.savefig(chart_path);
                pdf.image(chart_path, x=2, y=130, w=200)
        if (report.type=="enfermedad"):
            total = report.campo_1 + report.campo_2 + report.campo_3 + report.campo_4
            total_covid = report.campo_3 + report.campo_4
            line3 = "Total de vacunas aplicadas: " + str(total)
            line4 = "- Para fiebre amarilla: " + str(report.campo_1) + " vacunas aplicadas."
            line5 = "- Para gripe: " + str(report.campo_2) + " vacunas aplicadas."
            line6 = "- Para covid (Primera dosis): " + str(report.campo_3) + " vacunas aplicadas."
            line7 = "- Para covid (Segunda dosis): " + str(report.campo_4) + " vacunas aplicadas."
            line8 = "  - Para covid (Total): " + str(total_covid) + " vacunas aplicadas."
            if (total > 0):
                names='Fiebre amarilla', 'Gripe', 'Covid (1era dosis)', 'Covid (2da dosis)'
                values=[report.campo_1, report.campo_2, report.campo_3, report.campo_4]
                colors = ['#96ce7a', '#DD7596', '#949492', '#5a7c49']
                plt.pie(values, labels=names, labeldistance=1.15, wedgeprops = { 'linewidth' : 1, 'edgecolor' : 'white' }, colors=colors);
                plt.savefig(chart_path);
                pdf.image(chart_path, x=2, y=130, w=200)
        if (report.type=="sede"):
            line3 = "Total de vacunas aplicadas: " + str(report.campo_4)
            line4 = "- En sede Terminal: " + str(report.campo_1) + " vacunas aplicadas."
            line5 = "- En sede Cementerio: " + str(report.campo_2) + " vacunas aplicadas."
            line6 = "- En sede Palacio Municipal: " + str(report.campo_3) + " vacunas aplicadas."
            line7 = ""
            line8 = ""
            if (report.campo_4 > 0):
                names='Terminal', 'Cementerio', 'Palacio Municipal'
                values=[report.campo_1, report.campo_2, report.campo_3]
                colors = ['#96ce7a', '#DD7596', '#949492']
                plt.pie(values, labels=names, labeldistance=1.15, wedgeprops = { 'linewidth' : 1, 'edgecolor' : 'white' }, colors=colors);
                plt.savefig(chart_path);
                pdf.image(chart_path, x=2, y=130, w=200)
        # Add text
        pdf.cell(0, 10, line1, ln=True, align='L')
        pdf.cell(0, 10, line2, ln=True, align='L')
        pdf.cell(0, 10, line3, ln=True, align='L')
        pdf.cell(0, 10, line4, ln=True, align='L')
        pdf.cell(0, 10, line5, ln=True, align='L')
        pdf.cell(0, 10, line6, ln=True, align='L')
        pdf.cell(0, 10, line7, ln=True, align='L')
        pdf.cell(0, 10, line8, ln=True, align='L')

        complete_path = path + "/app/static/uploads/" + report.name + ' ' + str(report.id) + ".pdf"
        # Generate output
        pdf.output(dest='F', name=complete_path)

        return complete_path