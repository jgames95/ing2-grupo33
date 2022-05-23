from datetime import date
from sqlalchemy import Column, Integer, Date, String, desc
from app.db import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from app.models.vaccine import Vaccine
from app.models.state import State
from fpdf import FPDF


class Appointment(db.Model):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    vaccine_name = Column(String(30))
    state_id = Column(Integer, ForeignKey("states.id"))
    state = relationship(State)
    date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))

    def __init__(self, user_id=None, vaccine_name=None, date=None):
        self.user_id = user_id
        self.vaccine_name = vaccine_name
        self.state_id = 1
        self.date = date

    @classmethod
    def create(cls, vac_name, user_id, **kwargs):
        appointment = Appointment(vaccine_name=vac_name,
                                  date=kwargs["date"],
                                  user_id=user_id)
        if (vac_name != "Fiebre Amarilla"):
            appointment.state_id = 2
        db.session.add(appointment)
        unique_name = "usuario" + str(appointment.user_id) + "_vacuna" + appointment.vaccine_name + "_estado" + str(appointment.state_id)
        cls.create_pdf(unique_name)
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
    def close_appointment(cls, appointment_id):
        cls.change_status(appointment_id, 5)

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

        if estado == "Aceptado":
            for a, s in appointments:
                if (a.state_id == 2):
                    n = "..//static/uploads/" + "usuario" + str(a.user_id) + "_idturno" + str(a.id) + ".pdf"
                    lista.append((a, s, n))
        elif estado == "Solicitado":
            for a, s in appointments:
                if (a.state_id == 1):
                    n = ""
                    lista.append((a, s, n))
        elif estado == "Todos":
            for a, s in appointments:
                n = "..//static/uploads/" + "usuario" + str(a.user_id) + "_idturno" + str(a.id) + ".pdf"
                lista.append((a, s, n))
        
        return lista

    @classmethod
    def create_pdf(cls, name):
        #path depende de donde tienen el repositorio localmente
        path = 'C:/Users/Jimena/Desktop/IS2/'
        
        # logo
        FPDF.image((path + 'ing2-grupo33/app/static/Logo_VacunAssist_1_chico.png'), 10, 8, 25)
        # font
        FPDF.set_font('helvetica', 'B', 20)
        # text color
        FPDF.set_text_color(150, 206, 122)
        # title
        FPDF.cell(0, 25, 'Certificado De Vacunación',
                  border=0, ln=1, align='C')
        # line break
        FPDF.ln(20)

        pdf = FPDF('P', 'mm', 'A4')

        # Add a page
        pdf.add_page()

        # Specify font
        pdf.set_font('times', '', 16)

        # Add text
        #pdf.cell(40, 10, 'Hello world!', ln=True)
        #pdf.cell(80, 10, 'Bye bro', border=1)
        
        complete_path = path + "ing2-grupo33/app/static/uploads/"
        # Generate output
        pdf.output(dest='F', name=(complete_path + name))
