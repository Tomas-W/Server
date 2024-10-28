from flask import render_template, Blueprint, url_for, redirect, request, flash, session
from flask_login import login_required

from src.models.auth_mod import get_user_by_email
from src.admin.admin_forms import NewsForm, VerifyEmailForm
from src.admin.admin_route_utils import (add_news_message, confirm_reset_token,
                                          send_verification_email)

admin_bp = Blueprint("admin", __name__)


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


@admin_bp.route("/admin/request-verification", methods=["GET", "POST"])
@login_required
def request_verification():
    verify_email_form: VerifyEmailForm = VerifyEmailForm()
    form_errors = session.pop("form_errors", None) 

    if request.method == "POST":
        if verify_email_form.validate_on_submit():
            send_verification_email(verify_email_form.email.data)
            flash("If email exists, a verification email has been sent!")
            return redirect(url_for("admin.request_verification"))
        session["form_errors"] = verify_email_form.errors

    return render_template(
        "admin/request_verification.html",
        verify_email_form=verify_email_form,
        form_errors=form_errors,
    )
        

@admin_bp.route("/admin/verify-email/<token>", methods=["GET"])
def verify_email(token):
    """Verifies user email."""
    email = confirm_reset_token(token)
    if email:
        user = get_user_by_email(email)
        if user:
            user.set_email_verified(True)
            flash("Your email has been verified!")
            return redirect(url_for("news.all_news"))
        
    flash("Verification link is invalid or has expired.")
    return redirect(url_for("news.all_news"))
