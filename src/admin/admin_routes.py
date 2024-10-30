from flask import render_template, Blueprint, url_for, redirect, request, flash, session
from flask_login import login_required

from src.models.auth_model.auth_mod import get_user_by_email
from src.models.auth_model.auth_mod_utils import confirm_authentication_token, process_verification_token
from src.admin.admin_forms import (NewsForm, VerifyEmailForm, AuthenticationForm)
from src.admin.admin_route_utils import (add_news_message)

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/user-admin", methods=["GET", "POST"])
@login_required
def user_admin():
    verify_email_form: VerifyEmailForm = VerifyEmailForm()
    authentication_form: AuthenticationForm = AuthenticationForm()
    
    form_type = request.form.get("form_type")
    
    if request.method == "POST":
        if form_type == "verify":
            if verify_email_form.validate_on_submit():
                process_verification_token(verify_email_form.email.data, "email_verification")
                flash("If email exists, a verification email has been sent!")
                session["flash_type"] = "verify"
                return redirect(url_for("admin.user_admin"))
            
            session["verify_errors"] = verify_email_form.errors
            
        elif form_type == "authentication":
            if authentication_form.validate_on_submit():
                for field in authentication_form:
                    if field.data:
                        pass
                        
                flash("Authentication successful!")
                session["flash_type"] = "authentication"
                return redirect(url_for("admin.user_admin"))

            session["authentication_errors"] = authentication_form.errors
            
    verify_errors = session.pop("verify_errors", None)
    authentication_errors = session.pop("authentication_errors", None)
    flash_type = session.pop("flash_type", None)
    
    return render_template(
        "admin/user_admin.html",
        page="admin",
        verify_email_form=verify_email_form,
        authentication_form=authentication_form,
        verify_errors=verify_errors,
        authentication_errors=authentication_errors,
        flash_type=flash_type,
    )


@admin_bp.route("/admin/add-news", methods=["GET", "POST"])
@login_required
def add_news():
    news_form: NewsForm = NewsForm()
    
    if request.method == "POST":
        if news_form.validate_on_submit():
            add_news_message(news_form.title.data,
                             news_form.content.data)
            return redirect(url_for("news.all_news"))
        session["news_errors"] = news_form.errors

    news_errors = session.pop("news_errors", None)
    return render_template(
        "admin/add_news.html",
        page="add_news",
        news_form=news_form,
        news_errors=news_errors,
    )


@admin_bp.route("/admin/verify-email/<token>", methods=["GET"])
def verify_email(token):
    """Verifies user email."""
    email = confirm_authentication_token(token, "email_verification")
    if email:
        user = get_user_by_email(email)
        if user:
            user.set_email(email)
            user.set_email_verified(True)
            session["flash_type"] = "authentication"
            flash("Your email has been verified!")
            return redirect(url_for("admin.user_admin"))
    
    session["flash_type"] = "verify"
    flash("Verification link is invalid or has expired.")
    return redirect(url_for("admin.user_admin"))
