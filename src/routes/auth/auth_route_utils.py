from argon2.exceptions import (
    VerifyMismatchError, VerificationError, InvalidHashError
)
from flask import url_for, redirect, session, flash
from flask_login import login_user, current_user, logout_user
from flask import Response
from src.extensions import argon2_
from src.routes.auth.auth_forms import FastLoginForm, LoginForm
from src.models.auth_model.auth_mod import User
from src.models.auth_model.auth_mod_utils import (
    get_user_by_email_or_username, get_user_by_fast_name
)
from config.settings import (
    CREDENTIALS_ERROR_MSG, VERIFICATION_ERROR_MSG,
    UNEXPECTED_ERROR_MSG, ALL_NEWS_REDIRECT
)


def handle_user_login(user: User, remember: bool = False, fresh: bool = True) -> None:
    """
    Logs in user and sets up the session.
    Session is NOT fresh or permanent unless specified (fast_login).
    Regular login is always fresh while permanent depends on remember.
    Message is flashed unless flash_ is False.
    """
    login_user(user=user, remember=remember, fresh=fresh)
    current_user.increment_tot_logins()
    current_user.set_remember_me(remember)
    session.permanent = remember
    session["user_id"] = user.id


def handle_user_logout() -> None:
    """Logs out user and removes session data."""
    logout_user()
    session.clear()


def fast_login(login_form: FastLoginForm) -> tuple[Response | None, str | None]:
    """
    Verifies fast_login credentials and redirects.
    If login successfull, redirect to ALL_NEWS_REDIRECT and call handle_user_login.
    Session is not fresh or permanent.
    
    If not, it returns tuple of None and error message.
    """
    user: User | None = get_user_by_fast_name(login_form.fast_name.data.lower())

    if not user:
        return None, CREDENTIALS_ERROR_MSG

    try:
        if argon2_.verify(user.fast_code, login_form.fast_code.data):
            handle_user_login(user)
            next_url = session.pop("next", None)
            if next_url:
                return redirect(next_url), None
            return redirect(url_for(ALL_NEWS_REDIRECT)), None
    except (VerifyMismatchError, VerificationError, InvalidHashError) as e:
        return None, handle_argon2_exception(e)

    return None, CREDENTIALS_ERROR_MSG


def normal_login(login_form: LoginForm) -> tuple[Response | None, str | None]:
    """
    Verifies login credentials and redirects.
    If login successfull, redirect to ALL_NEWS_REDIRECT and call handle_user_login.
    Sets remember to True if remember-me is checked.
    Session is always fresh.
    
    If not, it returns tuple of None and error message.
    """
    user: User | None = get_user_by_email_or_username(login_form.email_or_uname.data)

    if not user:
        return None, CREDENTIALS_ERROR_MSG

    try:
        if argon2_.verify(user.password, login_form.password.data):
            remember = login_form.remember.data
            handle_user_login(user, remember=remember, fresh=True)
            next_url = session.pop("next", None)
            if next_url:
                return redirect(next_url), None
            return redirect(url_for(ALL_NEWS_REDIRECT)), None
    except (VerifyMismatchError, VerificationError, InvalidHashError) as e:
        return None, handle_argon2_exception(e)

    return None, CREDENTIALS_ERROR_MSG


def handle_argon2_exception(e: Exception) -> str:
    """
    Checks argon2 exceptions to return appropriate error message.
    """
    if isinstance(e, VerifyMismatchError):
        return CREDENTIALS_ERROR_MSG
    if isinstance(e, (VerificationError, InvalidHashError)):
        return VERIFICATION_ERROR_MSG
    return UNEXPECTED_ERROR_MSG
