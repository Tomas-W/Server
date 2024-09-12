import os

import requests
from flask import Blueprint, redirect, url_for, request, render_template, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests

from src.extensions import argon2_, limiter_, flow_
from src.auth.forms import LoginForm, RegisterForm, EmailForm, PasswordForm, \
    FastLoginForm
from src.auth.utils import add_new_user, change_password, \
    confirm_reset_token, send_password_reset_email
from src.models.auth_mod import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    """
    Serves home page when logged in,
    else login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    return redirect(url_for("auth.login"))


@auth_bp.route("/fresh")
def base():
    """
    Creates a dummy account after db reset
    and serves login page.
    """
    hashed_password = argon2_.hash("Test123!")
    add_new_user(email="test@gmail.com", username="test",
                 hashed_password=hashed_password,
                 fast_name="test",
                 )

    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter_.limit("60 per hour")
@limiter_.limit("240 per day")
def login():
    """
    Serves fast login form, login form and google login.
    Redirects to home page when login is successful
    or to login page when not.
    """
    login_form = LoginForm()
    fast_login_form = FastLoginForm()
    fast_login = False
    # Request login form
    if request.method == "GET":
        return render_template("/auth/login.html",
                               login_form=login_form,
                               fast_login_form=fast_login_form,
                               fast_login=fast_login)

    # Post login forms
    if request.method == "POST":
        form_type = request.form.get("login_type")

        if form_type == "fast_login":
            fast_login = True
            if fast_login_form.validate_on_submit():
                user: User = User.query.filter_by(
                    fast_name=fast_login_form.fast_name.data).first()
                # Fast login successful
                if user and argon2_.verify(user.fast_code,
                                           fast_login_form.fast_code.data):
                    login_user(user=user)
                    return redirect(url_for("home.home"))
                # User not found or incorrect credentials
                else:
                    flash("Incorrect name or code")
            # Form not validated
            else:
                flash("Incorrect input")

        if form_type == "login":
            if login_form.validate_on_submit():
                user: User = User.query.filter_by(email=login_form.email.data).first()
                # Login successful
                if user and argon2_.verify(user.password,
                                           login_form.password.data):
                    remember = login_form.remember.data
                    fresh = not remember
                    login_user(user=user, remember=remember, fresh=fresh)
                    return redirect(url_for("home.home"))
                # User not found or incorrect credentials
                else:
                    flash("Name and or code incorrect")
            # Form not validated
            else:
                flash("Login fields incomplete")
    # Invalid request
    else:
        flash("Unexpected request.method error")
    # Unsuccessful attempt, re-serve login page
    return render_template("/auth/login.html",
                           login_form=login_form,
                           fast_login_form=fast_login_form,
                           fast_login=fast_login)


@auth_bp.route("/g-login")
@limiter_.limit("60 per hour")
@limiter_.limit("240 per day")
def g_login():
    """
    Creates authorization link
    and redirects to google login services.
    """
    authorization_url, state = flow_.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@auth_bp.route("/callback")
@limiter_.limit("60 per hour")
@limiter_.limit("240 per day")
def callback():
    """
    Serves home page when google authentication was successful
    or login page when not.
    """
    flow_.fetch_token(authorization_response=request.url)
    # Validation failed
    if not session.get("state") == request.args["state"]:
        return redirect(url_for("auth.login"))

    # Gather information
    credentials = flow_.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,  # noqa
        request=token_request,
        audience=os.environ.get("GOOGLE_CLIENT_ID"),
    )
    email = id_info.get("email")
    user: User = User.query.filter_by(email=email).first()
    # New user, add to database
    if not user:
        hashed_password = argon2_.hash("Test123!")
        add_new_user(email=email, username=email[:8],
                     fast_name=email[:5], hashed_password=hashed_password)

    user: User = User.query.filter_by(email=email).first()
    # Login successful
    if user:
        login_user(user=user)
        return redirect(url_for("home.home"))
    # Login unsuccessful
    return redirect(url_for("auth.login"))


@auth_bp.route("/logout", methods=["GET"])
@limiter_.limit("60 per hour")
@limiter_.limit("240 per day")
@login_required
def logout():
    """
    Logs out user, cleans up session
    and redirects to login page.
    """
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter_.limit("60 per hour")
@limiter_.limit("240 per day")
def register():
    """
    Serves register form and redirects to login page
    when successful or redirects to register page when not.
    """
    register_form = RegisterForm()
    # Request register form
    if request.method == "GET":
        return render_template("/auth/register.html",
                               register_form=register_form)

    # Post register form
    if request.method == "POST":
        if register_form.validate_on_submit():

            # Registration successful
            hashed_password = argon2_.hash(register_form.password.data)
            add_new_user(
                email=register_form.email.data,
                username=register_form.username.data,
                hashed_password=hashed_password,
                fast_name="samot",
            )
            return redirect(url_for("auth.login"))
        # Form not validated
        else:
            flash("Form could not be validated")
    # Invalid request
    else:
        flash("Unexpected request.method error")
    # Unsuccessful attempt, re-serve register page
    return render_template("/auth/register.html",
                           register_form=register_form)


@auth_bp.route("/request-reset", methods=["GET", "POST"])
@limiter_.limit("60 per hour")
@limiter_.limit("240 per day")
def request_reset():
    """
    Serves request reset form and redirects to request reset page
    when successful or not.
    """
    email_form = EmailForm()
    # Request request reset form
    if request.method == "GET":
        return render_template("/auth/request_reset.html",
                               email_form=email_form)

    # Post reset form
    if request.method == "POST":
        if email_form.validate_on_submit():
            user = User.query.filter_by(email=email_form.email.data).first()
            # Reset request successful
            if user:
                send_password_reset_email(user)
            flash("If user exists, code has been sent")
            return redirect(url_for("auth.request_reset"))
        # Form not validated
        else:
            flash("Form could not be validated")
    # Invalid request
    else:
        flash("Unexpected request.method error")
    # Unsuccessful attempt, re-serve request reset page
    return render_template("/auth/request_reset.html",
                           email_form=email_form)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
@limiter_.limit("60 per hour")
@limiter_.limit("240 per day")
def reset_password(token):
    """
    Serves reset password form and redirects to login page
    when successful or reset password page when not.
    """
    email = confirm_reset_token(token)
    # Invalid token
    if not email:
        flash("The reset link is invalid or has expired")
        return redirect(url_for("auth.request_reset"))

    user = User.query.filter_by(email=email).first()
    password_form = PasswordForm()
    # Password change successful
    if password_form.validate_on_submit():
        change_password(user, password_form.password.data)
        flash("Your password has been updated!")
        return redirect(url_for('auth.login'))
    # Unsuccessful attempt, re-serve reset page
    return render_template('auth/reset_password.html',
                           password_form=password_form)
