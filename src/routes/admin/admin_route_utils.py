import os

from flask_login import current_user
from flask_wtf import FlaskForm
from src.extensions import server_db_

from src.models.mod_utils import commit_to_db
from config.settings import PROFILE_PICTURES_FOLDER


@commit_to_db
def add_news_message(title, content):
    from src.models.news_model.news_mod import News
    # noinspection PyArgumentList
    new_news = News(
        title=title,
        content=content,
        author=current_user.username
    )
    server_db_.session.add(new_news)


def process_admin_form(form: FlaskForm):
    """
    Generic function to process forms on the admin.user_admin page.
    Takes a form object and updates the current user with the new data.
    If field is not empty and not in skip_fields, the set_<field.name> method is called.
    
    -skip_fields: ["form_type", "submit", "csrf_token"]
    """
    skip_fields = ["form_type", "submit", "csrf_token"]
    
    for field in form:
        if not field.data or field.name in skip_fields or field.data == "":
            continue
        
        method_name = f"set_{field.name}"
        if hasattr(current_user, method_name):
            method = getattr(current_user, method_name)
            
            if isinstance(field.data, bool) or field.type == "BooleanField":
                new_value = field.data if field.data is not None else False
            else:
                new_value = field.data
            user_entry = getattr(current_user, field.name, None)
            if user_entry != new_value:
                method(new_value)


def process_profile_picture(form: FlaskForm):
    """
    Takes the profile picture data from the form,
      saves its path to the database, stores the file in the UPLOAD_FOLDER
      and removes the profile picture from the form to be processed further.
    """
    profile_picture_data = form.profile_picture.data
    form.profile_picture.data = None
    if profile_picture_data:
        current_user.profile_picture = profile_picture_data.filename
        profile_picture_data.save(os.path.join(
            PROFILE_PICTURES_FOLDER,
            profile_picture_data.filename)
        )
