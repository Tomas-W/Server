import os
from random import randint

from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from flask import url_for, flash, render_template, redirect
from flask_login import login_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from src.auth.forms import FastLoginForm, LoginForm
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
    except SignatureExpired:
        flash("Code has expired, try again")
        return render_template(url_for("request_reset"))
    except BadSignature:
        flash("Invalid token, try again")
        return render_template(url_for("request_reset"))
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


def fast_login(login_form: FastLoginForm):
    user = User.query.filter_by(fast_name=login_form.fast_name.data).first()
    if user:
        try:
            if argon2_.verify(user.fast_code, login_form.fast_code.data):
                login_user(user=user)
                return redirect(url_for("home.home"))
        except VerifyMismatchError:
            flash("Incorrect credentials")
        except (VerificationError, InvalidHashError):
            flash("An error occurred during verification")
    else:
        flash("Incorrect credentials")
    return None


def normal_login(login_form: LoginForm):
    user = User.query.filter_by(email=login_form.email.data).first()
    if user:
        try:
            if argon2_.verify(user.password, login_form.password.data):
                remember = login_form.remember.data
                login_user(user=user, remember=remember, fresh=True)
                return redirect(url_for("home.home"))
        except VerifyMismatchError:
            flash("Invalid credentials")
        except (VerificationError,
                InvalidHashError):
            flash("An error occurred during verification")
    else:
        flash("Invalid credentials")
    return None
