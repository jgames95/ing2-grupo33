from flask import redirect, render_template, request, url_for, session, flash, Flask
from app.models.user import User
from app.models.role import Role
from app.models.vaccine import Vaccine
from app.models.location import Location
from app.helpers.validations import validate
from app.helpers.decorators import login_required, has_permission
import json
import random
import sys

app = Flask(__name__)


# Protected resources
'''@login_required
@has_permission("user_index")'''
'''def index():
    page = request.args.get("page", 1, type=int)
    users = User.query.order_by(User.first_name.asc()).paginate(
            page, 5, False
        )
    
    next_url = url_for("user_index", page=users.next_num) if users.has_next else None
    prev_url = url_for("user_index", page=users.prev_num) if users.has_prev else None

    roles = Role.query.all()

    return render_template(
        "user/index.html",
        users=users.items,
        next_url=next_url,
        prev_url=prev_url,
        roles=roles,
    )'''


@login_required
@has_permission(2)
def confirm():
    return render_template("user/confirm.html")


@login_required
@has_permission(2)
def confirm_account():
    user_input = request.form["token"]
    user_logged_id = session["user_id"]
    token = User.get_token(user_logged_id)
    if (int(user_input) == token):
        flash("El usuario fue confirmado")
        User.activate_account(user_logged_id)
        return redirect(url_for("home"))
    else:
        flash("El token ingresado es incorrecto")
        return render_template("user/confirm.html")


def new():
    locations = Location.query.all()
    return render_template("user/new.html", locations=locations)


def create():
    message = []
    condition = validate(
        request.form["email"], "Correo", required=True, email=True)
    valid_mail = condition
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["password"], "Clave", required=True, min_length='6'
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["first_name"], "Nombre", required=True, text=True)
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["last_name"], "Apellido", required=True, text=True
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["dni"], "DNI", required=True, min_length='7'
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["telephone"], "Telefono", required=True
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["date_of_birth"], "Fecha de Nacimiento", required=True, date=True
    )
    if condition is not True:
        message.append(condition)

    if (request.form["covid1"] == "Si"):
        condition = validate(
            request.form["covid1_date"], "Fecha de aplicación de vacuna - primera dosis Covid19", required=True, date=True
        )
        if condition is not True:
            message.append(condition)

    if (request.form["covid2"] == "Si"):
        condition = validate(
            request.form["covid2_date"], "Fecha de aplicación de vacuna - segunda dosis Covid19", required=True, date=True
        )
        if condition is not True:
            message.append(condition)

    if (request.form["gripe"] == "Si"):
        condition = validate(
            request.form["gripe_date"], "Fecha de aplicación de vacuna - Gripe", required=True, lessthanayear=True
        )
        if condition is not True:
            message.append(condition)

    if (request.form["fiebre"] == "Si"):
        condition = validate(
            request.form["fiebre_date"], "Fecha de aplicación de vacuna - Fiebre Amarilla", required=True, date=True,
        )
        if condition is not True:
            message.append(condition)

    if (request.form["covid1"] == "Si") and (request.form["covid2"] == "Si"):
        data = {
            "date1": request.form["covid1_date"],
            "date2": request.form["covid2_date"]
        }
        condition = validate(
            data, "dosis de Covid19", coviddate=True
        )
        if condition is not True:
            message.append(condition)

    if (request.form["covid1"] == "No") and (request.form["covid2"] == "Si"):
        message.append(
            "No puede tener aplicada solo la segunda dosis de Covid19, por favor\
            seleccione Si en la primera dosis de Covid19 e ingrese la fecha de aplicación"
        )

    if valid_mail is True and not User.valid_email(request.form["email"]):
        message.append(
            "Ya existe un usuario con ese email, por favor\
            ingrese uno nuevo"
        )

    if not User.valid_dni(request.form["dni"]):
        message.append(
            "Ya existe un paciente con ese dni, por favor\
            ingrese uno nuevo"
        )

    locations = Location.query.all()
    if message:
        for mssg in message:
            flash(mssg)
        return render_template("user/new.html", locations=locations)

    User.create_pacient(**request.form)

    user = User.search_user_by_email(request.form["email"])

    User.add_vaccines(request.form, user)

    User.add_automatic_appointments(user)

    message = ('Subject: Confirmar tu cuenta de Vacunassist\n\n Hola ' +
               (user.first_name).capitalize() + ' ' + (user.last_name).capitalize() + '. ' +
               'Ya creaste tu cuenta en Vacunassist. Ahora solo hay que confirmarla para poder utilizarla.\n\n' +
               'Cuando inicie sesion por primera vez le va a solicitar que ingrese un token para confirmar la cuenta. El numero que tiene que ingresar es el siguiente:\n\n'
               'Token: ' + str(user.token) +
               '\n\nGracias,\nVacunassist' + '\n\n****' +
               '\nSi no creaste una cuenta en nuestro sitio, por favor ignore este e-mail.').encode('utf-8')

    User.send_plaintext_email(request.form["email"], message)

    return redirect(url_for("auth_login"))


