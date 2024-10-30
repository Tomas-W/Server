import os

from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from flask import url_for, redirect, session, flash
from flask_login import login_user, current_user, logout_user
from flask_mail import Message
from itsdangerous import SignatureExpired, BadSignature

from src.auth.auth_forms import FastLoginForm, LoginForm
from src.extensions import mail_, server_db_, serializer_, argon2_
from src.models.auth_mod import (User, AuthenticationToken, get_user_by_fast_name,
                                 get_user_by_email_or_username, reset_password_reset_token,
                                 delete_password_reset_token)


def handle_user_login(user: User, remember: bool = False, fresh: bool = True,
                      flash_: bool = True) -> None:
    login_user(user=user, remember=remember, fresh=fresh)
    current_user.increment_tot_logins()
    current_user.set_remember_me(remember)
    session.permanent = remember
    if flash_:
        flash("Logged in successfully")


def handle_user_logout() -> None:
    current_user.set_remember_me(False)
    logout_user()
    session.pop('remember', None)


def fast_login(login_form: FastLoginForm):
    user: User | None = get_user_by_fast_name(login_form.fast_name.data.lower())

    if not user:
        return None, "Incorrect credentials"

    try:
        if argon2_.verify(user.fast_code, login_form.fast_code.data):
            handle_user_login(user)
            return redirect(url_for("news.all_news")), None
    except (VerifyMismatchError, VerificationError, InvalidHashError) as e:
        return None, handle_argon2_exception(e)

    return None, "Incorrect credentials"


def normal_login(login_form: LoginForm):
    user: User | None = get_user_by_email_or_username(login_form.email_or_uname.data)

    if not user:
        return None, "Incorrect credentials"

    try:
        if argon2_.verify(user.password, login_form.password.data):
            remember = login_form.remember.data
            handle_user_login(user, remember=remember, fresh=True)
            return redirect(url_for("news.all_news")), None
    except (VerifyMismatchError, VerificationError, InvalidHashError) as e:
        return None, handle_argon2_exception(e)

    return None, "Incorrect credentials"


def process_password_reset_verification(email: str) -> None:
    token = generate_password_reset_token(email)
    reset_password_reset_token(email, token)
    send_password_reset_email(email, token)


def generate_password_reset_token(email):
    token = serializer_.dumps(email, salt=os.environ.get("PASSWORD_VERIFICATION_SALT"))
    return token


def send_password_reset_email(email: str, token: str):
    verification_url = url_for("auth.reset_password", token=token, _external=True)
    message = Message(subject="Password Reset",
                      sender=os.environ.get("GMAIL_EMAIL"),
                      recipients=[email],
                      body=f"Please reset your password by visiting: {verification_url}")
    mail_.send(message)


def confirm_password_reset_token(token: str, expiration: int = 3600) -> str | None:
    stored_token = server_db_.session.query(AuthenticationToken).filter_by(
        user_id=current_user.id, token_type="password_reset").first()
    try:
        email = serializer_.loads(
            token,
            salt=os.environ.get("PASSWORD_VERIFICATION_SALT"),
            max_age=expiration
        )
        if stored_token and stored_token.token == token:
            delete_password_reset_token(current_user.id)
            return email
        else:
            return None
    except (SignatureExpired, BadSignature):
        return None
    
    
def confirm_password_reset_token(token: str, expiration: int = 3600) -> str | None:
    try:
        email = serializer_.loads(
            token,
            salt=os.environ.get("PASSWORD_VERIFICATION_SALT"),
            max_age=expiration
        )
        return email
    except (SignatureExpired, BadSignature):
        return None


def handle_argon2_exception(e: Exception) -> str:
    if isinstance(e, VerifyMismatchError):
        return "Incorrect credentials"
    if isinstance(e, (VerificationError, InvalidHashError)):
        return "Internal server error"
    return "An unexpected error occurred"








# def send_password_reset_email(user):
#     """
#     Generates a token and sends the user an email
#     with a verification link.
#     """
#     token = generate_verification_token(user.email)
#     reset_url = url_for('auth.reset_password', token=token, _external=True)
#     message = Message(subject="Password Reset",
#                       sender=os.environ.get("GMAIL_EMAIL"),
#                       recipients=[user.email],
#                       body=f"Please reset your password by visiting: {reset_url}")
#     mail_.send(message)


# def generate_verification_token(email):
#     return serializer_.dumps(email, salt=os.environ.get("PWD_RESET_SALT"))


# def confirm_reset_token(token: str, expiration: int = 3600) -> str | None:
#     try:
#         email = serializer_.loads(
#             token,
#             salt=os.environ.get("PWD_RESET_SALT"),
#             max_age=expiration
#         )
#         return email
#     except (SignatureExpired, BadSignature):
#         return None


