import os

from flask import (
    abort,
    flash,
    session,
)
from flask_login import current_user
from flask_wtf import FlaskForm

from src.extensions import logger

from src.models.auth_model.auth_mod_utils import start_verification_process

from config.settings import (
    DIR,
    MESSAGE,
    SERVER,
)


def clean_up_form_fields(form: FlaskForm) -> bool:
    """
    Deletes fields that are empty, None, or in delete_fields from the form.
    
    Returns True if no fields are left in the form, False otherwise.
    """
    delete_fields = {"form_type", "submit", "csrf_token"}
    empty_fields_to_delete = []

    for field in form:
        if field.name == "country":
            if field.data == current_user.country:
                empty_fields_to_delete.append(field.name)

        if field.data is None or field.data == "":
            empty_fields_to_delete.append(field.name)


    all_fields_to_delete = delete_fields.union(empty_fields_to_delete)
    logger.info(f"[DEBUG] All fields to delete: {all_fields_to_delete}")
    for field_name in all_fields_to_delete:
        if field_name in form._fields:
            del form._fields[field_name]
    return len(form._fields) == 0


def process_admin_form(form: FlaskForm) -> bool:
    """
    Generic function to process forms on the admin.user_admin page.
    Takes a form object and updates the current user with the new data by
      calling the set_<field.name> method.
      
    Returns True if any fields were updated, False otherwise.
    """
    set_value_fields = ["country", "news_notifications", "comment_notifications",
                        "bakery_notifications"]
    for field_name in set_value_fields:
        if field_name in form and getattr(current_user, field_name, None) == form[field_name].data:
            del form._fields[field_name]

    has_updated = False
    for field in form:
        method_name = f"set_{field.name}"
        if hasattr(current_user, method_name):
            method = getattr(current_user, method_name)

            user_data = getattr(current_user, field.name, None)
            if user_data != field.data:
                method(field.data)
                has_updated = True
    return has_updated


def process_new_email_address(form: FlaskForm) -> bool:
    """
    Takes the email address from the form,
      sends a verification token if it is different from the current email address,
      and returns True if a verification token was sent, False otherwise.
    """
    if not form.email.data:
        return False
    
    new_email_address = form.email.data
    if new_email_address != current_user.email:
        current_user.set_new_email(new_email_address)
        del form._fields["email"]
        start_verification_process(email=new_email_address,
                                   token_type=SERVER.EMAIL_VERIFICATION,
                                   allow_unknown=True)
        return True
    return False

def process_profile_picture(form: FlaskForm) -> bool:
    """
    Takes the profile picture data from the form,
    saves its path to the database, stores the file in the UPLOAD_FOLDER.
    
    Returns:
        bool: True if profile picture was updated, False otherwise
    """
    if not form.profile_picture.data:
        if "profile_picture" in form._fields:
            del form._fields["profile_picture"]
        return False

    profile_picture_data = form.profile_picture.data
    if profile_picture_data.filename == current_user.profile_picture:
        del form._fields["profile_picture"]
        return False
    
    try:
        # Generate filename with user ID to ensure uniqueness
        filename = f"{current_user.id}_{profile_picture_data.filename}"
        file_path = os.path.join(DIR.PROFILE_PICS, filename)
        
        # Save file to disk first
        profile_picture_data.save(file_path)
        
        # Then save only the filename to the database
        current_user.set_profile_picture(profile_picture_data.filename)
        
        del form._fields["profile_picture"]
        return True
        
    except FileNotFoundError:
        flash(MESSAGE.PROFILE_PICTURE_ERROR)
        logger.error("[USER] Profile picture folder not found")
        
    except PermissionError as e:
        logger.critical(f"[SYS] PROFILE PICTURE PERMISSION ERROR: {e}")
        abort(500)
    except Exception as e:
        logger.error(f"[SYS] PROFILE PICTURE ERROR: {e}")
        abort(500)
    
    if "profile_picture" in form._fields:
        del form._fields["profile_picture"]
    return False

