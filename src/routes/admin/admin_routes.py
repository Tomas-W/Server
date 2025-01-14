from flask import (
    render_template, Blueprint, url_for, redirect, request, flash, session
)
from flask_login import login_required, current_user

from src.models.auth_model.auth_mod import User

from src.models.auth_model.auth_mod_utils import (
    get_user_by_email, confirm_authentication_token,
    start_verification_process, delete_authentication_token
)
from src.routes.admin.admin_route_utils import (
    process_admin_form, process_profile_picture, clean_up_form_fields,
    process_new_email_address
)
from src.routes.admin.admin_forms import (
    VerifyEmailForm, AuthenticationForm, ProfileForm, NotificationsForm
)
from config.settings import (
    SERVER, MESSAGE, REDIRECT, TEMPLATE, FORM
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
        if form_type == FORM.VERIFY:
            if verify_email_form.validate_on_submit():
                start_verification_process(email=verify_email_form.email.data,
                                           token_type=SERVER.EMAIL_VERIFICATION)
                flash(MESSAGE.VERIFICATION_SEND)
                session["flash_type"] = "verify"  # To indicate flash position
                return redirect(url_for(REDIRECT.USER_ADMIN_REDIRECT,
                                        _anchor="admin-content"))
            
            session["verify_email_errors"] = verify_email_form.errors
            
        elif form_type == FORM.AUTHENTICATION:
            if authentication_form.validate_on_submit():
                if clean_up_form_fields(authentication_form):
                    flash(MESSAGE.NO_CHANGES)

                if process_new_email_address(authentication_form):
                    flash(MESSAGE.CHECK_INBOX)
                
                if process_admin_form(authentication_form):
                    flash(MESSAGE.UPDATED_DATA)
                                
                session["flash_type"] = "authentication"  # To indicate flash position
                session["_anchor"] = "authentication-wrapper"
                return redirect(url_for(REDIRECT.USER_ADMIN,
                                        _anchor="authentication-wrapper"))

            session["authentication_errors"] = authentication_form.errors
            
        
        elif form_type == FORM.PROFILE:
            if profile_form.validate_on_submit():
                if clean_up_form_fields(profile_form):
                    flash(MESSAGE.NO_CHANGES)
                    
                if process_profile_picture(profile_form):
                    flash(MESSAGE.UPDATED_DATA)
                else:
                    flash(MESSAGE.NO_CHANGES)
                    
                if process_admin_form(profile_form):
                    flash(MESSAGE.UPDATED_DATA)
                else:
                    flash(MESSAGE.NO_CHANGES)
                    
                session["flash_type"] = "profile"  # To indicate flash position
                session["_anchor"] = "profile-wrapper"
                return redirect(url_for(REDIRECT.USER_ADMIN,
                                        _anchor="profile-wrapper"))
            
            session["profile_errors"] = profile_form.errors
            session["_anchor"] = "profile-wrapper"
        
        elif form_type == FORM.NOTIFICATIONS:
            if notifications_form.validate_on_submit():
                if clean_up_form_fields(notifications_form):
                    flash(MESSAGE.NO_CHANGES)
                    
                if process_admin_form(notifications_form):
                    flash(MESSAGE.UPDATED_DATA)
                else:
                    flash(MESSAGE.NO_CHANGES)
                    
                session["flash_type"] = "notifications"  # To indicate flash position
                session["_anchor"] = "notification-settings-wrapper"
                return redirect(url_for(REDIRECT.USER_ADMIN,
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
        TEMPLATE.USER_ADMIN,
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


@admin_bp.route("/admin/verify-email/<token>", methods=["GET"])
def verify_email(token):
    """
    Verifies AuthenticationToken for email verification.
    """
    email = confirm_authentication_token(token, SERVER.EMAIL_VERIFICATION)
    if email:
        user: User = get_user_by_email(email, new_email=True)

        if user:
            user.set_email(email)
            user.reset_new_email()
            user.set_email_verified(True)
            delete_authentication_token(SERVER.EMAIL_VERIFICATION, token)
            session["flash_type"] = "authentication"
            flash(MESSAGE.EMAIL_VERIFIED)
            return redirect(url_for(REDIRECT.USER_ADMIN))
    
    session["flash_type"] = "verify"
    flash(MESSAGE.AUTHENTICATION_LINK_ERROR)

    return redirect(url_for(
        REDIRECT.USER_ADMIN,
    ))


@admin_bp.route("/admin/profile-icon/<filename>")
@login_required
def profile_icon(filename):
    """
    Updates or loads profile icon.
    """
    if not filename == current_user.profile_icon:
        current_user.set_profile_icon(filename)
        session["flash_type"] = "profile"
        flash("Updated profile icon")
    
    session["flash_type"] = "profile"
    flash(MESSAGE.INVALID_PROFILE_ICON)    
    return redirect(url_for(
        REDIRECT.USER_ADMIN,
        _anchor="profile-wrapper"
    ))


@admin_bp.route("/admin/email")
@login_required
def email():
    title = "We have news!"
    redirect_title = "To read the latest news, "
    notification_settings = "You receive these emails because you signed up for notifications."
    
    return render_template(
        TEMPLATE.EMAIL,
        title=title,
        redirect_title=redirect_title,
        notification_settings=notification_settings
    )


