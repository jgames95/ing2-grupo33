from cmath import log
from fpdf import FPDF
from app.models.appointment import Appointment
from app.models.user import User


class PDF():
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


# si corres en consola este .py te guarda en la carpeta el pdf correctamente
