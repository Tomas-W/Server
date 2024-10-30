from flask_login import current_user
from flask import url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import os

from src import server_db_, mail_
from src.models.news_mod import News
from src.auth.auth_route_utils import generate_verification_token
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


def send_verification_email(email: str):
    token = generate_verification_token(email)
    verification_url = url_for('admin.verify_email', token=token, _external=True)
    message = Message(subject="Email Verification",
                      sender=os.environ.get("GMAIL_EMAIL"),
                      recipients=[email],
                      body=f"Please verify your email by visiting: {verification_url}")
    mail_.send(message)


def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(os.environ.get("FLASK_KEY"))
    return serializer.dumps(email, salt=os.environ.get("EMAIL_VERIFICATION_SALT"))


def confirm_reset_token(token: str, expiration: int = 3600) -> str | None:
    serializer = URLSafeTimedSerializer(os.environ.get("FLASK_KEY"))
    try:
        email = serializer.loads(
            token,
            salt=os.environ.get("EMAIL_VERIFICATION_SALT"),
            max_age=expiration
        )
        return email
    except (SignatureExpired, BadSignature):
        return None


def process_authentication_form(authentication_form: AuthenticationForm):
    for field in authentication_form:
        if field.data:
            pass
