import os

from flask_login import current_user

from src.extensions import server_db_
from src.models.mod_utils import commit_to_db
from src.models.news_model.news_mod import News
from src.routes.admin.admin_routes import AuthenticationForm, ProfileForm
from config.settings import PROFILE_PICTURES_FOLDER


@commit_to_db
def add_news_message(title, content):
    # noinspection PyArgumentList
    new_news = News(
        title=title,
        content=content,
        author=current_user.username
    )
    server_db_.session.add(new_news)


def process_admin_form(form: AuthenticationForm):
    """
    Generic function to process forms on the user_admin-page.
    Takes a form object and updates the current user with the new data.
    If field is not empty and not in skip_fields, the set_<field.name> method is called.
    
    -skip_fields: ["form_type", "submit", "csrf_token"]
    """
    skip_fields = ["form_type", "submit", "csrf_token"]
    for field in form:
        if field.data and field.name not in skip_fields:
            method_name = f"set_{field.name}"
            if hasattr(current_user, method_name):
                method = getattr(current_user, method_name)
                user_entry = getattr(current_user, field.name, None)
                if user_entry != field.data:
                    method(field.data)


def process_profile_picture(form: ProfileForm):
    profile_picture_data = form.profile_picture.data
    form.profile_picture.data = None
    if profile_picture_data:
        current_user.profile_picture = profile_picture_data.filename
        profile_picture_data.save(os.path.join(
            PROFILE_PICTURES_FOLDER,
            profile_picture_data.filename)
        )
