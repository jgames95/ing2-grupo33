from flask import redirect, render_template, request, url_for, session, flash, Flask
from app.models.user import User
from app.models.role import Role
from app.helpers.validations import validate
from app.helpers.decorators import login_required, has_permission
import json

app = Flask(__name__)


# Protected resources
@login_required
@has_permission("user_index")
def index():
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
    )

def new():
    return render_template("user/new.html")

def create():
    message = []
    condition = validate(request.form["email"], "Correo", required=True, email=True)
    valid_mail = condition
    if condition is not True:
        message.append(condition)
    
    condition = validate(
        request.form["password"], "Clave", required=True, min_length="6"
    )
    if condition is not True:
        message.append(condition)
    
    condition = validate(request.form["first_name"], "Nombre", required=True, text=True)
    if condition is not True:
        message.append(condition)
    
    condition = validate(
        request.form["last_name"], "Apellido", required=True, text=True
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["dni"], "DNI", required=True, min_length=8
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["telephone"], "Telefono", required=True
    )
    if condition is not True:
        message.append(condition)

    condition = validate(
        request.form["date_birth"], "Fecha de Nacimiento", required=True
    )
    if condition is not True:
        message.append(condition)
    
    if valid_mail is True and not User.valid_email(request.form["email"]):
        message.append(
            "Ya existe un usuario con ese email, por favor\
            ingrese uno nuevo"
        )

    if message:
        for mssg in message:
            flash(mssg)
        return render_template("user/new.html")

    User.create_pacient(**request.form)
    return redirect(url_for("user_index"))


'''@login_required
@has_permission("user_activate")
def activate(user_id, activate):
    if activate == "1":
        activate = True
    else:
        activate = False
    usuario = User.activate(user_id, activate)
    return redirect(url_for("user_index"))'''

@login_required
@has_permission("user_edit")
def edit(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    return render_template("user/update.html", user=user)


@login_required
@has_permission("user_update")
def update():
    message = []
    condition = validate(request.form["first_name"], "Nombre", required=True, text=True)
    if condition is not True:
        message.append(condition)
    
    condition = validate(
        request.form["last_name"], "Apellido", required=True, text=True
    )
    if condition is not True:
        message.append(condition)

    if message:
        for mssg in message:
            flash(mssg)
        return render_template("user/update.html", user=request.form)

    User.update(user_id=request.form["id"], kwargs=request.form)
    return redirect(url_for("user_index"))


@login_required
@has_permission("user_index")
def search():
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
    )


@login_required
def profile():
    user = User.search_user_by_id(session["user_id"])
    return render_template("user/profile.html", user=user)


def is_admin(user_id):
    consulta = User.get_role(user_id)
    return (consulta==1)

def is_pacient(user_id):
    consulta = User.get_role(user_id)
    return (consulta==2)

def is_nurse(user_id):
    consulta = User.get_role(user_id)
    return (consulta==3)
