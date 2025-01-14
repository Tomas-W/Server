from argon2.exceptions import (
    VerifyMismatchError, VerificationError, InvalidHashError
)
from flask import url_for, redirect, session
from flask_login import login_user, current_user, logout_user
from flask import Response
from src.extensions import argon2_, logger
from src.routes.auth.auth_forms import FastLoginForm, LoginForm
from src.models.auth_model.auth_mod import User
from src.models.auth_model.auth_mod_utils import (
    get_user_by_email_or_username, get_user_by_fast_name
)
from config.settings import (
    FORM, MESSAGE, SERVER, REDIRECT
)


def handle_user_login(user: User, remember: bool = False, fresh: bool = True, login_type: str = SERVER.NORMAL_LOGIN) -> None:
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
    if login_type == SERVER.FAST_LOGIN:
        logger.info(f"[AUTH] FAST LOG IN")
    elif login_type == SERVER.GOOGLE_LOGIN:
        logger.info(f"[AUTH] GOOGLE LOG IN")
    else:
        logger.info(f"[AUTH] NORMAL LOG IN", )
    

def handle_user_logout() -> None:
    """Logs out user and removes session data."""
    logger.info(f"[AUTH] LOG OUT")
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
        return None, MESSAGE.CREDENTIALS_ERROR

    try:
        if argon2_.verify(user.fast_code, login_form.fast_code.data):
            handle_user_login(user, login_type=FORM.FAST_LOGIN)
            next_url = session.pop("next", None)
            if next_url:
                return redirect(next_url), None
            return redirect(url_for(REDIRECT.ALL_NEWS)), None
    except (VerifyMismatchError, VerificationError, InvalidHashError) as e:
        return None, handle_argon2_exception(e)

    return None, MESSAGE.CREDENTIALS_ERROR


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
        return None, MESSAGE.CREDENTIALS_ERROR

    try:
        if argon2_.verify(user.password, login_form.password.data):
            remember = login_form.remember.data
            handle_user_login(user, remember=remember, fresh=True)
            next_url = session.pop("next", None)
            if next_url:
                return redirect(next_url), None
            return redirect(url_for(REDIRECT.ALL_NEWS)), None
    except (VerifyMismatchError, VerificationError, InvalidHashError) as e:
        return None, handle_argon2_exception(e)

    return None, MESSAGE.CREDENTIALS_ERROR


def handle_argon2_exception(e: Exception) -> str:
    """
    Checks argon2 exceptions to return appropriate error message.
    """
    if isinstance(e, VerifyMismatchError):
        logger.warning(f"[AUTH] CREDENTIALS ERROR: {e}")
        return MESSAGE.CREDENTIALS_ERROR
    if isinstance(e, (VerificationError, InvalidHashError)):
        logger.warning(f"[AUTH] VERIFICATION ERROR: {e}")
        return MESSAGE.VERIFICATION_ERROR
    return MESSAGE.UNEXPECTED_ERROR
