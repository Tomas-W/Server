import os
from itsdangerous import SignatureExpired, BadSignature
from flask import url_for
from flask_login import current_user
from flask_mail import Message

from src.extensions import server_db_, serializer_, mail_
from src.models.auth_model.auth_mod import get_user_by_email, AuthenticationToken
from src.models.mod_utils import commit_to_db


def process_verification_token(email: str, token_type: str) -> None:
    token = generate_authentication_token(email, token_type)
    reset_authentication_token(email, token_type, token)
    send_authentication_email(email, token_type, token)


def generate_authentication_token(email: str, token_type: str) -> str:
    token = serializer_.dumps(email, salt=os.environ.get(f"{token_type.upper()}_SALT"))
    return token


def reset_authentication_token(email: str, token_type: str, token: str) -> bool:
    """
    Reset the specified authentication token.
    If no User with the given email exists, return False.
    If the token already exists, update it and return True.
    If the token does not exist, create a new one and return True.
    """
    id_ = get_user_by_email(email).id
    if not id_:
        return False
    
    existing_token = server_db_.session.query(AuthenticationToken).filter_by(
        user_id=id_).first()
    if existing_token:
        existing_token.token = token
    else:
        new_token = AuthenticationToken(user_id=id_, token_type=token_type, token=token)
        server_db_.session.add(new_token)
        server_db_.session.commit()
    return True


def send_authentication_email(email: str, token_type: str, token: str):
    if token_type == "email_verification":
        url_ = "admin.verify_email"
        subject = "Email Verification"
        message = "Please verify your email by visiting: "
    elif token_type == "password_verification":
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
    stored_token = server_db_.session.query(AuthenticationToken).filter_by(
        token=token).first()
    try:
        email = serializer_.loads(
            token,
            salt=os.environ.get(f"{token_type.upper()}_SALT"),
            max_age=expiration
        )
        if stored_token and stored_token.token == token:
            delete_authentication_token(token_type, token)
            return email
        else:
            return None
    except (SignatureExpired, BadSignature):
        return None
    
    
@commit_to_db
def delete_authentication_token(token_type: str, token: str) -> None:
    """Delete the specified authentication token."""
    server_db_.session.query(AuthenticationToken).filter_by(
        token_type=token_type, token=token).delete()

