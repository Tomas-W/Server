import os
from datetime import datetime

import requests
from flask import (Blueprint, redirect, url_for, request, render_template, flash,
                   session)
from flask_login import login_user, logout_user, login_required, current_user
from google.oauth2 import id_token
from pip._vendor import cachecontrol  # noqa
import google.auth.transport.requests
from sqlalchemy import select

from config.settings import CET
from src.extensions import flow_, server_db_
from src.auth.forms import (LoginForm, FastLoginForm, RegisterForm, RequestResetForm,
                            SetPasswordForm, ResetPasswordForm)
from src.auth.route_utils import (add_new_user, change_user_password, confirm_reset_token,
                                  send_password_reset_email, fast_login, normal_login)
from src.models.auth_mod import User
from src.models.state_mod import State

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    """Serves home page when logged in, else login page."""
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/fresh")
def base():
    """Creates a dummy account after db reset and serves login page."""
    add_new_user(
        email="test@gmail.com",
        username="test",
        password="Test123$",
    )
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    fast_login_form = FastLoginForm()
    form_type = request.form.get("form_type")
    fast = request.args.get("fast", "false").lower() == "true"

    if form_type == "fast_login":
        fast = True
        if fast_login_form.validate_on_submit():
            response, message = fast_login(fast_login_form)
            if response:
                return response
            if message:
                flash(message)
                return redirect(url_for("auth.login", fast=True))
    
    elif form_type == "login":
        if login_form.validate_on_submit():
            response, message = normal_login(login_form)
            if response:
                return response
            if message:
                flash(message)
                return redirect(url_for("auth.login"))
            
    return render_template(
        "/auth/login.html",
        login_form=login_form,
        fast_login_form=fast_login_form,
        page="login",
        fast=fast,
    )


@auth_bp.route("/g-login")
def g_login():
    """Creates authorization link and redirect to Google login services."""
    authorization_url, state = flow_.authorization_url()

    # Store state in database
    oauth_state = State(state=state)
    server_db_.session.add(oauth_state)
    server_db_.session.commit()

    return redirect(authorization_url)


@auth_bp.route("/callback")
def callback():
    try:
        flow_.fetch_token(authorization_response=request.url)
    except Exception as e:
        flash("Authentication failed. Please try again.")
        return redirect(url_for("auth.login"))

    state_in_request = request.args.get("state")
    
    oauth_state = server_db_.session.execute(
        select(State).filter_by(state=state_in_request)
    ).scalar_one_or_none()
    
    if not oauth_state:
        flash("Invalid state. Please try again.")
        return redirect(url_for("auth.login"))
    
    server_db_.session.delete(oauth_state)
    server_db_.session.commit()

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
    user = server_db_.session.execute(
        select(User).filter_by(email=email)
    ).scalar_one_or_none()
    
    if not user:
        session["email"] = email
        return redirect(url_for("auth.set_password"))

    login_user(user=user)
    return redirect(url_for("home.home"))


@auth_bp.route("/set_password", methods=["GET", "POST"])
def set_password():
    set_password_form = SetPasswordForm()
    fast_login_form = FastLoginForm()
    fast = False
    form_type = request.form.get("form_type")
    
    if form_type == "fast_login":
        fast = True
        if fast_login_form.validate_on_submit():
            response, message = fast_login(fast_login_form)
            if response:
                return response
            if message:
                flash(message)
    if form_type == "password":
        if set_password_form.validate_on_submit():
            email = session["email"]
            if not email:
                flash("Session has expired, please try again.")
                return redirect(url_for("auth.request-reset"))
            session.pop("email")
            add_new_user(
                email=email,
                username=email[:8],
                password=set_password_form.password.data,
            )
            user: User = server_db_.session.execute(select(User).filter_by(email=email)).scalar_one_or_none()
            if user:
                login_user(user)
                return redirect(url_for("home.home"))
            else:
                flash("Unexpected error, try again")
                return redirect(url_for("auth.set_password"))
    
    return render_template(
        "/auth/set_password.html",
        set_password_form=set_password_form,
        fast_login_form=fast_login_form,
        page="set_password",
        fast=fast,
    )


@auth_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logs out user, clean up session and redirect to login page."""
    print("* ")
    current_user.remember_me = False
    server_db_.session.commit()
    logout_user()

    session.remember = False
    flash('You have been logged out.')
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Serves register form and redirects to login page
    when successful or redirects to register page when not.
    """
    register_form = RegisterForm()
    fast_login_form = FastLoginForm()
    fast = False
    form_type = request.form.get("form_type")

    if form_type == "fast_login":
        fast = True
        if fast_login_form.validate_on_submit():
            response, message = fast_login(fast_login_form)
            if response:
                return response
            if message:
                flash(message)

    elif form_type == "register":
        if register_form.validate_on_submit():
            add_new_user(
                email=register_form.email.data,
                username=register_form.username.data,
                password=register_form.password.data,
            )
            return redirect(url_for("auth.login"))
        flash("Form failed to validate")

    return render_template(
        "/auth/register.html",
        register_form=register_form,
        fast_login_form=fast_login_form,
        page="register",
        fast=fast,
        )


@auth_bp.route("/request-reset", methods=["GET", "POST"])
def request_reset():
    """
    Serves request reset form and redirects to request reset page
    when successful or not.
    """
    request_reset_form = RequestResetForm()
    fast_login_form = FastLoginForm()
    fast = False
    form_type = request.form.get("form_type")
    
    if form_type == "fast_login":
        fast = True
        if fast_login_form.validate_on_submit():
            response, message = fast_login(fast_login_form)
            if response:
                return response
            if message:
                flash(message)

    elif form_type == "request_reset":
        if request_reset_form.validate_on_submit():
            user: User = server_db_.session.execute(select(User).filter_by(email=request_reset_form.email.data)).scalar_one_or_none()
            if user:
                send_password_reset_email(user)
            flash("If user exists, code has been sent")
            return redirect(url_for("auth.request_reset"))

    return render_template(
        "/auth/request_reset.html",
        request_reset_form=request_reset_form,
        fast_login_form=fast_login_form,
        page="request_reset",
        fast=fast,
        )


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """
    Serves reset password form and redirects to login page
    when successful or reset password page when not.
    """
    reset_password_form = ResetPasswordForm()
    email = confirm_reset_token(token)
    fast_login_form = FastLoginForm()
    fast = False
    form_type = request.form.get("form_type")
    
    if form_type == "fast_login":
        fast = True
        if fast_login_form.validate_on_submit():
            response, message = fast_login(fast_login_form)
            if response:
                return response
            if message:
                flash(message)
                
    # Invalid or expired token
    if not email:
        flash("The reset link is invalid or has expired")
        return redirect(url_for("auth.request_reset"))

    user: User = server_db_.session.execute(select(User).filter_by(email=email)).scalar_one_or_none()

    if form_type == "password":
        if reset_password_form.validate_on_submit():
            change_user_password(user, reset_password_form.password.data)
            flash("Your password has been updated!")
            return redirect(url_for('auth.login'))
        
    # Unsuccessful attempt, re-serve reset page
    return render_template(
        "auth/reset_password.html",
        reset_password_form=reset_password_form,
        fast_login_form=fast_login_form,
        page="reset_password",
        fast=fast,
        )


@auth_bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen_at = datetime.now(CET)
        server_db_.session.commit()
