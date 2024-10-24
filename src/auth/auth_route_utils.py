import os

from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from flask import url_for, redirect, session
from flask_login import login_user, current_user, logout_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from src.auth.auth_forms import FastLoginForm, LoginForm
from src.extensions import mail_, argon2_
from src.models.auth_mod import User
from src.utils.db_utils import get_user_by_fast_name, get_user_by_email_or_username


def handle_user_login(user: User, remember: bool = False, fresh: bool = True) -> None:
    login_user(user=user, remember=remember, fresh=fresh)
    current_user.increment_tot_logins()
    current_user.set_remember_me(remember)
    session.permanent = remember


def handle_user_logout() -> None:
    current_user.set_remember_me(False)
    logout_user()
    session.pop('remember', None)


def fast_login(login_form: FastLoginForm):
    user: User = get_user_by_fast_name(login_form.fast_name.data.lower())

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
    user: User = get_user_by_email_or_username(login_form.email_or_uname.data)

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


def confirm_reset_token(token: str, expiration: int = 3600) -> str | None:
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


def handle_argon2_exception(e: Exception) -> str:
    if isinstance(e, VerifyMismatchError):
        return "Incorrect credentials"
    if isinstance(e, (VerificationError, InvalidHashError)):
        return "Internal server error"
    return "An unexpected error occurred"
