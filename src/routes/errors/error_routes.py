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
    logger.error(f"[SQL] ERROR HANDLER: {error}")
    return render_template(E_500_TEMPLATE), 500


@errors_bp.app_errorhandler(400)
def bad_request(error):
    return render_template(E_400_TEMPLATE, error_msg=error.description), 400


@errors_bp.app_errorhandler(401)
def unauthorized(error):
    logger.debug(f"[DEBUG] Unauthorized error: {error}")
    return render_template(E_401_TEMPLATE, error_msg=error.description), 401


@errors_bp.app_errorhandler(403)
def forbidden(error):
    return render_template(E_403_TEMPLATE, error_msg=error.description), 403


@errors_bp.app_errorhandler(404)
def not_found(error):
    return render_template(E_404_TEMPLATE, error_msg=error.description), 404


@errors_bp.app_errorhandler(500)
def internal_server_error(error):
    return render_template(E_500_TEMPLATE, error_msg=error.description), 500
