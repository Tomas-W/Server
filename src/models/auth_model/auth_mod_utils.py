import os

from flask import url_for
from flask_login import current_user
from flask_mail import Message
from itsdangerous import SignatureExpired, BadSignature
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError

from src.extensions import server_db_, serializer_, mail_
from src.models.auth_model.auth_mod import (
    User, AuthenticationToken, AuthenticationToken
)
from src.models.mod_utils import commit_to_db
from config.settings import PASSWORD_VERIFICATION, EMAIL_VERIFICATION


def process_verification_token(email: str, token_type: str) -> None:
    """
    Generate a token, reset it in the database, and send an email with a 
    verification link and instructions.
    """
    token = generate_authentication_token(email, token_type)
    reset_authentication_token(token_type, token)
    send_authentication_email(email, token_type, token)


def generate_authentication_token(email: str, token_type: str) -> str:
    token = serializer_.dumps(email, salt=os.environ.get(f"{token_type.upper()}_SALT"))
    return token


def reset_authentication_token(token_type: str, token: str) -> bool:
    """
    Reset the specified authentication token.
    If no User with the given email exists, return False.
    If the token already exists, update it and return True.
    If the token does not exist, create a new one and return True.
    """
    user = get_user_by_email(current_user.email)
    if not user:
        return False
    
    id_ = user.id
    existing_token = server_db_.session.query(AuthenticationToken).filter_by(
        user_id=id_, token_type=token_type).first()
    if existing_token:
        existing_token.token = token
    else:
        new_token = AuthenticationToken(user_id=id_, token_type=token_type, token=token)
        server_db_.session.add(new_token)
        server_db_.session.commit()
    return True


def send_authentication_email(email: str, token_type: str, token: str):
    """
    Send an email with a authentication link and instructions.
    Verifications:
    - EMAIL_VERIFICATION [set email verified]
    - PASSWORD_VERIFICATION [reset password]
    """
    if token_type == EMAIL_VERIFICATION:
        url_ = "admin.verify_email"
        subject = "Email Verification"
        message = "Please verify your email by visiting: "
    elif token_type == PASSWORD_VERIFICATION:
        url_ = "auth.reset_password"
        subject = "Password Reset"
        message = "Please reset your password by visiting: "

    verification_url = url_for(url_, token=token, _external=True)
    message = Message(subject=subject,
                      sender=os.environ.get("GMAIL_EMAIL"),
                      recipients=[email],
                      body=f"{message} {verification_url}")
    mail_.send(message)


def confirm_authentication_token(token: str, token_type: str, expiration: int = 3600) -> str | None:
    """
    Confirm the specified authentication token.
    Verifications:
    - EMAIL_VERIFICATION [set email verified | set new email]
    - PASSWORD_VERIFICATION [reset password]
    """
    stored_token = server_db_.session.query(AuthenticationToken).filter_by(
        user_id=current_user.id, token_type=token_type).first()
    try:
        email = serializer_.loads(
            token,
            salt=os.environ.get(f"{token_type.upper()}_SALT"),
            max_age=expiration
        )
        
        if stored_token and stored_token.token == token:
            delete_authentication_token(token_type, token)
            return email
        
        elif get_user_by_email(email) is None:
            return -1
        
        else:
            return None
        
    except (SignatureExpired, BadSignature):
        return None
    
    
@commit_to_db
def delete_authentication_token(token_type: str, token: str) -> None:
    """Delete the specified authentication token."""
    server_db_.session.query(AuthenticationToken).filter_by(
        token_type=token_type, token=token).delete()


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


@commit_to_db
def delete_user_by_id(id_: int) -> None:
    server_db_.session.delete(server_db_.session.get(User, id_))


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
        )
        server_db_.session.add(new_user)
        server_db_.session.commit()
        return repr(new_user)
    
    return None
