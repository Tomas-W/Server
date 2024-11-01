from flask_login import current_user

from src.extensions import server_db_
from src.models.mod_utils import commit_to_db
from src.models.news_model.news_mod import News


@commit_to_db
def add_news_message(title, content):
    # noinspection PyArgumentList
    new_news = News(
        title=title,
        content=content,
        author=current_user.username
    )
    server_db_.session.add(new_news)
