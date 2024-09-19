import os

import requests
from flask import Blueprint, redirect, url_for, request, render_template, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from google.oauth2 import id_token
from pip._vendor import cachecontrol  # noqa
import google.auth.transport.requests

from src.extensions import argon2_, flow_, server_db_
from src.auth.forms import (LoginForm, RegisterForm, EmailForm, PasswordForm,
                            FastLoginForm)
from src.auth.route_utils import (add_new_user, change_password, confirm_reset_token,
                                  send_password_reset_email, fast_login, normal_login)
from src.models.auth_mod import User

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
    hashed_password = argon2_.hash("Test123!")
    add_new_user(
        email="test@gmail.com",
        username="test",
        hashed_password=hashed_password,
    )
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Serves fast login form, login form and google login.
    Redirects to home page when login is successful or to login page when not.
    """
    login_form = LoginForm()
    fast_login_form = FastLoginForm()
    fast = False

    form_type = request.form.get("login_type")
    if form_type == "fast_login":
        if fast_login_form.validate_on_submit():
            response, message = fast_login(fast_login_form)
            if response:
                return response
            if message:
                flash(message)

    elif form_type == "login":
        if login_form.validate_on_submit():
            response, message = normal_login(login_form)
            if response:
                return response
            if message:
                flash(message)

    return render_template(
        "/auth/login.html",
        login_form=login_form,
        fast_login_form=fast_login_form,
        fast=fast,
    )


@auth_bp.route("/g-login")
def g_login():
    """Creates authorization link and redirect to Google login services."""
    authorization_url, state = flow_.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@auth_bp.route("/callback")
def callback():
    """
    Serves home page when google authentication was successful
    or login page when not.
    """
    flow_.fetch_token(authorization_response=request.url)
    if not session.get("state") == request.args["state"]:
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
    user: User = User.query.filter_by(email=email).first()
    # New user, ask for password
    if not user:
        session["email"] = email
        return redirect(url_for("auth.set_password"))

    login_user(user=user)
    return redirect(url_for("home.home"))


@auth_bp.route("/set_password", methods=["GET", "POST"])
def set_password():
    password_form = PasswordForm()

    if password_form.validate_on_submit():
        email = session["email"]
        if not email:
            flash("Session has expired, please try again.")
            return redirect(url_for("auth.request-reset"))
        session.pop("email")
        hashed_password = argon2_.hash(password_form.password.data)
        add_new_user(
            email=email,
            username=email[:8],
            hashed_password=hashed_password,
        )
        user: User = User.query.filter_by(email=email).first()
        if user:
            login_user(user)
            return redirect(url_for("home.home"))
        else:
            flash("Unexpected error, try again")
            return redirect(url_for("auth.set_password"))
    return render_template(
        "/auth/set_password.html",
        password_form=password_form,
    )


@auth_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logs out user, clean up session and redirect to login page."""
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

    if register_form.validate_on_submit():
        hashed_password = argon2_.hash(register_form.password.data)
        add_new_user(
            email=register_form.email.data,
            username=register_form.username.data,
            hashed_password=hashed_password,
        )
        return redirect(url_for("auth.login"))

    return render_template("/auth/register.html", register_form=register_form)


@auth_bp.route("/request-reset", methods=["GET", "POST"])
def request_reset():
    """
    Serves request reset form and redirects to request reset page
    when successful or not.
    """
    email_form = EmailForm()

    if email_form.validate_on_submit():
        user = User.query.filter_by(email=email_form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("If user exists, code has been sent")
        return redirect(url_for("auth.request_reset"))

    return render_template("/auth/request_reset.html", email_form=email_form)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """
    Serves reset password form and redirects to login page
    when successful or reset password page when not.
    """
    email = confirm_reset_token(token)
    # Invalid or expired token
    if not email:
        flash("The reset link is invalid or has expired")
        return redirect(url_for("auth.request_reset"))

    user = User.query.filter_by(email=email).first()
    password_form = PasswordForm()

    if password_form.validate_on_submit():
        change_password(user, password_form.password.data)
        flash("Your password has been updated!")
        return redirect(url_for('auth.login'))
    # Unsuccessful attempt, re-serve reset page
    return render_template('auth/reset_password.html',
                           password_form=password_form)
