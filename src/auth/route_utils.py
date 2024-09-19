import os

from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from flask import url_for, redirect, session
from flask_login import login_user, current_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from src.auth.forms import FastLoginForm, LoginForm
from src.extensions import server_db_, mail_, argon2_
from src.models.auth_mod import User


def add_new_user(email: str, username: str,
                 hashed_password: str) -> None:
    """Takes register_form input data and creates a new user."""
    # noinspection PyArgumentList
    new_user = User(
        email=email,
        username=username,
        password=hashed_password,
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
    token = generate_reset_token(user.email_or_uname)
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    message = Message(subject="Password Reset",
                      sender=os.environ.get("GMAIL_EMAIL"),
                      recipients=[user.email_or_uname],
                      body=f"Please reset your password by visiting: {reset_url}")
    mail_.send(message)


def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(os.environ.get("FLASK_KEY"))
    return serializer.dumps(email, salt=os.environ.get("PWD_RESET_SALT"))


def confirm_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(os.environ.get("FLASK_KEY"))
    try:
        email = serializer.loads(
            token,
            salt=os.environ.get("PWD_RESET_SALT"),
            max_age=expiration
        )
        return email
    except (SignatureExpired, BadSignature):
        return None


def handle_argon2_exception(e):
    if isinstance(e, VerifyMismatchError):
        return "Incorrect credentials"
    elif isinstance(e, (VerificationError, InvalidHashError)):
        return "An error occurred during verification"
    else:
        return "An unexpected error occurred"


def fast_login(login_form: FastLoginForm):
    user = User.query.filter_by(fast_name=login_form.fast_name.data).first()
    if not user:
        return None, "Incorrect credentials"

    try:
        if argon2_.verify(user.fast_code, login_form.fast_code.data):
            login_user(user=user)
            current_user.tot_logins += 1
            server_db_.session.commit()
            session.permanent = False
            return redirect(url_for("home.home")), None
    except (VerifyMismatchError, VerificationError, InvalidHashError) as e:
        return None, handle_argon2_exception(e)
    return None, "Incorrect credentials"


def normal_login(login_form: LoginForm):
    user = User.query.filter((User.email == login_form.email_or_uname.data) |
                             (User.username == login_form.email_or_uname.data)).first()
    if not user:
        return None, "Invalid credentials"

    try:
        if argon2_.verify(user.password, login_form.password.data):
            remember = login_form.remember.data
            user.remember_me = remember
            server_db_.session.commit()
            login_user(user=user, remember=remember, fresh=True)
            current_user.tot_logins += 1
            server_db_.session.commit()
            session.permanent = remember
            return redirect(url_for("home.home")), None
    except (VerifyMismatchError, VerificationError, InvalidHashError) as e:
        return None, handle_argon2_exception(e)
    return None, "Incorrect credentials"
