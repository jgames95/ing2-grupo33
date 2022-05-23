
from os import path, environ, urandom
from flask import Flask, render_template, Blueprint
from flask_session import Session
from config import config
from app import db

from app.resources import auth, appointment, user, vaccine

from app.helpers import handler
from app.helpers import auth as helper_auth

import logging
from datetime import datetime, timedelta

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


def create_app(environment="development"):
    # Configuración inicial de la app
    app = Flask(__name__)
    #app.config["JSON_SORT_KEYS"] = False

    app.secret_key = environ.get("SECRET_KEY") or urandom(24)

    # Carga de la configuración
    env = environ.get("FLASK_ENV", environment)
    app.config.from_object(config[env])

    # Server Side session
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = "false"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=50)

    Session(app)

    # Configure db
    db.init_app(app)

    # Funciones que se exportan al contexto de Jinja2
    app.jinja_env.globals.update(is_authenticated=helper_auth.authenticated)
    app.jinja_env.globals.update(is_admin=user.is_admin)
    app.jinja_env.globals.update(is_pacient=user.is_pacient)
    app.jinja_env.globals.update(is_active=user.is_active)
    app.jinja_env.globals.update(vaccines_from_user=user.vaccines_from_user)
    app.jinja_env.globals.update(
        applicatedvac_from_user=user.applicatedvac_from_user)
    app.jinja_env.globals.update(is_elder=user.is_elder)
    app.jinja_env.globals.update(get_vaccines_names=vaccine.get_vaccines_names)
    app.jinja_env.globals.update(have_vaccine=vaccine.have_vaccine)
    app.jinja_env.globals.update(
        have_gripe_lastyear=vaccine.have_gripe_lastyear)
    app.jinja_env.globals.update(covid2_avalaible=vaccine.covid2_avalaible)
    app.jinja_env.globals.update(
        have_active_appointment=appointment.have_active_appointment)

    # Autenticación
    app.add_url_rule("/iniciar_sesion", "auth_login", auth.login)
    app.add_url_rule("/cerrar_sesion", "auth_logout", auth.logout)
    app.add_url_rule(
        "/autenticacion", "auth_authenticate", auth.authenticate, methods=["POST"]
    )
    app.add_url_rule(
        "/iniciar_sesion", "user_confirmation", user.confirm_account, methods=["POST"]
    )
    app.add_url_rule("/confirmacion", "user_confirm", user.confirm)

    # Rutas de Usuarios
    app.add_url_rule("/usuario", "user_create", user.create, methods=["POST"])
    app.add_url_rule("/usuario/nuevo", "user_new", user.new)

    app.add_url_rule("/usuario/editar/<int:user_id>", "users_edit", user.edit)
    app.add_url_rule(
        "/usuario/actualizar", "users_update", user.update, methods=["POST", "GET"]
    )
    '''app.add_url_rule(
        "/usuarios/results", "user_search", user.search, methods=["POST", "GET"]
    )'''
    app.add_url_rule("/usuario/perfil", "user_profile", user.profile)

    # Rutas de Turnos
    app.add_url_rule("/turnos/nuevo", "appointment_new", appointment.new)
    app.add_url_rule("/turnos", "appointment_create",
                     appointment.create, methods=["POST"])
    app.add_url_rule("/turnos", "appointments", appointment.index)
    #app.add_url_rule("/turnos", "appointment_download", appointment.download)
    app.add_url_rule("/turnos/<int:appointment_id>", "appointment_cancel", appointment.cancel, methods=["POST", "GET"])
    app.add_url_rule("/turnos/filtro", "appointmentfilter",
                     appointment.filter, methods=["POST", "GET"])

    # Ruta para el Home (usando decorator)

    @app.route("/")
    def home():
        return render_template("home.html")

    # Handlers
    app.register_error_handler(404, handler.not_found_error)
    app.register_error_handler(401, handler.unauthorized_error)
    app.register_error_handler(500, handler.internal_server_error)
    app.register_error_handler(400, handler.bad_request)

    # Retornar la instancia de app configurada
    return app
