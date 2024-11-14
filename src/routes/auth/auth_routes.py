from functools import wraps
import os

import requests
from flask import (
    Blueprint, redirect, url_for, request, render_template, flash, session
)
from flask_login import login_required, current_user
from google.oauth2 import id_token  # noqa
from pip._vendor import cachecontrol  # noqa
import google.auth.transport.requests  # noqa
from sqlalchemy import select

from src.extensions import server_db_, flow_
from src.models.auth_model.auth_mod_utils import delete_authentication_token
from src.routes.auth.auth_forms import (
    LoginForm, FastLoginForm, RegisterForm, RequestResetForm, SetPasswordForm,
    ResetPasswordForm
)
from src.routes.auth.auth_route_utils import (
    fast_login, normal_login, handle_user_login, handle_user_logout
)
from src.models.auth_model.auth_mod import User
from src.models.auth_model.auth_mod_utils import (
    process_verification_token, confirm_authentication_token, get_user_by_email,
    get_new_user
)
from src.models.state_model.state_mod_utils import (
    save_oauth_state, get_and_delete_oauth_state
)
from config.settings import (
    PASSWORD_VERIFICATION, LOGIN_REDIRECT, ALL_NEWS_REDIRECT, FAST_LOGIN_FORM_TYPE,
    SET_PASSWORD_REDIRECT, REQUEST_RESET_REDIRECT, REGISTER_REDIRECT,
    USER_ADMIN_REDIRECT, TOKEN_ERROR_MSG, STATE_ERROR_MSG, SESSION_ERROR_MSG,
    AUTHENTICATION_LINK_ERROR_MSG, UNEXPECTED_ERROR_MSG, LOGOUT_SUCCESS_MSG,
    PASSWORD_RESET_SEND_MSG, CREATE_ACCOUNT_MSG, PASSWORD_UPDATE_MSG, HOME_PAGE_REDIRECT
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
                flash("Fast login failed.")
                return redirect(url_for(f"auth.{view_func.__name__}"))

        return view_func(*args, **kwargs)

    return wrapper


@auth_bp.route("/")
def index():
    """Serves home page when logged in, else login page."""
    if current_user.is_authenticated:
        return redirect(url_for(HOME_PAGE_REDIRECT))
    return redirect(url_for(LOGIN_REDIRECT))


@auth_bp.route("/fresh")
def base():
    """Creates a dummy account after db reset and serves login page."""
    new_user = User(email="100pythoncourse@gmail.com",
                    username="tomas",
                    password="TomasTomas1!",
                    fast_name="tomas",
                    fast_code="00000")
    server_db_.session.add(new_user)
    server_db_.session.commit()
    return redirect(url_for(LOGIN_REDIRECT))


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

    if request.method == "POST":
        if login_form.validate_on_submit():
            response, message = normal_login(login_form)
            if response:
                return response
            if message:
                flash(message)

        session["form_errors"] = login_form.errors
        flash(f"Remember me: {login_form.remember.data}")

    form_errors = session.pop("form_errors", None)
    
    return render_template(
        "/auth/login.html",
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
    except Exception as e:
        flash(TOKEN_ERROR_MSG)
        return redirect(url_for(LOGIN_REDIRECT))

    state_in_request = request.args.get("state")
    oauth_state = get_and_delete_oauth_state(state_in_request)

    if not oauth_state:
        flash(STATE_ERROR_MSG)
        return redirect(url_for(LOGIN_REDIRECT))

    credentials = flow_.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials.id_token,
        request=token_request,
        audience=os.environ.get("GOOGLE_CLIENT_ID"),
    )
    email = id_info.get("email")
    user = get_user_by_email(email)

    if not user:
        session["email"] = email
        return redirect(url_for(SET_PASSWORD_REDIRECT))

    handle_user_login(user, remember=False)
    return redirect(url_for(ALL_NEWS_REDIRECT))


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
                flash(SESSION_ERROR_MSG)
                return redirect(url_for(REQUEST_RESET_REDIRECT))
            
            user: User | None = get_new_user(
                email=email,
                username=email[:8],
                password=set_password_form.password.data,
            )
            if user:
                handle_user_login(user, remember=False)
                return redirect(url_for(ALL_NEWS_REDIRECT))
            else:
                flash(UNEXPECTED_ERROR_MSG)
                return redirect(url_for(LOGIN_REDIRECT))

        session["form_errors"] = set_password_form.errors

    form_errors = session.pop("form_errors", None)

    return render_template(
        "/auth/set_password.html",
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
                return redirect(url_for(ALL_NEWS_REDIRECT))
            else:
                flash(UNEXPECTED_ERROR_MSG)
                return redirect(url_for(REGISTER_REDIRECT))

        session["form_errors"] = register_form.errors
        flash("T0000STER")

    form_errors = session.pop("form_errors", None)
    fill_email = session.pop("fill_email", None)
    if fill_email:
        register_form.email.data = fill_email

    return render_template(
        "/auth/register.html",
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
            process_verification_token(request_reset_form.email.data,
                                       token_type=PASSWORD_VERIFICATION)
            flash(PASSWORD_RESET_SEND_MSG)
            session["email"] = request_reset_form.email.data
            return redirect(url_for(REQUEST_RESET_REDIRECT))
        
        session["form_errors"] = request_reset_form.errors
        flash("T0000STER")

    form_errors = session.pop("form_errors", None)

    return render_template(
        "/auth/request_reset.html",
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

    email = confirm_authentication_token(token, PASSWORD_VERIFICATION)
    if not email:
        flash(AUTHENTICATION_LINK_ERROR_MSG)
        return redirect(url_for(REQUEST_RESET_REDIRECT))

    # if email == -1:  # Fix workaroud for email == -1
    #     flash(CREATE_ACCOUNT_MSG)
    #     session["fill_email"] = session.pop("email")
    #     return redirect(url_for(REGISTER_REDIRECT))
    
    user: User | None = server_db_.session.execute(
        select(User).filter_by(email=email)).scalar_one_or_none()

    if request.method == "POST":
        if reset_password_form.validate_on_submit():
            user.set_password(reset_password_form.password.data)
            user.set_email_verified(True)
            delete_authentication_token(PASSWORD_VERIFICATION, token)
            handle_user_login(user, remember=False, flash_=False)
            
            flash(PASSWORD_UPDATE_MSG)
            session["flash_type"] = "authentication"
            return redirect(url_for(USER_ADMIN_REDIRECT))

        session["form_errors"] = reset_password_form.errors
        session["last_form_type"] = "password"
    
    form_errors = session.pop("form_errors", None)

    return render_template(
        "auth/reset_password.html",
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
    flash(LOGOUT_SUCCESS_MSG)
    return redirect(url_for(LOGIN_REDIRECT))
