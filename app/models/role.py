from app.db import db


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.relationship(
        "Permission", secondary="roles_permissions", lazy="dynamic"
    )

    @classmethod
    def has_permissions(cls, id_rol, permiso):
        has_permissions = (
            Role.query.filter_by(id=id_rol)
            .first()
            .permissions.filter_by(name=permiso)
            .first()
        )
        return has_permissions


class RolesPermissions(db.Model):
    __tablename__ = "roles_permissions"
    id = db.Column(db.Integer(), primary_key=True)
    role_id = db.Column(db.Integer(), db.ForeignKey("roles.id", ondelete="CASCADE"))
    permission_id = db.Column(
        db.Integer(), db.ForeignKey("permissions.id", ondelete="CASCADE")
    )
