import os

from flask import render_template, url_for
from flask_mail import Message
from src.extensions import server_db_, mail_
from src.models.email_model.email_mod import EmailStrorage


def add_email_to_db(email_type: str, recipient_email: str, news_id: int = None,
                    comment_id: int = None, bakery_id: int = None,
                    add_update: str = None) -> None:
    """
    Adds an email to the database.
    """
    new_email = EmailStrorage(email_type=email_type, recipient_email=recipient_email,
                      news_id=news_id, comment_id=comment_id, bakery_id=bakery_id,
                      add_update=add_update)
    server_db_.session.add(new_email)
    server_db_.session.commit()


def get_news_notification_recipient_emails() -> list[str]:
    """
    Extrapolates email addresses from the EmailStorage database for news notifications.
    """
    news_mails = EmailStrorage.query.filter_by(email_type="news").all()
    return [mail.recipient_email for mail in news_mails]


def send_news_notification_emails(recipient_emails: list[str]) -> None:
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
                      bcc=recipient_emails,
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
