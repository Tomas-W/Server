from flask_login import current_user
from flask import url_for
from flask_mail import Message
from itsdangerous import (SignatureExpired, BadSignature)
import os

from src.extensions import server_db_, mail_, serializer_
from src.models.news_mod import News
from src.models.auth_mod import (reset_verification_token, AuthenticationToken,
                                 delete_verification_token)
from src.admin.admin_forms import AuthenticationForm

def add_news_message(title, content):
    # noinspection PyArgumentList
    new_news = News(
        title=title,
        content=content,
        author=current_user.username
    )
    server_db_.session.add(new_news)
    server_db_.session.commit()


def process_email_verification(email: str) -> None:
    token = generate_verification_token(email)
    reset_verification_token(email, token)
    send_verification_email(email, token)


def generate_verification_token(email):
    token = serializer_.dumps(email, salt=os.environ.get("EMAIL_VERIFICATION_SALT"))
    return token


def send_verification_email(email: str, token: str):
    verification_url = url_for("admin.verify_email", token=token, _external=True)
    message = Message(subject="Email Verification",
                      sender=os.environ.get("GMAIL_EMAIL"),
                      recipients=[email],
                      body=f"Please verify your email by visiting: {verification_url}")
    mail_.send(message)


def confirm_verification_token(token: str, expiration: int = 3600) -> str | None:
    stored_token = server_db_.session.query(AuthenticationToken).filter_by(
        user_id=current_user.id).first()
    try:
        email = serializer_.loads(
            token,
            salt=os.environ.get("EMAIL_VERIFICATION_SALT"),
            max_age=expiration
        )
        if stored_token and stored_token.token == token:
            delete_verification_token(current_user.id)
            return email
        else:
            return None
    except (SignatureExpired, BadSignature):
        return None
    

def process_authentication_form(authentication_form: AuthenticationForm):
    for field in authentication_form:
        if field.data:
            pass
