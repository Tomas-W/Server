from flask import (
    Blueprint,
    render_template,
)
from sqlalchemy.exc import SQLAlchemyError

from src.extensions import logger

from config.settings import (
    TEMPLATE,
)
from .error_route_utils import (
    Abort400,
    Abort401,
    Abort403,
    Abort404,
    Abort500
)

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(error):
    logger.error(f"[SQL] ERROR HANDLER: {error}")
    return render_template(TEMPLATE.ERROR_500), 500


@errors_bp.app_errorhandler(Abort400)
@errors_bp.app_errorhandler(400)
def bad_request(error):
    go_to = getattr(error, "go_to", None)
    return render_template(TEMPLATE.E_400, error_msg=error.description, go_to=go_to), 400


@errors_bp.app_errorhandler(Abort401)
@errors_bp.app_errorhandler(401)
def unauthorized(error):
    go_to = getattr(error, "go_to", None)
    return render_template(TEMPLATE.E_401, error_msg=error.description, go_to=go_to), 401


@errors_bp.app_errorhandler(Abort403)
@errors_bp.app_errorhandler(403)
def forbidden(error):
    go_to = getattr(error, "go_to", None)
    return render_template(TEMPLATE.E_403, error_msg=error.description, go_to=go_to), 403


@errors_bp.app_errorhandler(Abort404)
@errors_bp.app_errorhandler(404)
def not_found(error):
    go_to = getattr(error, "go_to", None)
    return render_template(TEMPLATE.E_404, error_msg=error.description, go_to=go_to), 404


@errors_bp.app_errorhandler(Abort500)
@errors_bp.app_errorhandler(500)
def internal_server_error(error):
    go_to = getattr(error, "go_to", None)
    return render_template(TEMPLATE.E_500, error_msg=error.description, go_to=go_to), 500
