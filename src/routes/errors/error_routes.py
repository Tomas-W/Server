from flask import Blueprint, render_template

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(400)
def bad_request(error):
    return render_template("errors/400.html"), 400


@errors_bp.app_errorhandler(401)
def unauthorized(error):
    return render_template("errors/401.html"), 401


@errors_bp.app_errorhandler(403)
def forbidden(error):
    return render_template("errors/403.html"), 403


@errors_bp.app_errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404


@errors_bp.app_errorhandler(500)
def internal_server_error(error):
    return render_template("errors/500.html"), 500
