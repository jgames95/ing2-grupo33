from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    config_db(app)


def config_db(app):
    @app.before_first_request
    def init_database():
        from app.models.role import Role
        from app.models.permission import Permission
        from app.models.appointment import Appointment
        from app.models.vaccine import Vaccine
        from app.models.user import User
        from app.models.state import State

        db.create_all()

    @app.teardown_request
    def close_session(exception=None):
        db.session.remove()