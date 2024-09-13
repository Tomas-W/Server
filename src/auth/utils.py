import inspect
import os
from random import randint

from flask import url_for
from flask_mail import Message
from flask_wtf import FlaskForm
from itsdangerous import URLSafeTimedSerializer
from wtforms.fields.core import Field
from wtforms.validators import ValidationError

from src.extensions import server_db_, mail_, argon2_
from src.models.auth_mod import User


def add_new_user(email: str, username: str,
                 hashed_password: str, fast_name: str) -> None:
    """Takes register_form input data and creates a new user."""
    # noinspection PyArgumentList
    new_user = User(
        email=email,
        username=username,
        password=hashed_password,
        fast_name=fast_name,
    )
    server_db_.session.add(new_user)
    server_db_.session.commit()


def change_password(user: User, password: str) -> None:
    """
    Takes a user_id(int) and a hashed_password(str)
    Updates the password in the database.
    """
    hashed_password = argon2_.hash(password)
    user.password = hashed_password
    server_db_.session.commit()


def send_password_reset_email(user):
    """
    Generates a token and sends the user an email
    with a verification link.
    """
    token = generate_reset_token(user.email)
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    message = Message(subject="Password Reset",
                      sender=os.environ.get("GMAIL_EMAIL"),
                      recipients=[user.email],
                      body=f"Please reset your password by visiting: {reset_url}")
    mail_.send(message)


def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(os.environ.get("FLASK_KEY"))
    return serializer.dumps(email, salt=os.environ.get("PWD_RESET_SALT"))


def confirm_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(os.environ.get("FLASK_KEY"))
    try:
        email = serializer.loads(token, salt=os.environ.get("PWD_RESET_SALT"),
                                 max_age=expiration)
    except:
        return False
    return email


def send_reset_password_mail(user: User) -> None:
    """Sends reset key to the users email."""
    reset_code = str(randint(100000, 999999))
    user.reset_key = argon2_.hash(reset_code)
    server_db_.session.commit()
    message = Message(subject="Password reset request",
                      sender=os.environ.get("GMAIL_EMAIL"),
                      recipients=[user.email])
    message.body = f"""Your reset code: {reset_code}"""
    mail_.send(message=message)


class UsernameCheck:
    """Validates username by checking forbidden words and characters."""
    def __init__(self, banned_words: list, banned_chars: list, message=None) -> None:
        self.banned_words = banned_words
        self.banned_chars = banned_chars

        if not message:
            message = "Invalid username and or characters"
        self.message = message

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if field.data.lower() in (word.lower() for word in self.banned_words):
            raise ValidationError(self.message)
        if len([x for x in list(self.banned_chars) if x in field.data]):
            raise ValidationError(self.message)


class PasswordCheck:
    """Validates password by checking requirements."""
    def __init__(self, required_symbols: list | str, message: str | None = None) -> None:
        self.symbols = required_symbols

        if not message:
            message = "Password requirements not met"
        self.message = message

    def __call__(self, form: FlaskForm, field: Field) -> None:
        if not any(sym in field.data for sym in self.symbols):
            raise ValidationError("At least one special character required")

        if field.data == field.data.lower() or \
                field.data == field.data.upper():
            raise ValidationError("At least one upper and one lower case "
                                  "character required")


class EmailCheck:
    """Validates email by checking is registered or not."""
    def __init__(self, register: bool = False, message: str | None = None) -> None:
        self.register = register

        if not message:
            message = "Email unknown or already registered"
        self.message = message

    def __call__(self, form: FlaskForm, field: Field) -> None:
        user = User.query.filter_by(email=field.data).first()
        if user:
            if self.register:
                raise ValidationError(self.message)

        if not user and not self.register:
            ValidationError(self.message)
