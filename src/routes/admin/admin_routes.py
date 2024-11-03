from flask import (
    render_template, Blueprint, url_for, redirect, request, flash, session,
    get_flashed_messages
)
from flask_login import login_required, current_user

from src.models.auth_model.auth_mod import User
from src.models.auth_model.auth_mod_utils import (
    get_user_by_email, confirm_authentication_token, process_verification_token,
    process_verification_token
)
from src.routes.admin.admin_forms import (
    NewsForm, VerifyEmailForm, AuthenticationForm, ProfileForm
)
from src.routes.admin.admin_route_utils import (
    add_news_message, process_admin_form, process_profile_picture,
    send_news_notification_email, send_comment_notification_email,
    send_bakery_notification_email
)
from config.settings import (
    EMAIL_VERIFICATION, EMAIL_VERIFIED_MSG, VERIFICATION_SEND_MSG,
    AUTHENTICATION_LINK_ERROR_MSG, USER_ADMIN_REDIRECT, ALL_NEWS_REDIRECT,
    VERIFY_FORM_TYPE, AUTHENTICATION_FORM_TYPE, PROFILE_FORM_TYPE
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
    profile_form: ProfileForm = ProfileForm()
    form_type = request.form.get("form_type")
    
    if request.method == "POST":
        if form_type == VERIFY_FORM_TYPE:
            if verify_email_form.validate_on_submit():
                process_verification_token(email=verify_email_form.email.data,
                                           token_type=EMAIL_VERIFICATION)
                flash(VERIFICATION_SEND_MSG)
                session["flash_type"] = "verify"  # To indicate flash position
                return redirect(url_for(USER_ADMIN_REDIRECT,
                                        _anchor="admin-content"))
            
            session["verify_errors"] = verify_email_form.errors
            
        elif form_type == AUTHENTICATION_FORM_TYPE:
            if authentication_form.validate_on_submit():
                process_admin_form(authentication_form)
                flash("Updated authentication data")
                session["flash_type"] = "authentication"  # To indicate flash position
                session["_anchor"] = "authentication-wrapper"
                return redirect(url_for(USER_ADMIN_REDIRECT,
                                        _anchor="authentication-wrapper"))

            session["authentication_errors"] = authentication_form.errors
        
        elif form_type == PROFILE_FORM_TYPE:
            if profile_form.validate_on_submit():
                process_profile_picture(profile_form)
                process_admin_form(profile_form)
                flash("Updated profile data")
                session["flash_type"] = "profile"  # To indicate flash position
                session["_anchor"] = "profile-wrapper"
                return redirect(url_for(USER_ADMIN_REDIRECT,
                                        _anchor="profile-wrapper"))

            session["profile_errors"] = profile_form.errors
            
    verify_errors = session.pop("verify_errors", None)
    authentication_errors = session.pop("authentication_errors", None)
    profile_errors = session.pop("profile_errors", None)
    
    flash_type = session.pop("flash_type", None)
    profile_form.country.data = current_user.country
    
    return render_template(
        "admin/user_admin.html",
        page="admin",
        verify_email_form=verify_email_form,
        verify_errors=verify_errors,
        
        authentication_form=authentication_form,
        authentication_errors=authentication_errors,
        
        profile_form=profile_form,
        profile_errors=profile_errors,
        
        flash_type=flash_type,
    )


@admin_bp.route("/admin/verify-email/<token>", methods=["GET"])
def verify_email(token):
    """
    Verifies AuthenticationToken for email verification.
    
    """
    email = confirm_authentication_token(token, EMAIL_VERIFICATION)
    if email:
        user: User = get_user_by_email(email)
        if user:
            user.set_email(email)
            user.set_email_verified(True)
            session["flash_type"] = "authentication"
            flash(EMAIL_VERIFIED_MSG)
            return redirect(url_for(USER_ADMIN_REDIRECT))
    
    session["flash_type"] = "verify"
    messages = get_flashed_messages()
    for message in messages:
        print(message)
    
    flash(AUTHENTICATION_LINK_ERROR_MSG)
    return redirect(url_for(USER_ADMIN_REDIRECT, tester=request.url))


@admin_bp.route("/admin/profile-icon/<filename>")
@login_required
def profile_icon(filename):
    current_user.profile_icon = filename
    return redirect(url_for("admin.user_admin", _anchor="profile-wrapper"))


@admin_bp.route("/admin/email")
@login_required
def email():
    title = "We have news!"
    redirect_title = "To read the latest news, "
    notification_settings = "You receive these emails because you signed up for notifications."
    send_news_notification_email(recipient_email="tomaswaverijn@hotmail.com")
    send_comment_notification_email(recipient_email="tomaswaverijn@hotmail.com",
                                   comment_id=1, news_id=2)
    send_bakery_notification_email(recipient_email="tomaswaverijn@hotmail.com",
                                   bakery_id=1, add_update="updated")
    return render_template(
        "admin/email.html",
        title=title,
        redirect_title=redirect_title,
        notification_settings=notification_settings
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
    