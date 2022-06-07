from datetime import date
from sqlalchemy import Column, Integer, Date, String, desc
from app.db import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from app.models.vaccine import Vaccine
from app.models.state import State
from app.models.location import Location
from datetime import date

from fpdf import FPDF
import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import  MIMEBase
from email.encoders import encode_base64

class Appointment(db.Model):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    vaccine_name = Column(String(30))
    state_id = Column(Integer, ForeignKey("states.id"))
    state = relationship(State)
    date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    location = relationship(Location)

    def __init__(self, user_id=None, vaccine_name=None, date=None, location_id=None):
        self.user_id = user_id
        self.vaccine_name = vaccine_name
        self.state_id = 1
        self.date = date
        self.location_id=location_id

    @classmethod
    def create(cls, vac_name, user_id, first_name, last_name, location_id, **kwargs):
        appointment = Appointment(vaccine_name=vac_name,
                                  date=kwargs["date"],
                                  user_id=user_id,
                                  location_id=location_id)
        if (vac_name != "Fiebre Amarilla"):
            appointment.state_id = 2
        db.session.add(appointment)
        db.session.commit()

    @classmethod
    def change_status(cls, appointment_id, state_id):
        appointment = Appointment.query.filter_by(id=appointment_id).first()
        appointment.state_id = state_id
        db.session.commit()

    @classmethod
    def approve_appointment(cls, appointment_id):
        cls.change_status(appointment_id, 2)

    @classmethod
    def reject_appointment(cls, appointment_id):
        cls.change_status(appointment_id, 3)

    @classmethod
    def cancel_appointment(cls, appointment_id):
        cls.change_status(appointment_id, 4)

    @classmethod
    def close_appointment(cls, appointment_id, lote, user):
        appointment = Appointment.query.filter_by(id=appointment_id).first()
        appointment.state_id = 5
        db.session.commit()
        Vaccine.create(appointment.vaccine_name, date.today(), appointment.user_id)
        unique_name = "usuario" + \
            str(appointment.user_id) + "_vacuna" + \
            appointment.vaccine_name + ".pdf"
        name = user.first_name + ' ' + user.last_name
        path = cls.create_pdf(unique_name, appointment, name, lote)
        cls.send_pdf(user, path)

    @classmethod
    def appoint_list(cls, user_id):
        appoint_list = (
            db.session.query(Appointment, State)
            .select_from(Appointment)
            .join(State)
            .where(Appointment.user_id == user_id)
            .order_by(Appointment.date.desc())
            .all()
        )
        return appoint_list

    @classmethod
    def have_active_appointment(cls, user_id, vac_name):
        appoint_list = Appointment.query.filter_by(user_id=user_id).all()
        consulta = False
        for ap in appoint_list:
            if (ap.vaccine_name == vac_name and (ap.state_id == 2 or ap.state_id == 1)):
                consulta = True
        return consulta

    @classmethod
    def appoint_list_filter(cls, estado, user_id):

        appointments = Appointment.appoint_list(user_id)
        lista = []

        if estado == "Aceptados":
            for a, s in appointments:
                if (a.state_id == 2):
                    n = "..//static/uploads/" + "usuario" + \
                        str(a.user_id) + "_vacuna" + \
                        str(a.vaccine_name) + ".pdf"
                    lista.append((a, s, n))
        elif estado == "Solicitados":
            for a, s in appointments:
                if (a.state_id == 1):
                    n = "..//static/uploads/" + "usuario" + \
                        str(a.user_id) + "_vacuna" + \
                        str(a.vaccine_name) + ".pdf"
                    lista.append((a, s, n))
        elif estado == "Cerrados":
            for a, s in appointments:
                if (a.state_id == 5):
                    n = "..//static/uploads/" + "usuario" + \
                        str(a.user_id) + "_vacuna" + \
                        str(a.vaccine_name) + ".pdf"
                    lista.append((a, s, n))
        elif estado == "Todos":
            for a, s in appointments:
                n = "..//static/uploads/" + "usuario" + \
                    str(a.user_id) + "_vacuna" + str(a.vaccine_name) + ".pdf"
                lista.append((a, s, n))

        return lista

    @classmethod
    def appointments_from_location(cls, location_id):
        appoint_list = Appointment.query.filter_by(location_id=location_id, state_id=2, date=date.today()).all()
        #appoint_list = Appointment.query.filter_by(location_id=location_id, state_id=2).all()
        return appoint_list

    @classmethod
    def create_pdf(cls, name, appointment, name_line, lote):
        # path depende de donde tienen el repositorio localmente
        path = os.getcwd()
        path = path.replace("\\","/")

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
        pdf.cell(0, 25, 'Certificado De Vacunación',
                 border=0, ln=1, align='C')
        # line break
        pdf.ln(20)

        # Specify font
        pdf.set_font('times', '', 20)
        pdf.set_text_color(10, 10, 10)

        line1 = "Se certifica que " + str(name_line)
        line2 = "Recibio la vacuna " + \
            str(appointment.vaccine_name)+" el dia: "+str(appointment.date)
        line3 = "Con lote: " + str(lote)

        # Add text
        pdf.cell(0, 10, line1, ln=True, align='C')
        pdf.cell(0, 10, line2, ln=True, align='C')
        pdf.cell(0, 10, line3, ln=True, align='C')

        complete_path = path + "/app/static/uploads/"
        # Generate output
        pdf.output(dest='F', name=(complete_path + name))

        return complete_path + name

    @classmethod
    def send_pdf(cls, user, file_path):
        conn = smtplib.SMTP('smtp.gmail.com', 587)
        sender_email = "infinityloop33.help@gmail.com"
        receiver_email = user.email
        password = "vuiosiqvpwburvni"
        subject = "Certificado de Vacunación - VacunAssist"
        message = ('Hola ' + (user.first_name).capitalize() + ' ' + (user.last_name).capitalize()  + '. \n\n' +
        'Te acercamos tu certificado de vacunación. \n\n' +
        'También se encuentra disponible para descargar en la página web, en la sección de Turnos\n\n'+
        'Gracias,\nVacunassist' + '\n\n****')
        type(conn)
        conn.ehlo()
        conn.starttls()
        conn.login(sender_email, password)
        header = MIMEMultipart()
        header['Subject'] = subject
        header['From'] = sender_email
        header['To'] = user.email
        message = MIMEText(message, _subtype='plain')
        header.attach(message)
        if (os.path.isfile(file_path)):
            attached = MIMEBase('application', 'octet-stream')
            attached.set_payload(open(file_path, "rb").read())
            encode_base64(attached)
            attached.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file_path))
            header.attach(attached)
        conn.sendmail(sender_email, receiver_email, header.as_string())
        conn.quit()