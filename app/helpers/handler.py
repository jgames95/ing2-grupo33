from flask import render_template, request, jsonify


def not_found_error(e):
    kwargs = {
        "error_name": "404 Not Found Error",
        "error_description": "La url a la que quiere acceder no existe",
    }
    return make_response(kwargs, 404)


def unauthorized_error(e):
    kwargs = {
        "error_name": "401 Unauthorized Error",
        "error_description": "No está autorizado para acceder a la url",
    }
    return make_response(kwargs, 401)


def internal_server_error(e):
    kwargs = {
        "error_name": "500 Internal Server Error",
        "error_description": " Oops! Algo ha ido mal en el servidor",
    }
    return make_response(kwargs, 500)


def bad_request(e):
    kwargs = {
        "error_name": "400 Bad Request",
        "error_description": "El servidor no puede procesar la solicitud debido a error externo",
    }
    return make_response(kwargs, 400)


def make_response(data, code):
    if request.path.startswith("/api/"):
        return jsonify(data)
    else:
        return render_template("error.html", **data), code
