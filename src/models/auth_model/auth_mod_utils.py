from __future__ import annotations

import os
import time
from functools import wraps
from typing import Callable, TYPE_CHECKING
from flask import url_for, render_template, redirect, flash, request
from flask_login import current_user
from flask_mail import Message
from itsdangerous import SignatureExpired, BadSignature
from sqlalchemy import select, or_, delete
from smtplib import SMTPRecipientsRefused

from config.settings import (
    PASSWORD_VERIFICATION, EMAIL_VERIFICATION, NOT_AUTHORIZED_MSG, ADMIN_ROLE,
    ALL_NEWS_REDIRECT, RESET_PASSWORD_REDIRECT, VERIFY_EMAIL_REDIRECT,
    USER_ADMIN_REDIRECT, GMAIL_EMAIL, EMAIL_TEMPLATE, TOKEN_EXPIRATION,
    E_500_REDIRECT
)
from src.extensions import server_db_, serializer_, mail_, logger
from src.utils.logger import log_routes, log_function

if TYPE_CHECKING:
    from src.models.auth_model.auth_mod import User

def admin_required(f: Callable) -> Callable:
    """
    Decorator for admin-only routes.
    Redirects to news.all_news if User is not authenticated or has no admin role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_role(ADMIN_ROLE):
            flash(NOT_AUTHORIZED_MSG)
            logger.warning(f"@admin_required failed {log_routes()}")
            return redirect(url_for(ALL_NEWS_REDIRECT))
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
            logger.info(f"User not found {log_function()} {log_routes()}")
            time.sleep(0.3)  # TODO: remove delay
            return False

    token = get_authentication_token(email, token_type)
    reset_authentication_token(token_type, token, email)
    send_authentication_email(email, token_type, token)
    return True


def get_authentication_token(email: str, token_type: str) -> str:
    salt = os.environ.get(f"{token_type.upper()}_SALT")
    if not salt:
        errors = f"Salt not found for: {token_type}", log_function(), log_routes()
        logger.critical(errors)
        return url_for(E_500_REDIRECT, errors=errors)
    token = serializer_.dumps(email, salt=salt)
    return token


def reset_authentication_token(token_type: str, token: str, email: str) -> None:
    """
    Reset the specified authentication token.
    If an old token exists, overwrite it, else create a new one.
    """
    from src.models.auth_model.auth_mod import AuthenticationToken
    existing_token = server_db_.session.execute(
        select(AuthenticationToken).filter_by(
            user_email=email,
            token_type=token_type)).scalar_one_or_none()

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
        errors = f"Wrong token_type: {token_type}", log_function(), log_routes()
        logger.error(errors)
        return redirect(url_for(E_500_REDIRECT, errors=errors))

    try:
        verification_url = url_for(url_,
                                   token=token,
                                   _external=True)
        settings_url = url_for(USER_ADMIN_REDIRECT,
                               _anchor="notifications-wrapper",
                               _external=True)
    except Exception as e:
        errors = f"Error generating url_for: {e}", log_function(), log_routes()
        logger.error(errors)
        return redirect(url_for(E_500_REDIRECT, errors=errors))

    try:
        html_body = render_template(
            EMAIL_TEMPLATE,
        title=subject,
        redirect_title=redirect_title,
        redirect_url=verification_url,
        notification_settings="You can change your notification settings below.",
            settings_url=settings_url
        )
    except Exception as e:
        errors = f"Error rendering email template: {e}", log_function(), log_routes()
        logger.error(errors)
        return redirect(url_for(E_500_REDIRECT, errors=errors))

    message = Message(
        subject=subject,
        sender=GMAIL_EMAIL,
        recipients=[email],
        html=html_body
    )
    try:
        mail_.send(message)
    except SMTPRecipientsRefused as e:
        errors = f"Recipients refused: {e}", log_function(), log_routes()
        logger.error(errors)
        return redirect(url_for(E_500_REDIRECT, errors=errors))
    except Exception as e:
        errors = f"Error sending verification: {e}", log_function(), log_routes()
        logger.error(errors)
        return redirect(url_for(E_500_REDIRECT, errors=errors))


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
        errors = f"Salt not found for: {token_type}", log_function(), log_routes()
        logger.critical(errors)
        return url_for(E_500_REDIRECT, errors=errors)

    try:
        email = serializer_.loads(
            token,
            salt=salt,
            max_age=expiration
        )
        stored_token = server_db_.session.execute(
            select(AuthenticationToken).filter_by(
                user_email=email,
                token_type=token_type)).scalar_one_or_none()

        if stored_token and stored_token.token == token:
            return email

        else:
            errors = f"Email token not confirmed", log_function(), log_routes()
            logger.warning(errors)
            return None

    except (SignatureExpired, BadSignature) as e:
        errors = f"Email token expired: {e}", log_function(), log_routes()
        logger.warning(errors)
        return None


def delete_authentication_token(token_type: str, token: str) -> None:
    """Delete the specified authentication token."""
    from src.models.auth_model.auth_mod import AuthenticationToken
    server_db_.session.execute(
        delete(AuthenticationToken).filter_by(
            token_type=token_type,
            token=token))
    server_db_.session.commit()



def get_user_by_email(email: str, new_email: bool = False) -> "User" | None:
    """
    Get a user by email.
    If new_email is True, check if the user exists by new_email.
    """
    from src.models.auth_model.auth_mod import User
    result = server_db_.session.execute(
        select(User).filter_by(email=email)).scalar_one_or_none()
    if result is None and new_email:
        result = server_db_.session.execute(
            select(User).filter_by(new_email=email)
        ).scalar_one_or_none()
    return result


def get_user_by_username(username: str) -> "User" | None:
    from src.models.auth_model.auth_mod import User
    return server_db_.session.execute(
        select(User).filter_by(username=username)).scalar_one_or_none()


def get_user_by_email_or_username(email_or_username: str) -> "User" | None:
    from src.models.auth_model.auth_mod import User
    return server_db_.session.execute(
        select(User).filter(
            or_(User.email == email_or_username,
                User.username == email_or_username))).scalar_one_or_none()


def get_user_by_display_name(display_name: str) -> "User" | None:
    from src.models.auth_model.auth_mod import User
    return server_db_.session.execute(
        select(User).filter_by(display_name=display_name)).scalar_one_or_none()


def get_user_by_fast_name(fast_name: str) -> "User" | None:
    from src.models.auth_model.auth_mod import User
    return server_db_.session.execute(
        select(User).filter_by(fast_name=fast_name)).scalar_one_or_none()


def delete_user_by_id(id_: int) -> None:
    """Delete a user by id. Used in cli."""
    from src.models.auth_model.auth_mod import User
    server_db_.session.execute(delete(User).filter_by(id=id_))
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
        server_db_.session.add(new_user)
        server_db_.session.commit()
        return repr(new_user)

    return None
