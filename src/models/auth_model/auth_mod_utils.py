from __future__ import annotations

import os
import time

from flask import (
    current_app,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user
from flask_mail import Message
from functools import wraps
from itsdangerous import (
    BadSignature,
    SignatureExpired,
)
from jinja2 import (
    TemplateNotFound,
    TemplateSyntaxError,
    UndefinedError,
)
from smtplib import (
    SMTPRecipientsRefused,
    SMTPSenderRefused,
)
from sqlalchemy import (
    delete,
    or_,
    select,
)
from typing import Any, Callable, TYPE_CHECKING
from werkzeug.routing import BuildError
from hmac import compare_digest

from src.extensions import (
    mail_,
    get_serializer,
    server_db_,
    logger,
)

from src.routes.errors.error_route_utils import (
    Abort401,
    Abort500
)

from config.settings import (
    REDIRECT,
    SERVER,
    TEMPLATE
)

if TYPE_CHECKING:
    from src.models.auth_model.auth_mod import User


def admin_required(f: Callable) -> Callable:
    """
    Calls custom 401 error if User has no Admin role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.has_role(SERVER.ADMIN_ROLE):
            logger.warning(f"[AUTH] ADMIN ACCESS DENIED: {current_user.username}")
            description = f"This page requires Admin access."
            raise Abort401(description=description)
        
        return f(*args, **kwargs)
    return decorated_function


def employee_required(f: Callable) -> Callable:
    """
    Calls custom 401 error if User has no Employee role.
    Has redirect to User admin page to request access.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        
        if not current_user.has_role(SERVER.EMPLOYEE_ROLE):
            go_route = url_for(REDIRECT.USER_ADMIN, _anchor="access-wrapper")
            description = f"This page requires Employee access."
            raise Abort401(description=description, go_to=go_route)
        
        return f(*args, **kwargs)
    return decorated_function


def start_verification_process(email: str, token_type: str,
                               allow_unknown: bool = False) -> bool:
    """
    Generates a token, resets it in the database and sends an email with a
    verification link and instructions.
    - allow_unknown: if True, do not check if the user exists (for email verification)
    """
    if not allow_unknown:
        user = get_user_by_email(email)
        if not user:
            time.sleep(0.3)  # TODO: remove delay mimicking a slow response
            return False

    token = get_authentication_token(email, token_type)
    reset_authentication_token(token_type, token, email)
    send_authentication_email(email, token_type, token)
    return True


def get_authentication_token(email: str, token_type: str) -> str:
    salt_map = {
        SERVER.EMAIL_VERIFICATION: current_app.ENV.EMAIL_VERIFICATION_SALT.get_secret_value(),
        SERVER.PASSWORD_VERIFICATION: current_app.ENV.PASSWORD_VERIFICATION_SALT.get_secret_value(),
        SERVER.EMPLOYEE_VERIFICATION: current_app.ENV.EMPLOYEE_VERIFICATION_SALT.get_secret_value(),
    }
    salt = salt_map.get(token_type)
    if not salt:
        logger.critical(f"[VALIDATION] SALT NOT FOUND for token: {token_type}")
        raise Abort500()
    token = get_serializer().dumps(email, salt=salt)
    return token


def reset_authentication_token(token_type: str, token: str, email: str) -> None:
    """
    Reset the specified authentication token.
    If an old token exists, overwrite it, else create a new one.
    """
    from src.models.auth_model.auth_mod import AuthenticationToken
    stmt = select(AuthenticationToken).filter_by(
        user_email=email,
        token_type=token_type
    )
    existing_token = server_db_.session.execute(stmt).scalar_one_or_none()

    if existing_token:
        existing_token.set_token(token)
    else:
        new_token = AuthenticationToken(user_email=email,
                                        token_type=token_type, token=token)
        server_db_.session.add(new_token)
        server_db_.session.commit()


def send_authentication_email(email: str, token_type: str, token: str) -> None:
    """
    Send an email with a authentication link and instructions.
    Verification [token] types:
    - EMAIL_VERIFICATION [set email verified]
    - PASSWORD_VERIFICATION [reset password]
    """
    if token_type == SERVER.EMAIL_VERIFICATION:
        url_ = REDIRECT.VERIFY_EMAIL
        subject = "Email Verification"
        redirect_title = "To verify your email, "
        _anchor = "notifications-wrapper"
    elif token_type == SERVER.PASSWORD_VERIFICATION:
        url_ = REDIRECT.RESET_PASSWORD
        subject = "Password Reset"
        redirect_title = "To reset your password, "
        _anchor = "notifications-wrapper"
    elif token_type == SERVER.EMPLOYEE_VERIFICATION:
        url_ = REDIRECT.VERIFY_EMPLOYEE
        subject = "Employee Verification"
        redirect_title = "To verify your employee account, "
        _anchor = "schedule-wrapper"
    else:
        logger.error(f"[VALIDATION] WRONG TOKEN TYPE: {token_type}")
        raise Abort500()

    redirect_url = get_authentication_url(url_, token=token, _external=True)
    settings_url = get_authentication_url(REDIRECT.USER_ADMIN,
                                          _external=True,
                                          _anchor=_anchor)

    html_body = get_authentication_email_template(
        template_name=TEMPLATE.EMAIL,
        title=subject,
        redirect_title=redirect_title,
        redirect_url=redirect_url,
        notification_settings="You can change your notification settings below.",
        settings_url=settings_url
    )

    message = Message(
        subject=subject,
        sender=current_app.ENV.GMAIL_EMAIL.get_secret_value(),
        recipients=[email],
        html=html_body
    )
    send_email(message)


def get_authentication_url(endpoint: str, **values: Any) -> str:
    try:
        return url_for(endpoint, **values)
    except (BuildError, KeyError, ValueError):
        logger.exception("[VALIDATION] ERROR GENERATING URL")
        raise Abort500()


def get_authentication_email_template(template_name: str, **context: Any) -> str:
    try:
        return render_template(template_name, **context)
    except (TemplateNotFound, TemplateSyntaxError, UndefinedError) as e:
        logger.exception("[VALIDATION] ERROR RENDERING EMAIL TEMPLATE")
        raise Abort500()


def send_email(message: Message) -> None:
    try:
        mail_.send(message)
    except SMTPRecipientsRefused:
        logger.exception("[VALIDATION] RECIPIENTS REFUSED")
        raise Abort500()
    except SMTPSenderRefused:
        logger.exception("[VALIDATION] SENDER REFUSED")
        raise Abort500()
    except Exception:
        logger.exception("[VALIDATION] ERROR SENDING VERIFICATION")
        raise Abort500()

def confirm_authentication_token(token: str, token_type: str,
                                 expiration: int = SERVER.TOKEN_EXPIRATION) -> str | None:
    """
    Confirm the specified authentication token.
    Verifications:
    - EMAIL_VERIFICATION [set email verified | set new email]
    - PASSWORD_VERIFICATION [reset password]
    """
    from src.models.auth_model.auth_mod import AuthenticationToken
    salt_map = {
        SERVER.EMAIL_VERIFICATION: current_app.ENV.EMAIL_VERIFICATION_SALT.get_secret_value(),
        SERVER.PASSWORD_VERIFICATION: current_app.ENV.PASSWORD_VERIFICATION_SALT.get_secret_value(),
        SERVER.EMPLOYEE_VERIFICATION: current_app.ENV.EMPLOYEE_VERIFICATION_SALT.get_secret_value(),
    }
    salt = salt_map.get(token_type)
    if not salt:
        logger.critical(f"[VALIDATION] SALT NOT FOUND for token: {token_type}")
        raise Abort500()

    try:
        email = get_serializer().loads(
            token,
            salt=salt,
            max_age=expiration
        )
        stmt = select(AuthenticationToken).filter_by(
            user_email=email,
            token_type=token_type
        )
        stored_token = server_db_.session.execute(stmt).scalar_one_or_none()

        if stored_token and compare_digest(stored_token.token, token):
            return email

        else:
            return None

    except (SignatureExpired, BadSignature):
        return None


def delete_authentication_token(token_type: str, token: str) -> None:
    """Delete the specified authentication token."""
    from src.models.auth_model.auth_mod import AuthenticationToken
    stmt = delete(AuthenticationToken).filter_by(
        token_type=token_type,
        token=token
    )
    server_db_.session.execute(stmt)
    server_db_.session.commit()


def get_user_by_email(email: str, new_email: bool = False) -> "User" | None:
    """
    Get a user by email.
    If new_email is True, check if the user exists by new_email.
    """
    from src.models.auth_model.auth_mod import User
    stmt = select(User).filter_by(email=email)
    result = server_db_.session.execute(stmt).scalar_one_or_none()
    if result is None and new_email:
        result = server_db_.session.execute(
            select(User).filter_by(new_email=email)
        ).scalar_one_or_none()
    return result


def get_user_by_username(username: str) -> "User" | None:
    from src.models.auth_model.auth_mod import User
    stmt = select(User).filter_by(username=username)
    return server_db_.session.execute(stmt).scalar_one_or_none()


def get_user_by_email_or_username(email_or_username: str) -> "User" | None:
    from src.models.auth_model.auth_mod import User
    stmt = select(User).filter(
            or_(User.email == email_or_username,
                User.username == email_or_username)
        )
    return server_db_.session.execute(stmt).scalar_one_or_none()


def get_user_by_display_name(display_name: str) -> "User" | None:
    from src.models.auth_model.auth_mod import User
    stmt = select(User).filter_by(display_name=display_name)
    return server_db_.session.execute(stmt).scalar_one_or_none()


def get_user_by_fast_name(fast_name: str) -> "User" | None:
    from src.models.auth_model.auth_mod import User
    stmt = select(User).filter_by(fast_name=fast_name)
    return server_db_.session.execute(stmt).scalar_one_or_none()


def get_user_by_employee_name(employee_name: str) -> "User" | None:
    from src.models.auth_model.auth_mod import User
    stmt = select(User).filter_by(employee_name=employee_name)
    return server_db_.session.execute(stmt).scalar_one_or_none()


def update_employee_name(id_: int, employee_name: str) -> None:
    """
    Set the employee_name for a User by id. Used in cli.
    """
    from src.models.auth_model.auth_mod import User
    user = server_db_.session.get(User, id_)
    user.set_employee_name(employee_name)
    server_db_.session.commit()
    

def delete_user_by_id(id_: int, cli: bool = False) -> None:
    """Delete a user by id. Used in cli."""
    from src.models.auth_model.auth_mod import User
    stmt = delete(User).filter_by(id=id_)
    server_db_.session.execute(stmt)
    server_db_.session.commit()
    if not cli:
        logger.warning(f"[DEL] DELETE USER: {id_} DELETED")


def get_new_user(email: str, username: str, password: str) -> "User" | None:
    # noinspection PyArgumentList
    from src.models.auth_model.auth_mod import User
    new_user = User(
        email=email,
        username=username,
        password=password,
    )
    server_db_.session.add(new_user)
    server_db_.session.commit()
    logger.info(f"[ADD] USER CREATED: {new_user.username}")
    return new_user


def _init_user() -> str | bool:
    """
    Initializer function for cli.
    No internal use.
    """
    from src.models.auth_model.auth_mod import User
    if not server_db_.session.query(User).count():
        new_user = User(
            email=current_app.ENV.GMAIL_EMAIL.get_secret_value(),
            username=current_app.ENV.ADMIN_UNAME,
            password=current_app.ENV.ADMIN_PWD.get_secret_value(),
            fast_name=current_app.ENV.ADMIN_F_NAME.get_secret_value(),
            fast_code=current_app.ENV.ADMIN_F_CODE.get_secret_value(),
            display_name=current_app.ENV.ADMIN_DISPLAY_NAME,
            email_verified=True,
            employee_name=current_app.ENV.ADMIN_EMPLOYEE_NAME.get_secret_value(),
            roles=current_app.ENV.ADMIN_ROLES.split(",")
        )
        deleted_user = User(
            email=current_app.ENV.DELETED_USER_EMAIL,
            username=current_app.ENV.DELETED_USER_UNAME,
            password=current_app.ENV.DELETED_USER_PWD.get_secret_value(),
            display_name="Deleted user",
        )
        server_db_.session.add(new_user)
        server_db_.session.add(deleted_user)
        server_db_.session.commit()
        return new_user.cli_repr()

    return False
