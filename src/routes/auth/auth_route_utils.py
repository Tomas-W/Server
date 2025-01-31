from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)
from flask import (
    Response,
    current_app,
    redirect,
    session,
    url_for,
)
from flask_login import (
    current_user,
    login_user,
    logout_user,
)

from src.extensions import (
    argon2_,
    logger,
)
from src.models.auth_model.auth_mod import User
from src.models.auth_model.auth_mod_utils import (
    get_user_by_email_or_username,
    get_user_by_fast_name,
)

from src.routes.auth.auth_forms import (
    FastLoginForm,
    LoginForm,
)

from config.settings import (
    FORM,
    MESSAGE,
    REDIRECT,
    SERVER,
)


def handle_user_login(user: User, login_type: str, remember: bool = False, fresh: bool = True) -> None:
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
        logger.info(f"[AUTH] FAST LOG IN", user="CLI")
    elif login_type == SERVER.GOOGLE_LOGIN:
        logger.info(f"[AUTH] GOOGLE LOG IN")
    else:
        logger.info("[AUTH] NORMAL LOG IN")
    

def handle_user_logout() -> None:
    """Logs out user and removes session data."""
    logger.info("logout ye")
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
            handle_user_login(user, login_type=SERVER.FAST_LOGIN)
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
            handle_user_login(user, login_type=SERVER.NORMAL_LOGIN, remember=remember, fresh=True)
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
        return MESSAGE.CREDENTIALS_ERROR
    if isinstance(e, (VerificationError, InvalidHashError)):
        logger.exception("[AUTH] VERIFICATION ERROR")
        return MESSAGE.VERIFICATION_ERROR
    return MESSAGE.UNEXPECTED_ERROR
