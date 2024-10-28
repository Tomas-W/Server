from functools import wraps
import os
from datetime import datetime

import requests
from flask import (Blueprint, redirect, url_for, request, render_template, flash,
                   session)
from flask_login import login_required, current_user
from google.oauth2 import id_token  # noqa
from pip._vendor import cachecontrol  # noqa
import google.auth.transport.requests  # noqa
from sqlalchemy import select

from src.extensions import flow_, server_db_
from src.auth.auth_forms import (LoginForm, FastLoginForm, RegisterForm, RequestResetForm,
                                 SetPasswordForm, ResetPasswordForm)
from src.auth.auth_route_utils import (confirm_reset_token, send_password_reset_email,
                                       fast_login, normal_login, handle_user_login,
                                       handle_user_logout)
from src.models.auth_mod import User
from src.models.auth_mod import (get_user_by_email, add_new_user, get_new_user,
                                change_user_password)
from src.models.state_mod import (save_oauth_state, get_and_delete_oauth_state)


auth_bp = Blueprint("auth", __name__)
SESSION_FORM_ERRORS = "form_errors"
SESSION_LAST_FORM_TYPE = "last_form_type"
FAST_FORM_TYPE = "fast_login"


def handle_fast_login(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if request.method == "POST":
            form_type = request.form.get("form_type")
            if form_type == FAST_FORM_TYPE:
                form = FastLoginForm()
                if form.validate_on_submit():
                    response, message = fast_login(form)
                    if response:
                        return response
                    if message:
                        flash(message)
                        return redirect(url_for(f"auth.{view_func.__name__}", fast=True))
                session[SESSION_FORM_ERRORS] = form.errors
                session[SESSION_LAST_FORM_TYPE] = FAST_FORM_TYPE
                return redirect(url_for(f"auth.{view_func.__name__}", fast=True))

        return view_func(*args, **kwargs)

    return wrapper


@auth_bp.route("/")
def index():
    """Serves home page when logged in, else login page."""
    if current_user.is_authenticated:
        return redirect(url_for("news.all_news"))
    return redirect(url_for("auth.login"))


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
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
@handle_fast_login
def login():
    login_form = LoginForm()
    fast_login_form = FastLoginForm()
    form_type = request.form.get("form_type")
    fast = request.args.get("fast", "false").lower() == "true"

    if request.method == "POST" and form_type == "login":
            if login_form.validate_on_submit():
                response, message = normal_login(login_form)
                if response:
                    return response
                if message:
                    flash(message)
                    return redirect(url_for("auth.login"))
            # Store form errors and type
            session["form_errors"] = login_form.errors
            session["last_form_type"] = "login"
            return redirect(url_for("auth.login"))

    # Retrieve form errors and type
    form_errors = session.pop("form_errors", None)
    last_form_type = session.pop("last_form_type", None)

    if form_errors:
        # Re-populatedata
        if last_form_type == "fast_login":
            fast_login_form = FastLoginForm(formdata=None)
            fast_login_form.process(request.form)
            flash("Invalid input")
        elif last_form_type == "login":
            login_form = LoginForm(formdata=None)
            login_form.process(request.form)

    return render_template(
        "/auth/login.html",
        login_form=login_form,
        fast_login_form=fast_login_form,
        page="login",
        fast=fast,
        form_errors=form_errors,
        last_form_type=last_form_type
    )


@auth_bp.route("/g-login")
def g_login():
    """Creates authorization link and redirect to Google login services."""
    authorization_url, state = flow_.authorization_url()
    save_oauth_state(state)
    return redirect(authorization_url)


@auth_bp.route("/callback")
def callback():
    try:
        flow_.fetch_token(authorization_response=request.url)
    except Exception as e:
        flash("Token authentication failed")
        return redirect(url_for("auth.login"))

    state_in_request = request.args.get("state")
    oauth_state = get_and_delete_oauth_state(state_in_request)

    if not oauth_state:
        flash("State authentication failed")
        return redirect(url_for("auth.login"))

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
        return redirect(url_for("auth.set_password"))

    handle_user_login(user, remember=False)
    return redirect(url_for("news.all_news"))


@auth_bp.route("/set_password", methods=["GET", "POST"])
@handle_fast_login
def set_password():
    set_password_form = SetPasswordForm()
    fast_login_form = FastLoginForm()
    form_type = request.form.get("form_type")
    fast = request.args.get("fast", "false").lower() == "true"

    if request.method == "POST" and form_type == "password":
            if set_password_form.validate_on_submit():
                email = session.get("email")
                if not email:
                    flash("Session authentication failed")
                    return redirect(url_for("auth.request-reset"))
                session.pop("email")
                user: User = get_new_user(
                    email=email,
                    username=email[:8],
                    password=set_password_form.password.data,
                )
                if user:
                    handle_user_login(user, remember=False)
                    return redirect(url_for("news.all_news"))
                else:
                    flash("Unexpected db error")
                    return redirect(url_for("auth.set_password"))
            # Store form errors and type
            session["form_errors"] = set_password_form.errors
            session["last_form_type"] = "password"
            return redirect(url_for("auth.set_password"))

    # Retrieve form errors and type
    form_errors = session.pop("form_errors", None)
    last_form_type = session.pop("last_form_type", None)

    if form_errors:
        # Re-populate the data
        if last_form_type == "fast_login":
            fast_login_form = FastLoginForm(formdata=None)
            fast_login_form.process(request.form)
            flash("Invalid input")
        elif last_form_type == "password":
            set_password_form = SetPasswordForm(formdata=None)
            set_password_form.process(request.form)

    return render_template(
        "/auth/set_password.html",
        set_password_form=set_password_form,
        fast_login_form=fast_login_form,
        page="set_password",
        fast=fast,
        form_errors=form_errors,
        last_form_type=last_form_type
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
    form_type = request.form.get("form_type")
    fast = request.args.get("fast", "false").lower() == "true"

    if request.method == "POST" and form_type == "register":
            if register_form.validate_on_submit():
                add_new_user(
                    email=register_form.email.data,
                    username=register_form.username.data,
                    password=register_form.password.data,
                )
                return redirect(url_for("auth.login"))
            # Store form errors and type
            session["form_errors"] = register_form.errors
            session["last_form_type"] = "register"
            return redirect(url_for("auth.register"))

    # Retrieve form errors and type
    form_errors = session.pop("form_errors", None)
    last_form_type = session.pop("last_form_type", None)

    if form_errors:
        # Re-populate the data
        if last_form_type == "fast_login":
            fast_login_form = FastLoginForm(formdata=None)
            fast_login_form.process(request.form)
            flash("Invalid input")
        elif last_form_type == "register":
            register_form = RegisterForm(formdata=None)
            register_form.process(request.form)

    return render_template(
        "/auth/register.html",
        register_form=register_form,
        fast_login_form=fast_login_form,
        page="register",
        fast=fast,
        form_errors=form_errors,
        last_form_type=last_form_type
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
    form_type = request.form.get("form_type")
    fast = request.args.get("fast", "false").lower() == "true"

    if request.method == "POST" and form_type == "request_reset":
            if request_reset_form.validate_on_submit():
                user: User = server_db_.session.execute(select(User).filter_by(
                    email=request_reset_form.email.data)).scalar_one_or_none()
                if user:
                    send_password_reset_email(user)
                flash("If user exists, code has been sent")
                return redirect(url_for("auth.request_reset"))
            # Store form errors and type
            session["form_errors"] = request_reset_form.errors
            session["last_form_type"] = "request_reset"
            return redirect(url_for("auth.request_reset"))

    # Retrieve form errors and type
    form_errors = session.pop("form_errors", None)
    last_form_type = session.pop("last_form_type", None)

    if form_errors:
        # Re-populate the data
        if last_form_type == "fast_login":
            fast_login_form = FastLoginForm(formdata=None)
            fast_login_form.process(request.form)
            flash("Invalid input")
        elif last_form_type == "request_reset":
            request_reset_form = RequestResetForm(formdata=None)
            request_reset_form.process(request.form)

    return render_template(
        "/auth/request_reset.html",
        request_reset_form=request_reset_form,
        fast_login_form=fast_login_form,
        page="request_reset",
        fast=fast,
        form_errors=form_errors,
        last_form_type=last_form_type
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
    form_type = request.form.get("form_type")
    fast = request.args.get("fast", "false").lower() == "true"

    email = confirm_reset_token(token)

    if not email:
        flash("Reset link invalid or expired")
        return redirect(url_for("auth.request_reset"))

    user: User = server_db_.session.execute(
        select(User).filter_by(email=email)).scalar_one_or_none()

    if request.method == "POST" and form_type == "password":
            if reset_password_form.validate_on_submit():
                change_user_password(user, reset_password_form.password.data)
                flash("Your password has been updated!")
                return redirect(url_for('auth.login'))
            # Store form errors and type
            session["form_errors"] = reset_password_form.errors
            session["last_form_type"] = "password"
            return redirect(url_for("auth.reset_password", token=token))

    # Retrieve form errors and type
    form_errors = session.pop("form_errors", None)
    last_form_type = session.pop("last_form_type", None)

    if form_errors:
        # Re-populate the data
        if last_form_type == "fast_login":
            fast_login_form = FastLoginForm(formdata=None)
            fast_login_form.process(request.form)
            flash("Invalid input")
        elif last_form_type == "password":
            reset_password_form = ResetPasswordForm(formdata=None)
            reset_password_form.process(request.form)

    return render_template(
        "auth/reset_password.html",
        reset_password_form=reset_password_form,
        fast_login_form=fast_login_form,
        page="reset_password",
        fast=fast,
        form_errors=form_errors,
        last_form_type=last_form_type
    )
    
    
@auth_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logs out user, clean up session and redirect to login page."""
    handle_user_logout()
    flash("You are logged out")
    return redirect(url_for("auth.login"))
