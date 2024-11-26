from __future__ import annotations
import os
import time
from typing import Any
from functools import wraps
from typing import Callable, TYPE_CHECKING
from flask import url_for, render_template, request, session, abort
from flask_login import current_user
from flask_mail import Message
from itsdangerous import SignatureExpired, BadSignature
from sqlalchemy import select, or_, delete
from werkzeug.routing import BuildError
from jinja2 import TemplateNotFound, TemplateSyntaxError, UndefinedError
from smtplib import SMTPRecipientsRefused, SMTPSenderRefused

from config.settings import (
    PASSWORD_VERIFICATION, EMAIL_VERIFICATION, ADMIN_ROLE,
    RESET_PASSWORD_REDIRECT, VERIFY_EMAIL_REDIRECT, USER_ADMIN_REDIRECT,
    GMAIL_EMAIL, EMAIL_TEMPLATE, TOKEN_EXPIRATION
)
from src.extensions import server_db_, serializer_, mail_, logger

if TYPE_CHECKING:
    from src.models.auth_model.auth_mod import User


def admin_required(f: Callable) -> Callable:
    """
    Decorator for admin-only routes.
    Redirects to ALL_NEWS_REDIRECT if User has no admin role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.has_role(ADMIN_ROLE):
            session["log_trigger"] = "admin_required"
            abort(401)
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
            errors = f"User not found - {logger.get_log_info()}"
            logger.log.info(errors)
            time.sleep(0.3)  # TODO: remove delay
            return False

    token = get_authentication_token(email, token_type)
    reset_authentication_token(token_type, token, email)
    send_authentication_email(email, token_type, token)
    return True


def get_authentication_token(email: str, token_type: str) -> str:
    salt = os.environ.get(f"{token_type.upper()}_SALT")
    if not salt:
        session["error_msg"] = f"Salt not found for: {token_type=}"
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
    if token_type == EMAIL_VERIFICATION:
        url_ = VERIFY_EMAIL_REDIRECT
        subject = "Email Verification"
        redirect_title = "To verify your email, "
    elif token_type == PASSWORD_VERIFICATION:
        url_ = RESET_PASSWORD_REDIRECT
        subject = "Password Reset"
        redirect_title = "To reset your password, "
    else:
        session["error_msg"] = f"Wrong token_type: {token_type}"
        abort(500)

    redirect_url = get_authentication_url(url_, token=token, _external=True)
    settings_url = get_authentication_url(USER_ADMIN_REDIRECT,
                                          _external=True,
                                          _anchor="notifications-wrapper")

    html_body = get_authentication_email_template(
        template_name=EMAIL_TEMPLATE,
        title=subject,
        redirect_title=redirect_title,
        redirect_url=redirect_url,
        notification_settings="You can change your notification settings below.",
        settings_url=settings_url
    )

    message = Message(
        subject=subject,
        sender=GMAIL_EMAIL,
        recipients=[email],
        html=html_body
    )
    send_email(message)


def get_authentication_url(endpoint: str, **values: Any) -> str:
    try:
        return url_for(endpoint, **values)
    except (BuildError, KeyError, ValueError) as e:
        session["error_msg"] = f"Error generating url_for: {e}"
        abort(500)


def get_authentication_email_template(template_name: str, **context: Any) -> str:
    try:
        return render_template(template_name, **context)
    except (TemplateNotFound, TemplateSyntaxError, UndefinedError) as e:
        session["error_msg"] = f"Error rendering email template: {e}"
        abort(500)


def send_email(message: Message) -> None:
    try:
        mail_.send(message)
    except SMTPRecipientsRefused as e:
        session["error_msg"] = f"Recipients refused: {e}"
        abort(500)
    except SMTPSenderRefused as e:
        session["error_msg"] = f"Sender refused: {e}"
        abort(500)
    except Exception as e:
        session["error_msg"] = f"Error sending verification: {e}"
        abort(500)

def confirm_authentication_token(token: str, token_type: str,
                                 expiration: int = TOKEN_EXPIRATION) -> str | None:
    """
    Confirm the specified authentication token.
    Verifications:
    - EMAIL_VERIFICATION [set email verified | set new email]
    - PASSWORD_VERIFICATION [reset password]
    """
    from src.models.auth_model.auth_mod import AuthenticationToken
    salt = os.environ.get(f"{token_type.upper()}_SALT")
    if not salt:
        session["error_msg"] = f"Salt not found for: {token_type}"
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
            errors = f"Email token not confirmed - {logger.get_log_info()}"
            logger.log.warning(errors)
            return None

    except (SignatureExpired, BadSignature) as e:
        errors = f"Email token expired: {e} - {logger.get_log_info()}"
        logger.log.warning(errors)
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


def delete_user_by_id(id_: int) -> None:
    """Delete a user by id. Used in cli."""
    from src.models.auth_model.auth_mod import User
    stmt = delete(User).filter_by(id=id_)
    server_db_.session.execute(stmt)
    server_db_.session.commit()


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
    return new_user


def _init_user() -> str | None:
    """
    Initializer function for cli.
    No internal use.
    """
    if not server_db_.session.query(User).count():
        new_user = User(
            email="100pythoncourse@gmail.com",
            username="100python",
            password="TomasTomas1!",
            fast_name="tomas",
            fast_code=("00000"),
            email_verified=True,
            roles="admin"
        )
        delete_user = User(
            email="deleted@user.com",
            username="Deleted user",
            password="TomasTomas1!",
            display_name="Deleted user",
        )
        server_db_.session.add(new_user)
        server_db_.session.add(delete_user)
        server_db_.session.commit()
        return repr(new_user)

    return None
