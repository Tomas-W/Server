from __future__ import annotations

import os
import time

from flask import (
    abort,
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

from src.extensions import (
    logger,
    mail_,
    serializer_,
    server_db_,
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
    Decorator for Admin-only routes.
    Redirects to ALL_NEWS_REDIRECT if User has no admin role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.has_role(SERVER.ADMIN_ROLE):
            logger.warning(f"[AUTH] ADMIN ACCESS DENIED: {current_user.username}")
            description = f"This page requires Admin access."
            abort(401, description=description)
        return f(*args, **kwargs)
    return decorated_function


def employee_required(f: Callable) -> Callable:
    """
    Decorator for Employee-only routes.
    Redirects to USER_ADMIN_REDIRECT if User has no employee role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.has_role(SERVER.EMPLOYEE_ROLE):
            logger.warning(f"[AUTH] EMPLOYEE ACCESS DENIED: {current_user.username}.")
            description = f"This page requires Employee access."
            abort(401, description=description)
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
            time.sleep(0.3)  # TODO: remove delay
            return False

    token = get_authentication_token(email, token_type)
    reset_authentication_token(token_type, token, email)
    send_authentication_email(email, token_type, token)
    return True


def get_authentication_token(email: str, token_type: str) -> str:
    salt = os.environ.get(f"{token_type.upper()}_SALT")
    if not salt:
        logger.critical(f"[VALIDATION] SALT NOT FOUND for token: {token_type}")
        abort(500)
    token = serializer_.dumps(email, salt=salt)
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
        abort(500)

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
        sender=SERVER.EMAIL,
        recipients=[email],
        html=html_body
    )
    send_email(message)


def get_authentication_url(endpoint: str, **values: Any) -> str:
    try:
        return url_for(endpoint, **values)
    except (BuildError, KeyError, ValueError) as e:
        logger.error(f"[VALIDATION] ERROR GENERATING URL: {e}")
        abort(500)


def get_authentication_email_template(template_name: str, **context: Any) -> str:
    try:
        return render_template(template_name, **context)
    except (TemplateNotFound, TemplateSyntaxError, UndefinedError) as e:
        logger.error(f"[VALIDATION] ERROR RENDERING EMAIL TEMPLATE: {e}")
        abort(500)


def send_email(message: Message) -> None:
    try:
        mail_.send(message)
    except SMTPRecipientsRefused as e:
        logger.info(f"[VALIDATION] RECIPIENTS REFUSED: {e}")
        abort(500)
    except SMTPSenderRefused as e:
        logger.critical(f"[VALIDATION] SENDER REFUSED: {e}")
        abort(500)
    except Exception as e:
        logger.error(f"[VALIDATION] ERROR SENDING VERIFICATION: {e}")
        abort(500)

def confirm_authentication_token(token: str, token_type: str,
                                 expiration: int = SERVER.TOKEN_EXPIRATION) -> str | None:
    """
    Confirm the specified authentication token.
    Verifications:
    - EMAIL_VERIFICATION [set email verified | set new email]
    - PASSWORD_VERIFICATION [reset password]
    """
    from src.models.auth_model.auth_mod import AuthenticationToken
    salt = os.environ.get(f"{token_type.upper()}_SALT")
    if not salt:
        logger.critical(f"[VALIDATION] SALT NOT FOUND for token: {token_type}")
        abort(500)

    try:
        email = serializer_.loads(
            token,
            salt=salt,
            max_age=expiration
        )
        stmt = select(AuthenticationToken).filter_by(
            user_email=email,
            token_type=token_type
        )
        stored_token = server_db_.session.execute(stmt).scalar_one_or_none()

        if stored_token and stored_token.token == token:
            return email

        else:
            logger.info(f"[VALIDATION] EMAIL TOKEN NOT CONFIRMED: {email}")
            return None

    except (SignatureExpired, BadSignature) as e:
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
            email=SERVER.EMAIL,
            username=os.environ.get("ADMIN_UNAME"),
            password=os.environ.get("ADMIN_PWD"),
            fast_name=os.environ.get("ADMIN_F_NAME"),
            fast_code=os.environ.get("ADMIN_F_CODE"),
            display_name=os.environ.get("ADMIN_DISPLAY_NAME"),
            email_verified=True,
            employee_name=os.environ.get("ADMIN_EMPLOYEE_NAME"),
            roles=os.environ.get("ADMIN_ROLES").split(",")
        )
        deleted_user = User(
            email=os.environ.get("DELETED_USER_EMAIL"),
            username=os.environ.get("DELETED_USER_UNAME"),
            password=os.environ.get("DELETED_USER_PWD"),
            display_name=os.environ.get("DELETED_USER_DISPLAY_NAME"),
        )
        server_db_.session.add(new_user)
        server_db_.session.add(deleted_user)
        server_db_.session.commit()
        return new_user.cli_repr()

    return False
