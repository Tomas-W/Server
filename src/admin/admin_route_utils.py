from flask_login import current_user

from src import server_db_
from src.models.news_mod import News


def add_news_message(title, content):
    # noinspection PyArgumentList
    new_news = News(
        title=title,
        content=content,
        author=current_user.username
    )
    server_db_.session.add(new_news)
    server_db_.session.commit()
