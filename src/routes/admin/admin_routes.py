from flask import (
    render_template, Blueprint, url_for, redirect, request, flash, session
)
from flask_login import login_required

from src.models.auth_model.auth_mod_utils import get_user_by_email
from src.models.auth_model.auth_mod_utils import (
    confirm_authentication_token, process_verification_token, process_verification_token
)
from src.routes.admin.admin_forms import (
    NewsForm, VerifyEmailForm, AuthenticationForm
)
from src.routes.admin.admin_route_utils import add_news_message
from config.settings import (
    EMAIL_VERIFICATION, EMAIL_VERIFIED_MSG, VERIFICATION_SEND_MSG,
    AUTHENTICATION_LINK_ERROR_MSG, USER_ADMIN_REDIRECT, ALL_NEWS_REDIRECT,
    VERIFY_FORM_TYPE, AUTHENTICATION_FORM_TYPE
)

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/user-admin", methods=["GET", "POST"])
@login_required
def user_admin():
    """
    Asks user to verify email before allowing them to update their data.
    Updates only allowed during a fresh session.
    
    - VerifyEmailForm
    - AuthenticationForm
    - ProfileForm
    - NotificationsForm
    - SettingsForm
    """
    verify_email_form: VerifyEmailForm = VerifyEmailForm()
    authentication_form: AuthenticationForm = AuthenticationForm()
    form_type = request.form.get("form_type")
    
    if request.method == "POST":
        if form_type == VERIFY_FORM_TYPE:
            if verify_email_form.validate_on_submit():
                process_verification_token(email=verify_email_form.email.data,
                                           token_type=EMAIL_VERIFICATION)
                flash(VERIFICATION_SEND_MSG)
                session["flash_type"] = "verify"  # To indicate flash position
                return redirect(url_for(USER_ADMIN_REDIRECT))
            
            session["verify_errors"] = verify_email_form.errors
            
        elif form_type == AUTHENTICATION_FORM_TYPE:
            if authentication_form.validate_on_submit():
                flash("Temporary message")
                session["flash_type"] = "authentication"  # To indicate flash position
                return redirect(url_for(USER_ADMIN_REDIRECT))

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
    """
    Adds a news message to the database.
    
    - NewsForm
    """
    news_form: NewsForm = NewsForm()
    
    if request.method == "POST":
        if news_form.validate_on_submit():
            add_news_message(news_form.title.data,
                             news_form.content.data)
            return redirect(url_for(ALL_NEWS_REDIRECT))
        
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
    """
    Verifies AuthenticationToken for email verification.
    
    """
    email = confirm_authentication_token(token, EMAIL_VERIFICATION)
    if email:
        user = get_user_by_email(email)
        if user:
            user.set_email(email)
            user.set_email_verified(True)
            session["flash_type"] = "authentication"
            flash(EMAIL_VERIFIED_MSG)
            return redirect(url_for(USER_ADMIN_REDIRECT))
    
    session["flash_type"] = "verify"
    
    flash(AUTHENTICATION_LINK_ERROR_MSG)
    return redirect(url_for(USER_ADMIN_REDIRECT))
