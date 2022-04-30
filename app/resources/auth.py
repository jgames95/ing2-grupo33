from flask import redirect, render_template, request, url_for, session, flash
from app.models.user import User
from os import environ
import hashlib

# Configuracion del login

def login():
    return render_template("auth/login.html")

def authenticate():

    params = request.form
    user = User.query.filter(
        User.email == params["email"],
        User.password == hashlib.sha256(params["password"].encode("utf-8")).hexdigest(),
    ).first()
    if not user:
        flash("Correo y/o clave incorrecto.")
        return redirect(url_for("auth_login"))
    if int(user.active) != 1:
        flash("Necesita confirmar su cuenta")
        return redirect(url_for("auth_login"))
    session["user_id"] = user.id
    flash("La sesión se inició correctamente.")
    return redirect(url_for("home"))


def logout():
    del session["user_id"]
    session.clear()
    flash("La sesión se cerró correctamente.")

    return redirect(url_for("auth_login"))

