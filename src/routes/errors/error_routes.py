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
    Abort500,
    get_error_params,
)

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(error):
    logger.exception(f"[SQL] ERROR HANDLER: {error}")
    return render_template(
        TEMPLATE.E_500
        ), 500


@errors_bp.app_errorhandler(Abort400)
@errors_bp.app_errorhandler(400)
def bad_request(error):
    error_msg, go_to, extra_info = get_error_params(error)
    return render_template(
        TEMPLATE.E_400,
        error_msg=error_msg,
        go_to=go_to,
        extra_info=extra_info,
    ), 400


@errors_bp.app_errorhandler(Abort401)
@errors_bp.app_errorhandler(401)
def unauthorized(error):
    error_msg, go_to, extra_info = get_error_params(error)
    return render_template(
        TEMPLATE.E_401,
        error_msg=error_msg,
        go_to=go_to,
        extra_info=extra_info,
    ), 401


@errors_bp.app_errorhandler(Abort403)
@errors_bp.app_errorhandler(403)
def forbidden(error):
    error_msg, go_to, extra_info = get_error_params(error)
    return render_template(
        TEMPLATE.E_403,
        error_msg=error_msg,
        go_to=go_to,
        extra_info=extra_info,
    ), 403


@errors_bp.app_errorhandler(Abort404)
@errors_bp.app_errorhandler(404)
def not_found(error):
    error_msg, go_to, extra_info = get_error_params(error)
    return render_template(
        TEMPLATE.E_404,
        error_msg=error_msg,
        go_to=go_to,
        extra_info=extra_info,
    ), 404


@errors_bp.app_errorhandler(Abort500)
@errors_bp.app_errorhandler(500)
def internal_server_error(error):
    error_msg, go_to, extra_info = get_error_params(error)
    logger.exception(f"[500] ERROR HANDLER: {error}")
    return render_template(
        TEMPLATE.E_500,
        error_msg=error_msg,
        go_to=go_to,
        extra_info=extra_info,
    ), 500
