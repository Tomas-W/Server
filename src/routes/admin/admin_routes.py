from flask import (
    render_template, Blueprint, url_for, redirect, request, flash, session
)
from flask_login import login_required, current_user

from src.models.auth_model.auth_mod import User
from src.utils.logger import log_routes, log_function
from src.extensions import logger

from src.models.auth_model.auth_mod_utils import (
    get_user_by_email, confirm_authentication_token,
    start_verification_process, admin_required, delete_authentication_token
)
from src.routes.admin.admin_route_utils import (
    add_news_message, process_admin_form, process_profile_picture, clean_up_form_fields,
    process_new_email_address
)
from src.routes.admin.admin_forms import (
    AddNewsForm, VerifyEmailForm, AuthenticationForm, ProfileForm, NotificationsForm
)
from config.settings import (
    EMAIL_VERIFICATION, EMAIL_VERIFIED_MSG, VERIFICATION_SEND_MSG,
    AUTHENTICATION_LINK_ERROR_MSG, USER_ADMIN_REDIRECT, ALL_NEWS_REDIRECT,
    VERIFY_FORM_TYPE, AUTHENTICATION_FORM_TYPE, PROFILE_FORM_TYPE,
    NOTIFICATIONS_FORM_TYPE, EMAIL_TEMPLATE, ADD_NEWS_TEMPLATE, USER_ADMIN_TEMPLATE,
    E_404_TEMPLATE
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
    form_type = request.form.get("form_type")
    verify_email_form: VerifyEmailForm = VerifyEmailForm()
    authentication_form: AuthenticationForm = AuthenticationForm()
    profile_form: ProfileForm = ProfileForm()
    notifications_form: NotificationsForm = NotificationsForm()
       
    if request.method == "POST":
        if form_type == VERIFY_FORM_TYPE:
            if verify_email_form.validate_on_submit():
                start_verification_process(email=verify_email_form.email.data,
                                           token_type=EMAIL_VERIFICATION)
                flash(VERIFICATION_SEND_MSG)
                session["flash_type"] = "verify"  # To indicate flash position
                return redirect(url_for(USER_ADMIN_REDIRECT,
                                        _anchor="admin-content"))
            
            session["verify_email_errors"] = verify_email_form.errors
            
        elif form_type == AUTHENTICATION_FORM_TYPE:
            if authentication_form.validate_on_submit():
                logger.info("Authentication form submitted")

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
                if clean_up_form_fields(profile_form):
                    flash("No changes made")

                if process_profile_picture(profile_form):
                    flash("Updated profile picture")
                    
                if process_admin_form(profile_form):
                    flash("Updated profile data")
                    
                session["flash_type"] = "profile"  # To indicate flash position
                session["_anchor"] = "profile-wrapper"
                return redirect(url_for(USER_ADMIN_REDIRECT,
                                        _anchor="profile-wrapper"))
            
            session["profile_errors"] = profile_form.errors
            session["_anchor"] = "profile-wrapper"
        
        elif form_type == NOTIFICATIONS_FORM_TYPE:
            if notifications_form.validate_on_submit():
                if clean_up_form_fields(notifications_form):
                    flash("No changes made")
                    
                if process_admin_form(notifications_form):
                    flash("Updated notification settings")
                else:
                    flash("No changes made")
                    
                session["flash_type"] = "notifications"  # To indicate flash position
                session["_anchor"] = "notification-settings-wrapper"
                return redirect(url_for(USER_ADMIN_REDIRECT,
                                        _anchor="notifications-wrapper"))
            
            session["_anchor"] = "notifications-wrapper"
    
    verify_email_errors = session.pop("verify_email_errors", None)
    authentication_errors = session.pop("authentication_errors", None)
    profile_errors = session.pop("profile_errors", None)
    
    profile_form.country.data = current_user.country
    profile_form.profile_picture.data = current_user.profile_picture
    notifications_form.news_notifications.data = current_user.news_notifications
    notifications_form.comment_notifications.data = current_user.comment_notifications
    notifications_form.bakery_notifications.data = current_user.bakery_notifications

    flash_type = session.pop("flash_type", None)
    _anchor = session.pop("_anchor", None)

    return render_template(
        USER_ADMIN_TEMPLATE,
        verify_email_form=verify_email_form,
        verify_email_errors=verify_email_errors,
        
        authentication_form=authentication_form,
        authentication_errors=authentication_errors,
        
        profile_form=profile_form,
        profile_errors=profile_errors,
        
        notification_settings_form=notifications_form,
        
        flash_type=flash_type,
        _anchor=_anchor,
    )


@admin_bp.route("/admin/add-news", methods=["GET", "POST"])
@login_required
@admin_required
def add_news():
    add_news_form: AddNewsForm = AddNewsForm()
    
    if request.method == "POST":
        if add_news_form.validate_on_submit():
            grid_cols = request.form.getlist("table_cols[]")
            grid_rows = [row.replace("\n", "|") for row in request.form.getlist("table_rows[]")]
            info_cols = request.form.getlist("alinea_headers[]")
            info_rows = request.form.getlist("alinea_contents[]")
            add_news_message(add_news_form,
                             grid_cols,
                             grid_rows,
                             info_cols,
                             info_rows)
            return redirect(url_for(ALL_NEWS_REDIRECT))
        
        session["news_errors"] = add_news_form.errors

    add_news_errors = session.pop("add_news_errors", None)
    
    return render_template(
        ADD_NEWS_TEMPLATE,
        add_news_form=add_news_form,
        add_news_errors=add_news_errors
    )


@admin_bp.route("/admin/verify-email/<token>", methods=["GET"])
def verify_email(token):
    """
    Verifies AuthenticationToken for email verification.
    """
    email = confirm_authentication_token(token, EMAIL_VERIFICATION)
    if email:
        user: User = get_user_by_email(email, new_email=True)

        if user:
            user.set_email(email)
            user.reset_new_email()
            user.set_email_verified(True)
            delete_authentication_token(EMAIL_VERIFICATION, token)
            session["flash_type"] = "authentication"
            flash(EMAIL_VERIFIED_MSG)
            return redirect(url_for(USER_ADMIN_REDIRECT))
    
    logger.warning(f"Email token not confirmed {log_function()} {log_routes()}")
    session["flash_type"] = "verify"
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
        USER_ADMIN_REDIRECT,
        _anchor="profile-wrapper"
    ))


@admin_bp.route("/admin/email")
@login_required
def email():
    title = "We have news!"
    redirect_title = "To read the latest news, "
    notification_settings = "You receive these emails because you signed up for notifications."
    
    return render_template(
        EMAIL_TEMPLATE,
        title=title,
        redirect_title=redirect_title,
        notification_settings=notification_settings
    )


