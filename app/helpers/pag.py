from cmath import log
from fpdf import FPDF


class PDF(FPDF):
    def __init__(self):
        super().__init__()

    def header(self):
        # logo
        self.image('Logo_VacunAssist_1_chico.png', 10, 8, 25)
        # font
        self.set_font('helvetica', 'B', 20)
        # text color
        self.set_text_color(150, 206, 122)
        # title
        self.cell(0, 25, 'Certificado De Vacunación',
                  border=0, ln=1, align='C')
        # line break
        self.ln(20)

    def run():
        # create a FPDF object
        pdf = PDF('P', 'mm', 'A4')

        pdf.header()

        # Add a page
        pdf.add_page()

        # Specify font
        pdf.set_font('times', '', 16)

        # Add text
        #pdf.cell(40, 10, 'Hello world!', ln=True)
        #pdf.cell(80, 10, 'Bye bro', border=1)

        # Generate output
        pdf.output('segundaPrueba.pdf')
        pdf.output('descarga.pdf')
        log("llegue")


# si corres en consola este .py te guarda en la carpeta el pdf correctamente
