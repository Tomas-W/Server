from datetime import datetime

from src.models.news_mod import News


def get_all_news():
    news_items = News.query.with_entities(News.title, News.content, News.author, News.created_at).all()
    formatted_news = []
    for item in news_items:
        formatted_date = item[3].strftime("%d %b %H:%M")
        formatted_news.append((item[0], item[1], item[2], formatted_date))
    return formatted_news
