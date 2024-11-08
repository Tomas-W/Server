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
from src.routes.admin.admin_route_utils import (
    add_news_message, process_admin_form, process_profile_picture, clean_up_form_fields,
    process_new_email_address
)
from src.routes.admin.admin_forms import (
    NewsForm, VerifyEmailForm, AuthenticationForm, ProfileForm, NotificationSettingsForm
)
from config.settings import (
    EMAIL_VERIFICATION, EMAIL_VERIFIED_MSG, VERIFICATION_SEND_MSG,
    AUTHENTICATION_LINK_ERROR_MSG, USER_ADMIN_REDIRECT, ALL_NEWS_REDIRECT,
    VERIFY_FORM_TYPE, AUTHENTICATION_FORM_TYPE, PROFILE_FORM_TYPE,
    NOTIFICATION_SETTINGS_FORM_TYPE
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
    notification_settings_form: NotificationSettingsForm = NotificationSettingsForm()
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
            
            session["verify_email_errors"] = verify_email_form.errors
            
        elif form_type == AUTHENTICATION_FORM_TYPE:
            if authentication_form.validate_on_submit():

                if clean_up_form_fields(authentication_form):
                    flash("No changes made")

                if process_new_email_address(authentication_form):
                    flash("Check inbox for email verification!")
                
                if process_admin_form(authentication_form):
                    flash("Updated authentication data")
                                
                session["flash_type"] = "authentication"  # To indicate flash position
                session["_anchor"] = "authentication-wrapper"
                return redirect(url_for(USER_ADMIN_REDIRECT,
                                        _anchor="authentication-wrapper"))

            session["authentication_errors"] = authentication_form.errors
        
        elif form_type == PROFILE_FORM_TYPE:
            if profile_form.validate_on_submit():
                clean_up_form_fields(profile_form)
                process_profile_picture(profile_form)
                process_admin_form(profile_form)
                flash("Updated profile data")
                session["flash_type"] = "profile"  # To indicate flash position
                session["_anchor"] = "profile-wrapper"
                return redirect(url_for(USER_ADMIN_REDIRECT,
                                        _anchor="profile-wrapper"))

            session["profile_errors"] = profile_form.errors
        
        elif form_type == NOTIFICATION_SETTINGS_FORM_TYPE:
            if notification_settings_form.validate_on_submit():
                clean_up_form_fields(notification_settings_form)
                process_admin_form(notification_settings_form)
                flash("Updated notification settings")
                session["flash_type"] = "notifications"  # To indicate flash position
                session["_anchor"] = "notification-settings-wrapper"
                return redirect(url_for(USER_ADMIN_REDIRECT,
                                        _anchor="notifications-wrapper"))
                
    verify_email_errors = session.pop("verify_email_errors", None)
    authentication_errors = session.pop("authentication_errors", None)
    profile_errors = session.pop("profile_errors", None)
    
    profile_form.country.data = current_user.country
    notification_settings_form.news_notifications.data = current_user.news_notifications
    notification_settings_form.comment_notifications.data = current_user.comment_notifications
    notification_settings_form.bakery_notifications.data = current_user.bakery_notifications

    flash_type = session.pop("flash_type", None)

    return render_template(
        "admin/user_admin.html",
        page=["admin"],
        verify_email_form=verify_email_form,
        verify_email_errors=verify_email_errors,
        
        authentication_form=authentication_form,
        authentication_errors=authentication_errors,
        
        profile_form=profile_form,
        profile_errors=profile_errors,
        
        notification_settings_form=notification_settings_form,
        
        flash_type=flash_type,
    )


@admin_bp.route("/admin/verify-email/<token>", methods=["GET"])
def verify_email(token):
    """
    Verifies AuthenticationToken for email verification.
    """
    email = confirm_authentication_token(token, EMAIL_VERIFICATION)
    if email:
        user: User = get_user_by_email(current_user.email)
        if user:
            user.set_email(email)
            user.reset_new_email()
            user.set_email_verified(True)
            session["flash_type"] = "authentication"
            flash(EMAIL_VERIFIED_MSG)
            return redirect(url_for(USER_ADMIN_REDIRECT))
    
    if not current_user.email_verified:
        session["flash_type"] = "verify"
        flash(AUTHENTICATION_LINK_ERROR_MSG)
    else:
        session["flash_type"] = "authentication"
        flash(AUTHENTICATION_LINK_ERROR_MSG)
    
    return redirect(url_for(
        USER_ADMIN_REDIRECT,
    ))


@admin_bp.route("/admin/profile-icon/<filename>")
@login_required
def profile_icon(filename):
    """
    Updates or loads profile icon.
    """
    current_user.profile_icon = filename
    session["flash_type"] = "profile"
    flash("Updated profile icon")
        
    return redirect(url_for(
        "admin.user_admin",
        _anchor="profile-wrapper"
    ))


@admin_bp.route("/admin/email")
@login_required
def email():
    title = "We have news!"
    redirect_title = "To read the latest news, "
    notification_settings = "You receive these emails because you signed up for notifications."
    
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
        page=["add_news"],
        news_form=news_form,
        news_errors=news_errors,
    )
    