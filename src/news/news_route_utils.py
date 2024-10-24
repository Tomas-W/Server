from sqlalchemy import select

from src.models.news_mod import News
from src.extensions import server_db_


# def get_all_news():
#     stmt = select(News.title, News.content, News.author, News.created_at)
#     news_items = server_db_.session.execute(stmt).all()
#     formatted_news = []
#     for item in news_items:
#         formatted_news.append((item.title, item.content, item.author, item.created_at))
#     return formatted_news


def get_row_list(news_item: News) -> list[list[str]]:
    grid_len = news_item.grid_len()
    row_list = []
    
    if grid_len:
        if grid_len == len(news_item.grid_rows.split("|")):
            list_ = news_item.grid_rows.split("|")
            row_list.append(list_)
        else:
            for i in range(0, len(news_item.grid_rows.split("|")), grid_len):   
                row_list.append(news_item.grid_rows.split("|")[i:i + grid_len])

    return row_list
