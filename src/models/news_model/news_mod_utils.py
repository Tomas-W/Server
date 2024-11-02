from sqlalchemy import select

from src.extensions import server_db_
from src.models.news_model.news_mod import News, Comment
from src.routes.news.news_items import get_news_dict
from src.models.mod_utils import commit_to_db


def get_all_news_dict() -> list[dict]:
    result = server_db_.session.execute(
        select(News)
    ).scalars().all()
    return [news.to_dict() for news in result]


def get_all_unread_dict(user_id: int) -> list[dict]:
    result = server_db_.session.execute(
        select(News)
    ).scalars().all()
    return [news.to_dict() for news in result
            if str(user_id) not in news.seen_by.split("|")]


def get_news_by_id(id_: int):
    result = server_db_.session.get(News, id_)
    return result


def get_news_dict_by_id(id_: int):
    result = server_db_.session.get(News, id_)
    return result.to_dict()


@commit_to_db
def delete_news_by_id(id_: int) -> None:
    server_db_.session.delete(server_db_.session.get(News, id_))


@commit_to_db
def clear_news_db() -> None:
    server_db_.session.query(News).delete()


def _init_news() -> bool | None:
    """
    Initializer function for cli.
    No internal use.
    """
    if not server_db_.session.query(News).count():
        news_dict = get_news_dict()
        for _, item_details in news_dict.items():
            news_item = News(
                header=item_details["header"],
                title=item_details["title"],
                code=item_details["code"],
                important=item_details["important"],
                grid_cols=item_details["grid_cols"],
                grid_rows=item_details["grid_rows"],
                info_cols=item_details["info_cols"],
                info_rows=item_details["info_rows"],
                author=item_details["author"],
            )
            server_db_.session.add(news_item)
        server_db_.session.commit()
        return True
    
    return None

def get_comment_by_id(id_: int):
    result = server_db_.session.get(Comment, id_)
    return result


def add_new_comment(news_id: int, author_id: int, content: str) -> None:
    comment = Comment(
        news_id=news_id,
        author_id=author_id,
        content=content,
    )
    server_db_.session.add(comment)
    server_db_.session.commit()
