from sqlalchemy import select

from flask_login import current_user
from flask import session, abort

from src.extensions import server_db_, logger
from src.models.news_model.news_mod import News, Comment
from src.routes.news.news_items import get_news_dict
from src.routes.news.news_forms import AddNewsForm


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


def get_news_id_by_comment_id(id_: int):
    comment = server_db_.session.get(Comment, id_)
    return comment.news_id


def delete_news_by_id(id_: int) -> None:
    server_db_.session.delete(server_db_.session.get(News, id_))
    server_db_.session.commit()


def get_comment_by_id(id_: int):
    result = server_db_.session.get(Comment, id_)
    return result


def delete_comment_by_id(id_: int) -> bool:
    comment = server_db_.session.get(Comment, id_)
    if comment is not None:
        server_db_.session.delete(server_db_.session.get(Comment, id_))
        server_db_.session.commit()
        logger.log.info(f"Comment with ID {id_} deleted")
        return True
    else:
        error_msg = f"Comment with ID {id_} not found"
        session["error_msg"] = error_msg
        session["error_user_info"] = error_msg
        logger.log.error(error_msg)
        abort(404)


def clear_news_db() -> None:
    server_db_.session.query(News).delete()
    server_db_.session.commit()


def add_news_message(form: AddNewsForm, grid_cols: list[str], grid_rows: list[str],
                     info_cols: list[str], info_rows: list[str]) -> None:
    from src.models.news_model.news_mod import News
    # noinspection PyArgumentList
    new_news = News(
        title=form.title.data,
        header=form.header.data,
        code=form.code.data,
        important=form.important.data,
        grid_cols=grid_cols,
        grid_rows=grid_rows,
        info_cols=info_cols,
        info_rows=info_rows,
        author=form.author.data,
        user_id=current_user.id
    )
    server_db_.session.add(new_news)
    server_db_.session.commit()


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
                user_id=current_user.id if current_user else 1,
            )
            server_db_.session.add(news_item)
        server_db_.session.commit()
        return True
    
    return None

def get_comment_by_id(id_: int):
    result = server_db_.session.get(Comment, id_)
    return result


def add_new_comment(news_id: int, user_id: int, content: str) -> None:
    comment = Comment(
        news_id=news_id,
        user_id=user_id,
        content=content,
    )
    server_db_.session.add(comment)
    server_db_.session.commit()
