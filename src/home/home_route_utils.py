from sqlalchemy import select

from src.models.news_mod import News
from src.extensions import server_db_


def get_all_news():
    stmt = select(News.title, News.content, News.author, News.created_at)
    news_items = server_db_.session.execute(stmt).all()
    formatted_news = []
    for item in news_items:
        formatted_news.append((item.title, item.content, item.author, item.created_at))
    return formatted_news
