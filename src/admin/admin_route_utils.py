from flask import url_for
from flask_login import current_user
from flask_mail import Message
import os
from src.extensions import server_db_, serializer_
from src.models.news_mod import News

from src.admin.admin_forms import AuthenticationForm


def add_news_message(title, content):
    # noinspection PyArgumentList
    new_news = News(
        title=title,
        content=content,
        author=current_user.username
    )
    server_db_.session.add(new_news)
    server_db_.session.commit()

