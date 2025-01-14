from flask import Blueprint, render_template
from sqlalchemy.exc import SQLAlchemyError

from src.extensions import logger
from config.settings import (
    TEMPLATE
)

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(error):
    logger.error(f"[SQL] ERROR HANDLER: {error}")
    return render_template(TEMPLATE.ERROR_500), 500


@errors_bp.app_errorhandler(400)
def bad_request(error):
    return render_template(TEMPLATE.E_400, error_msg=error.description), 400


@errors_bp.app_errorhandler(401)
def unauthorized(error):
    logger.debug(f"[DEBUG] Unauthorized error: {error}")
    return render_template(TEMPLATE.E_401, error_msg=error.description), 401


@errors_bp.app_errorhandler(403)
def forbidden(error):
    return render_template(TEMPLATE.E_403, error_msg=error.description), 403


@errors_bp.app_errorhandler(404)
def not_found(error):
    return render_template(TEMPLATE.E_404, error_msg=error.description), 404


@errors_bp.app_errorhandler(500)
def internal_server_error(error):
    return render_template(TEMPLATE.E_500, error_msg=error.description), 500
