from app.models.vaccine import Vaccine
from flask import redirect, render_template, request, url_for, session, flash, Flask

app = Flask(__name__)

def get_vaccines_names(user_id):
    consulta = Vaccine.get_vaccines_names(user_id)
    return consulta

def have_vaccine(user_id, vaccine_name):
    consulta = Vaccine.have_vaccine(user_id, vaccine_name)
    return consulta