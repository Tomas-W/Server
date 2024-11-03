import os

from flask_login import current_user
from flask_mail import Message
from src.extensions import server_db_, mail_
from src.models.mod_utils import commit_to_db
from src.models.news_model.news_mod import News
from src.routes.admin.admin_routes import AuthenticationForm, ProfileForm
from config.settings import PROFILE_PICTURES_FOLDER
from flask import render_template, url_for


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



class NotificationEmail:
    def __init__(self, type_: str):
        if type_ == "news":
            self.subject = "Read the lastest news"
            self.message = "A new news post has been added."


def send_news_notification_email(recipient_email: str) -> None:
    notification_settings = "You receive these emails because you signed up for notifications."
    sender_email = os.environ.get("GMAIL_EMAIL")
    
    subject = "We have news!"
    redirect_title = "To read the latest news, "
    redirect_url = url_for('news.all_news', _external=True)
    settings_url = url_for('admin.user_admin', _external=True)
    
    email_body = render_template(
        "admin/email.html",
        title=subject,
        redirect_title=redirect_title,
        notification_settings=notification_settings,
        redirect_url=redirect_url,
        settings_url=settings_url
    )
    message = Message(subject=subject,
                      sender=sender_email,
                      recipients=[recipient_email],
                      html=email_body)
    mail_.send(message)
    

def send_comment_notification_email(recipient_email: str, comment_id: int, news_id: int) -> None:
    notification_settings = "You receive these emails because you signed up for notifications."
    sender_email = os.environ.get("GMAIL_EMAIL")

    subject = "Someone liked your comment!"
    redirect_title = "To read the comment, "
    redirect_url = url_for(f'news.news', id_=news_id, _anchor=f"comment-{comment_id}", _external=True)
    settings_url = url_for('admin.user_admin', _external=True)
    
    email_body = render_template(
        "admin/email.html",
        title=subject,
        redirect_title=redirect_title,
        notification_settings=notification_settings,
        redirect_url=redirect_url,
        settings_url=settings_url
    )
    message = Message(subject=subject,
                      sender=sender_email,
                      recipients=[recipient_email],
                      html=email_body)
    mail_.send(message)


def send_bakery_notification_email(recipient_email: str, bakery_id: int, add_update: str) -> None:
    notification_settings = "You receive these emails because you signed up for notifications."
    sender_email = os.environ.get("GMAIL_EMAIL")

    subject = f"Bakery item {add_update}!"
    redirect_title = "To read the bakery update, "
    redirect_url = url_for(f'bakery.info', id_=bakery_id, _external=True)
    settings_url = url_for('admin.user_admin', _external=True)
    
    email_body = render_template(
        "admin/email.html",
        title=subject,
        redirect_title=redirect_title,
        notification_settings=notification_settings,
        redirect_url=redirect_url,
        settings_url=settings_url
    )
    message = Message(subject=subject,
                      sender=sender_email,
                      recipients=[recipient_email],
                      html=email_body)
    mail_.send(message)
