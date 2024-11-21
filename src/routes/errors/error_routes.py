from flask import Blueprint, render_template
from sqlalchemy.exc import SQLAlchemyError

from src.extensions import logger, server_db_
from config.settings import (
    E_400_TEMPLATE, E_401_TEMPLATE, E_403_TEMPLATE, E_404_TEMPLATE,
    E_500_TEMPLATE
)

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(error):
    log_errors, html_errors = logger.get_errors(error)
    server_db_.session.rollback()
    logger.log.critical(log_errors)
    return render_template(E_500_TEMPLATE, errors=html_errors), 500


@errors_bp.app_errorhandler(400)
def bad_request(error):
    log_errors, html_errors = logger.get_errors(error)
    info = logger.get_user_info()
    logger.log.warning(log_errors)
    return render_template(E_400_TEMPLATE, info=info, errors=html_errors), 400


@errors_bp.app_errorhandler(401)
def unauthorized(error):
    log_errors, html_errors = logger.get_errors(error)
    info = logger.get_user_info()
    logger.log.warning(log_errors)
    return render_template(E_401_TEMPLATE, info=info, errors=html_errors), 401


@errors_bp.app_errorhandler(403)
def forbidden(error):
    log_errors, html_errors = logger.get_errors(error)
    info = logger.get_user_info()
    logger.log.warning(log_errors)
    return render_template(E_403_TEMPLATE, info=info, errors=html_errors), 403


@errors_bp.app_errorhandler(404)
def not_found(error):
    log_errors, html_errors = logger.get_errors(error)
    info = logger.get_user_info()
    logger.log.warning(log_errors)
    return render_template(E_404_TEMPLATE, info=info, errors=html_errors), 404


@errors_bp.app_errorhandler(500)
def internal_server_error(error):
    log_errors, html_errors = logger.get_errors(error)
    info = logger.get_user_info()
    logger.log.warning(log_errors)
    return render_template(E_500_TEMPLATE, info=info, errors=html_errors), 500
