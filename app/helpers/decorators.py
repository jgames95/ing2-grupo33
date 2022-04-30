from flask import abort, session
from app.models.user import User


def login_required(view_function):
    """Si no esta logueado  muestra el error 401.
    Si esta logueado sigue con la ejecucion del programa
    """
    #  Agregar como decorador de cada funcion que necesitemos que el
    #  usuario este logueado
    #  importarla con  from app.helpers.decorators import login_required
    def decorator(*args, **kwargs):
        if not session.get("user_id"):
            # Redirect to unauthenticated page
            return abort(401)

        return view_function(*args, **kwargs)

    return decorator


def has_permission(permiso):
    """
    Si el usuario tiene el permiso para acceder a esa funcionalidad  y esta]
    activo, sigue con la ejecucion, sino muestra el error 401
    """

    def wrapper(view_function):

        # funcion envoltura
        def decorator(*args, **kwargs):
            if not User.has_permission(session.get("user_id"), permiso):
                return abort(401)
            return view_function(*args, **kwargs)

        return decorator

    return wrapper
