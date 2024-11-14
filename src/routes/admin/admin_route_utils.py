import os

from flask_login import current_user
from flask_wtf import FlaskForm

from src.extensions import server_db_
from src.models.auth_model.auth_mod_utils import process_verification_token
from src.routes.admin.admin_forms import AddNewsForm
from config.settings import PROFILE_PICTURES_FOLDER, EMAIL_VERIFICATION


def add_news_message(form: AddNewsForm, grid_cols: list[str], grid_rows: list[str],
                     info_cols: list[str], info_rows: list[str]) -> None:
    from src.models.news_model.news_mod import News
    # noinspection PyArgumentList
    new_news = News(
        title=form.title.data,
        header=form.header.data,
        code=form.code.data,
        important=form.important.data,
        grid_cols=grid_cols,
        grid_rows=grid_rows,
        info_cols=info_cols,
        info_rows=info_rows,
        author=form.author.data
    )
    server_db_.session.add(new_news)
    server_db_.session.commit()


def clean_up_form_fields(form: FlaskForm) -> bool:
    """
    Deletes fields that are empty, None, or in delete_fields from the form.
    
    Returns True if no fields are left in the form, False otherwise.
    """
    delete_fields = {"form_type", "submit", "csrf_token"}
    empty_fields_to_delete = []

    for field in form:   
        if field.data is None or field.data == "":
            empty_fields_to_delete.append(field.name)

    all_fields_to_delete = delete_fields.union(empty_fields_to_delete)
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
            print(f"*****NOT UPDATING {field_name}*******")
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
        current_user.new_email = new_email_address
        del form._fields["email"]
        process_verification_token(email=new_email_address,
                                   token_type=EMAIL_VERIFICATION)
        return True
    return False

def process_profile_picture(form: FlaskForm) -> None:
    """
    Takes the profile picture data from the form,
      saves its path to the database, stores the file in the UPLOAD_FOLDER
      and removes the profile picture from the form to be processed further.
    """
    if form.profile_picture.data:
        current_user.set_profile_picture(form.profile_picture.data.filename)
        profile_picture_data = form.profile_picture.data
        if profile_picture_data:
            profile_picture_data.save(os.path.join(
                PROFILE_PICTURES_FOLDER,
                f"{current_user.id}_{profile_picture_data.filename}",
            ))
        del form["profile_picture"]
        return True
    
    del form["profile_picture"]
    return False

