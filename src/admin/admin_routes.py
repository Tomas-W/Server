from flask import render_template, Blueprint, url_for, redirect, request, flash, session
from flask_login import login_required, current_user

from src.models.auth_mod import get_user_by_email
from src.admin.admin_forms import (NewsForm, VerifyEmailForm, AuthenticationForm)
from src.admin.admin_route_utils import (add_news_message, confirm_reset_token,
                                          send_verification_email)

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/user-admin", methods=["GET", "POST"])
@login_required
def user_admin():
    verify_email_form: VerifyEmailForm = VerifyEmailForm()
    # verify_email_form.email.data = current_user.email
    
    authentication_form: AuthenticationForm = AuthenticationForm()
    
    verify_errors = None
    authentication_errors = None
    flash_type = session.pop("flash_type", None)
    form_type = request.form.get("form_type")
    
    if request.method == "POST":
        if form_type == "verify":
            if verify_email_form.validate_on_submit():
                send_verification_email(verify_email_form.email.data)
                flash("If email exists, a verification email has been sent!")
                session["flash_type"] = "verify"
                return redirect(url_for("admin.user_admin"))
            
            verify_errors = verify_email_form.errors
            
        elif form_type == "authentication":
            if authentication_form.validate_on_submit():
                print("*****************")
                print(f"authentication_form type: {type(authentication_form.fast_code.data)}")
                print("*****************")
                
                for field in authentication_form:
                    if field.data:
                        pass
                        
                
                flash("Authentication successful!")
                session["flash_type"] = "authentication"
                return redirect(url_for("admin.user_admin"))

            authentication_errors = authentication_form.errors
    
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
    form_errors = session.pop("form_errors", None)
    
    if request.method == "POST":
        if news_form.validate_on_submit():
            add_news_message(news_form.title.data,
                             news_form.content.data)
            return redirect(url_for("news.all_news"))
        session["form_errors"] = news_form.errors

    return render_template(
        "admin/add_news.html",
        page="add_news",
        news_form=news_form,
        form_errors=form_errors,
    )


@admin_bp.route("/admin/verify-email/<token>", methods=["GET"])
def verify_email(token):
    """Verifies user email."""
    email = confirm_reset_token(token)
    if email:
        user = get_user_by_email(email)
        if user:
            user.email = email
            user.set_email_verified(True)
            flash("Your email has been verified!")
            return redirect(url_for("admin.user_admin"))
        
    flash("Verification link is invalid or has expired.")
    return redirect(url_for("admin.user_admin"))
