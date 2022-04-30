from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    config_db(app)


def config_db(app):
    @app.before_first_request
    def init_database():
        '''from app.models.user import User
        from app.models.meeting_points import Meeting_point
        from app.models.configuration import Configuration
        from app.models.permission import Permission
        from app.models.role import Role
        from app.models.palette import Palette
        from app.models.flood_zone import FloodZone
        from app.models.issue import Issue
        from app.models.tracking import Tracking
        from app.models.evacuation_routes import Evacuation_route
        from app.models.category import Category
        from app.models.state import State'''

        db.create_all()

    @app.teardown_request
    def close_session(exception=None):
        db.session.remove()