import os
from functools import wraps

from flask import url_for, render_template, redirect, flash, request
from flask_login import current_user
from flask_mail import Message
from itsdangerous import SignatureExpired, BadSignature
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError

from config.settings import (
    PASSWORD_VERIFICATION, EMAIL_VERIFICATION, NOT_AUTHORIZED_MSG
)
from src.extensions import server_db_, serializer_, mail_, logger
from src.models.auth_model.auth_mod import (
    User, AuthenticationToken
)
from src.utils.logger_config import get_logging_routes

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated \
                or "admin" not in current_user.roles.split("|"):
            flash(NOT_AUTHORIZED_MSG)
            logger.warning(f"@admin_required {get_logging_routes()}")
            return redirect(url_for("news.all_news"))
        return f(*args, **kwargs)
    return decorated_function


def process_verification_token(email: str, token_type: str,
                               allow_unknown: bool = False) -> bool:
    """
    Generate a token, reset it in the database, and send an email with a 
    verification link and instructions.
    allow_unknown: if True, do not check if the user exists (for email verification)
    """
    if not allow_unknown:
        user = get_user_by_email(email)
        if not user:
            # time.sleep(0.2)
            return False
    token = generate_authentication_token(email, token_type)
    reset_authentication_token(token_type, token, email)
    send_authentication_email(email, token_type, token)
    return True


def generate_authentication_token(email: str, token_type: str) -> str:
    token = serializer_.dumps(email, salt=os.environ.get(f"{token_type.upper()}_SALT"))
    return token


def reset_authentication_token(token_type: str, token: str, email: str) -> None:
    """
    Reset the specified authentication token.
    If no User with the given email exists, return False.
    If the token already exists, update it and return True.
    If the token does not exist, create a new one and return True.
    """
    id_ = get_user_by_email(email).id
    existing_token = server_db_.session.query(AuthenticationToken).filter_by(
        user_id=id_, token_type=token_type).first_or_none()
    if existing_token:
        existing_token.token = token
    else:
        new_token = AuthenticationToken(user_id=id_, user_email=email,
                                        token_type=token_type, token=token)
        server_db_.session.add(new_token)
        server_db_.session.commit()


def send_authentication_email(email: str, token_type: str, token: str) -> None:
    """
    Send an email with a authentication link and instructions.
    Verifications:
    - EMAIL_VERIFICATION [set email verified]
    - PASSWORD_VERIFICATION [reset password]
    """
    user: User | None = get_user_by_email(email)
    if not user:
        return

    if token_type == EMAIL_VERIFICATION:
        url_ = "admin.verify_email"
        subject = "Email Verification"
        redirect_title = "To verify your email, "
    elif token_type == PASSWORD_VERIFICATION:
        url_ = "auth.reset_password"
        subject = "Password Reset"
        redirect_title = "To reset your password, "
    else:
        raise ValueError(f"Invalid token type: {token_type}")

    verification_url = url_for(url_, token=token, _external=True)
    settings_url = url_for("admin.user_admin",
                           _anchor="notifications-wrapper",
                           _external=True)

    html_body = render_template(
        "admin/email.html",
        title=subject,
        redirect_title=redirect_title,
        redirect_url=verification_url,
        notification_settings="You can change your notification settings below.",
        settings_url=settings_url
    )

    message = Message(
        subject=subject,
        sender=os.environ.get("GMAIL_EMAIL"),
        recipients=[email],
        html=html_body
    )
    mail_.send(message)


def confirm_authentication_token(token: str, token_type: str,
                                 expiration: int = 3600) -> str | None:
    """
    Confirm the specified authentication token.
    Verifications:
    - EMAIL_VERIFICATION [set email verified | set new email]
    - PASSWORD_VERIFICATION [reset password]
    """
    try:
        email = serializer_.loads(
            token,
            salt=os.environ.get(f"{token_type.upper()}_SALT"),
            max_age=expiration
        )
        stored_token = server_db_.session.query(AuthenticationToken).filter_by(
            user_email=email, token_type=token_type).first()

        if stored_token and stored_token.token == token:
            # delete_authentication_token(token_type, token)
            return email

        # elif get_user_by_email(email) is None:
        #     print("email not found")
        #     return -1

        else:
            return None

    except (SignatureExpired, BadSignature):
        return None


def delete_authentication_token(token_type: str, token: str) -> None:
    """Delete the specified authentication token."""
    try:
        server_db_.session.query(AuthenticationToken).filter_by(
            token_type=token_type, token=token).delete()
        server_db_.session.commit()
    except Exception as e:
        print(e)


def get_user_by_email(email: str) -> User | None:
    return server_db_.session.execute(
        select(User).filter_by(email=email)
    ).scalar_one_or_none()


def get_user_by_email_or_username(email_or_username: str) -> User | None:
    return server_db_.session.execute(
        select(User).filter(
            or_(User.email == email_or_username, User.username == email_or_username)
        )
    ).scalar_one_or_none()


def get_user_by_fast_name(fast_name: str) -> User | None:
    return server_db_.session.execute(
        select(User).filter_by(fast_name=fast_name)
    ).scalar_one_or_none()


def delete_user_by_id(id_: int) -> None:
    server_db_.session.delete(server_db_.session.get(User, id_))
    server_db_.session.commit()


def get_new_user(email: str, username: str, password: str) -> User | None:
    # noinspection PyArgumentList
    try:
        new_user = User(
            email=email,
            username=username,
            password=password,
        )
        server_db_.session.add(new_user)
        server_db_.session.commit()
        return new_user
    except IntegrityError:
        return None


def _init_user() -> User | None:
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
            roles="admin|"
        )
        server_db_.session.add(new_user)
        server_db_.session.commit()
        return repr(new_user)

    return None
