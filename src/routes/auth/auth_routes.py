import os
import requests

from functools import wraps
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
)
from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from pip._vendor import cachecontrol
from sqlalchemy import select

from src.extensions import (
    flow_,
    logger,
    server_db_,
)

from src.models.auth_model.auth_mod import User
from src.models.auth_model.auth_mod_utils import (
    confirm_authentication_token,
    delete_authentication_token,
    get_new_user,
    get_user_by_email,
    start_verification_process,
)
from src.models.state_model.state_mod_utils import (
    get_and_delete_oauth_state,
    save_oauth_state,
)

from src.routes.auth.auth_route_utils import (
    fast_login,
    handle_user_login,
    handle_user_logout,
    normal_login,
)

from src.routes.auth.auth_forms import (
    FastLoginForm,
    LoginForm,
    RegisterForm,
    RequestResetForm,
    ResetPasswordForm,
    SetPasswordForm,
)

from config.settings import (
    MESSAGE,
    REDIRECT,
    SERVER,
    TEMPLATE,
)

auth_bp = Blueprint("auth", __name__)


def handle_fast_login(view_func):
    """
    Wraps all interactive auth routes.
    Checks if fast login form is submitted and handles it.
    
    -FastLoginForm
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if request.method == "POST":
            fast_login_form = FastLoginForm()
            
            if fast_login_form.fast_name.data is not None and fast_login_form.fast_code.data is not None:
                session["fast_login"] = True
                if fast_login_form.validate_on_submit():
                    
                    response, message = fast_login(fast_login_form)
                    if response:
                        return response
                    if message:
                        flash(message)
                        return redirect(url_for(f"auth.{view_func.__name__}"))
                
                session["form_errors"] = fast_login_form.errors
                flash(MESSAGE.FAST_LOGIN_FAILED)
                return redirect(url_for(f"auth.{view_func.__name__}"))

        return view_func(*args, **kwargs)

    return wrapper


@auth_bp.route("/")
def index():
    """Serves home page when logged in, else login page."""
    if current_user.is_authenticated:
        return redirect(url_for(REDIRECT.HOME_PAGE))
    return redirect(url_for(REDIRECT.LOGIN))


@auth_bp.route("/login", methods=["GET", "POST"])
@handle_fast_login
def login():
    """
    Serves login form and redirects to login page when not successful.
    
    - LoginForm
    """
    login_form = LoginForm()
    fast_login_form = FastLoginForm()
    fast = session.pop("fast_login", False)
    next_url = request.args.get("next")
    if next_url:
        session["next"] = next_url

    if request.method == "POST":
        if login_form.validate_on_submit():
            response, message = normal_login(login_form)
            if response:
                return response
            if message:
                flash(message)

        session["form_errors"] = login_form.errors

    form_errors = session.pop("form_errors", None)
    
    return render_template(
        TEMPLATE.LOGIN,
        login_form=login_form,
        fast_login_form=fast_login_form,
        form_errors=form_errors,
        fast=fast,
    )


@auth_bp.route("/g-login")
def g_login():
    """Creates authorization link and redirect to Google login services."""
    authorization_url, state = flow_.authorization_url()
    save_oauth_state(state)
    return redirect(authorization_url)


@auth_bp.route("/callback")
def callback():
    """
    Serves callback for Google login.
    If successful and user exists,
     call handle_user_login and redirects to ALL_NEWS_REDIRECT.
    If successful and user does not exist,
     redirects to SET_PASSWORD_REDIRECT.
    If not successful, redirects to LOGIN_REDIRECT and flashes error message.
    """
    try:
        flow_.fetch_token(authorization_response=request.url)
    except GoogleAuthError as e:
        flash(MESSAGE.TOKEN_ERROR)
        return redirect(url_for(REDIRECT.LOGIN))
    except Exception as e:
        logger.warning(f"[AUTH] OAUTH ERROR {e}")
        flash(MESSAGE.TOKEN_ERROR)
        return redirect(url_for(REDIRECT.LOGIN))

    state_in_request = request.args.get("state")
    oauth_state = get_and_delete_oauth_state(state_in_request)

    if not oauth_state:
        logger.error(f"[AUTH] WRONG OAUTH STATE")
        flash(MESSAGE.STATE_ERROR)
        return redirect(url_for(REDIRECT.LOGIN))

    credentials = flow_.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google_requests.Request(session=cached_session)

    try:
        id_info = id_token.verify_oauth2_token(
            id_token=credentials.id_token,
            request=token_request,
            audience=current_app.ENV.GOOGLE_CLIENT_ID,
        )
    except GoogleAuthError as e:
        flash(MESSAGE.TOKEN_ERROR)
        return redirect(url_for(REDIRECT.LOGIN))
    except ValueError as e:
        logger.error(f"[AUTH] OAUTH TOKEN VALIDATION ERROR: {credentials.id_token[:20]}.. {e}")
        flash(MESSAGE.TOKEN_ERROR)
        return redirect(url_for(REDIRECT.LOGIN))
    
    email = id_info.get("email")
    user = get_user_by_email(email)

    if not user:
        session["email"] = email
        return redirect(url_for(REDIRECT.SET_PASSWORD))

    handle_user_login(user, remember=False)
    return redirect(url_for(REDIRECT.ALL_NEWS))


@auth_bp.route("/set_password", methods=["GET", "POST"])
@handle_fast_login
def set_password():
    """
    Serves set password form after Google login when User does not exist.
    If no session email, redirect to REQUEST_RESET_REDIRECT.
    Creates User, calls handle_user_login and redirects to ALL_NEWS_REDIRECT.
    If unexpected error, redirect to LOGIN_REDIRECT.
    
    - SetPasswordForm
    """
    set_password_form = SetPasswordForm()
    fast_login_form = FastLoginForm()
    fast = session.pop("fast_login", False)

    if request.method == "POST":
        if set_password_form.validate_on_submit():
            email = session.pop("email", None)
            if not email:
                flash(MESSAGE.SESSION_ERROR)
                return redirect(url_for(REDIRECT.REQUEST_RESET))
            
            user: User | None = get_new_user(
                email=email,
                username=email[:8],
                password=set_password_form.password.data,
            )
            if user:
                handle_user_login(user, remember=False)
                return redirect(url_for(REDIRECT.ALL_NEWS))
            else:
                flash(MESSAGE.UNEXPECTED_ERROR)
                return redirect(url_for(REDIRECT.LOGIN))

        session["form_errors"] = set_password_form.errors

    form_errors = session.pop("form_errors", None)

    return render_template(
        TEMPLATE.SET_PASSWORD,
        set_password_form=set_password_form,
        fast_login_form=fast_login_form,
        form_errors=form_errors,
        fast=fast,
    )


@auth_bp.route("/register", methods=["GET", "POST"])
@handle_fast_login
def register():
    """
    Serves register form and redirects to login page
    when successful or redirects to register page when not.
    """
    register_form = RegisterForm()
    fast_login_form = FastLoginForm()
    fast = session.pop("fast_login", False)

    if request.method == "POST":
        if register_form.validate_on_submit():
            new_user = get_new_user(
                email=register_form.email.data,
                username=register_form.username.data,
                password=register_form.password.data,
            )
            if new_user:
                handle_user_login(new_user, remember=False)
                return redirect(url_for(REDIRECT.ALL_NEWS))
            else:
                flash(MESSAGE.UNEXPECTED_ERROR)
                return redirect(url_for(REDIRECT.REGISTER))

        session["form_errors"] = register_form.errors

    form_errors = session.pop("form_errors", None)
    fill_email = session.pop("fill_email", None)
    if fill_email:
        register_form.email.data = fill_email

    return render_template(
        TEMPLATE.REGISTER,
        register_form=register_form,
        fast_login_form=fast_login_form,
        form_errors=form_errors,
        fast=fast,
    )


@auth_bp.route("/request-reset", methods=["GET", "POST"])
@handle_fast_login
def request_reset():
    """
    Serves request reset form and redirects to request reset page
    when successful or not.
    """
    request_reset_form = RequestResetForm()
    fast_login_form = FastLoginForm()
    fast = session.pop("fast_login", False)

    if request.method == "POST":
        if request_reset_form.validate_on_submit():
            start_verification_process(request_reset_form.email.data,
                                       token_type=SERVER.PASSWORD_VERIFICATION)
            flash(MESSAGE.PASSWORD_RESET_SEND)
            session["email"] = request_reset_form.email.data
            return redirect(url_for(REDIRECT.REQUEST_RESET))
        
        session["form_errors"] = request_reset_form.errors

    form_errors = session.pop("form_errors", None)

    return render_template(
        TEMPLATE.REQUEST_RESET,
        request_reset_form=request_reset_form,
        fast_login_form=fast_login_form,
        form_errors=form_errors,
        fast=fast,
    )


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
@handle_fast_login
def reset_password(token):
    """
    Serves reset password form and redirects to login page
    when successful or reset password page when not.
    """
    reset_password_form = ResetPasswordForm()
    fast_login_form = FastLoginForm()
    fast = session.pop("fast_login", False)

    email = confirm_authentication_token(token, SERVER.PASSWORD_VERIFICATION)
    if not email:
        flash(MESSAGE.AUTHENTICATION_LINK_ERROR)
        return redirect(url_for(REDIRECT.REQUEST_RESET))
    
    user: User | None = server_db_.session.execute(
        select(User).filter_by(email=email)).scalar_one_or_none()

    if request.method == "POST":
        if reset_password_form.validate_on_submit():
            user.set_password(reset_password_form.password.data)
            user.set_email_verified(True)
            delete_authentication_token(SERVER.PASSWORD_VERIFICATION, token)
            handle_user_login(user, remember=False)
            
            flash(MESSAGE.PASSWORD_UPDATE)
            session["flash_type"] = "authentication"
            return redirect(url_for(REDIRECT.USER_ADMIN))

        session["form_errors"] = reset_password_form.errors
        session["last_form_type"] = "password"
    
    form_errors = session.pop("form_errors", None)

    return render_template(
        TEMPLATE.RESET_PASSWORD,
        reset_password_form=reset_password_form,
        fast_login_form=fast_login_form,
        form_errors=form_errors,
        fast=fast,
    )
    
    
@auth_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logs out user, clean up session and redirect to login page."""
    handle_user_logout()
    flash(MESSAGE.LOGOUT_SUCCESS)
    return redirect(url_for(REDIRECT.LOGIN))
