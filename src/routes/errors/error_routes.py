from flask import Blueprint, render_template
from flask import session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.extensions import logger, server_db_
from src.utils.logger import log_function, log_routes
from config.settings import (
    E_400_TEMPLATE, E_401_TEMPLATE, E_403_TEMPLATE, E_404_TEMPLATE,
    E_500_TEMPLATE
)

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(error):
    error_msg = str(error).split("\n")[0]
    errors = error_msg, log_function(), log_routes()
    server_db_.session.rollback()
    logger.critical(f"Database error: {errors}")
    return render_template(E_500_TEMPLATE, errors=errors), 500


@errors_bp.app_errorhandler(400)
def bad_request(error):
    logger.warning(f"Bad request: {error} {log_function()} {log_routes()}")
    return render_template(E_400_TEMPLATE), 400


@errors_bp.app_errorhandler(401)
def unauthorized(error):
    logger.warning(f"Unauthorized: {error} {log_function()} {log_routes()}")
    return render_template(E_401_TEMPLATE), 401


@errors_bp.app_errorhandler(403)
def forbidden(error):
    logger.warning(f"Forbidden: {error} {log_function()} {log_routes()}")
    return render_template(E_403_TEMPLATE), 403


@errors_bp.app_errorhandler(404)
def not_found(error):
    logger.warning(f"Not found: {error} {log_function()} {log_routes()}")
    info = session.pop("error_info", None)
    return render_template(E_404_TEMPLATE, info=info), 404


@errors_bp.app_errorhandler(500)
def internal_server_error(error):
    logger.warning(f"Internal server error: {error} {log_function()} {log_routes()}")
    return render_template(E_500_TEMPLATE), 500