@login_required
@has_permission(2)
def edit(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    locations = Location.query.all()
    return render_template("user/update.html", user=user, locations=locations)


@login_required
@has_permission(2)
def update():
    message = []
    condition = validate(
        request.form["first_name"], "Nombre", required=True, text=True)
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["last_name"], "Apellido", required=True, text=True
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["telephone"], "Telefono", required=True
    )
    if condition is not True:
        message.append(condition)

    locations = Location.query.all()

    if message:
        for mssg in message:
            flash(mssg)
        return render_template("user/update.html", user=request.form, locations=locations)

    User.update(user_id=session["user_id"], kwargs=request.form)
    return redirect(url_for("user_profile"))


'''@login_required
@has_permission("user_index")'''
'''def search():
    page = request.args.get("page", 1, type=int)
    form = request.form.to_dict()

    if not form:
        form = request.args.get("form")
        form = form.replace('"', "'")
        form = form.replace("'", '"')
        form = json.loads(form)
    
    users = User.filter(page, form)

    next_url = (
        url_for("user_search", page=users.next_num, form=form)
        if users.has_next
        else None
    )
    prev_url = (
        url_for("user_search", page=users.prev_num, form=form)
        if users.has_prev
        else None
    )

    return render_template(
        "user/search_results.html",
        users=users.items,
        next_url=next_url,
        prev_url=prev_url,
    )'''


@login_required
@has_permission(2)
def profile():
    user = User.search_user_by_id(session["user_id"])
    return render_template("user/profile.html", user=user)


@login_required
@has_permission(1)
def new_nurse():
    return render_template("nurse/new.html")


@login_required
@has_permission(1)
def create_nurse():
    message = []
    condition = validate(
        request.form["email"], "Correo", required=True, email=True)
    valid_mail = condition
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["password"], "Clave", required=True, min_length='6'
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["first_name"], "Nombre", required=True, text=True)
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["last_name"], "Apellido", required=True, text=True
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["dni"], "DNI", required=True, min_length='7'
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["telephone"], "Telefono", required=True
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["date_of_birth"], "Fecha de Nacimiento", required=True, date=True
    )
    if condition is not True:
        message.append(condition)

    if valid_mail is True and not User.valid_email(request.form["email"]):
        message.append(
            "Ya existe un usuario con ese email, por favor\
            ingrese uno nuevo"
        )

    if not User.valid_nurse_dni(request.form["dni"]):
        message.append(
            "Ya existe un paciente con ese dni, por favor\
            ingrese uno nuevo"
        )

    if message:
        for mssg in message:
            flash(mssg)
        return render_template("nurse/new.html")

    User.create_nurse(**request.form)

    return redirect(url_for("nurses_list"))


@login_required
@has_permission(3)
def profile_nurse():
    user = User.search_user_by_id(session["user_id"])
    return render_template("nurse/profile.html", user=user)


@login_required
@has_permission(3)
def profile_appointment(user_id):
    user = User.search_user_by_id(user_id)
    return render_template("user/profile_appointment.html", user=user)


@login_required
@has_permission(3)
def edit_nurse(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    return render_template("nurse/update.html", user=user)


@login_required
@has_permission(3)
def update_nurse():
    message = []
    condition = validate(
        request.form["first_name"], "Nombre", required=True, text=True)
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["last_name"], "Apellido", required=True, text=True
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["telephone"], "Telefono", required=True
    )
    if condition is not True:
        message.append(condition)

    if message:
        for mssg in message:
            flash(mssg)
        return render_template("nurse/update.html", user=request.form)

    User.update_nurse(user_id=session["user_id"], kwargs=request.form)
    return redirect(url_for("nurse_profile"))


def is_admin(user_id):
    consulta = User.get_role(user_id)
    return (consulta == 1)


def is_pacient(user_id):
    consulta = User.get_role(user_id)
    return (consulta == 2)


def is_nurse(user_id):
    consulta = User.get_role(user_id)
    return (consulta == 3)


def is_active(user_id):
    consulta = User.is_active(user_id)
    return consulta


def vaccines_from_user(user_id):
    list = Vaccine.get_vaccines(user_id)
    return list


def applicatedvac_from_user(user_id):
    list = Vaccine.get_applicatedvaccines(user_id)
    return list


def is_elder(user_id):
    consulta = User.is_elder(user_id)
    return consulta


def return_fullname(user_id):
    name = User.get_fullname(user_id)
    return name


def return_location(user_id):
    name = User.get_location(user_id)
    return name


def return_age(user_id):
    age = User.get_age(user_id)
    return age


def return_email(user_id):
    email = User.get_email(user_id)
    return email


def filter():
    lista = User.nurse_list_filter(
        request.form["sede"])
    return render_template("nurse/list.html", nurse_list=lista)


def change_location(user_id):
    location = request.form["sede"]

    User.change_location(location, user_id)

    user = User.search_user_by_id(user_id)

    message = ('Subject: Cambio de sede asignada\n\n Hola ' +
               (user.first_name).title() + ' ' + (user.last_name).title() + '. ' +
               'Te informamos que has sido asignado a la sede: ' + location + '.\n\n' +
               'Frente a cualquier inconveniente pongase en contacto con un Administrador.'
               +
               '\n\nGracias,\nVacunassist' + '\n\n****').encode('utf-8')

    User.send_plaintext_email(user.email, message)

    return redirect(url_for("nurses_list"))


def delete_location(user_id):
    User.change_location("NotAssigned", user_id)
    return redirect(url_for("nurses_list"))


@login_required
@has_permission(1)
def index_filter():
    return (render_template("nurse/list.html", nurse_list=User.nurse_list_filter("Todos")))
