from sqlalchemy import select

from flask import session
from flask_login import current_user

from src.extensions import (
    logger,
    server_db_,
)

from src.models.news_model.news_mod import (
    Comment,
    News,
)

from src.routes.news.news_forms import AddNewsForm
from src.routes.news.news_items import get_news_dict


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
    if comment:
        return comment.news_id
    return None


def delete_news_by_id(id_: int, cli: bool = False) -> None:
    server_db_.session.delete(server_db_.session.get(News, id_))
    server_db_.session.commit()
    if not cli:
        logger.warning(f"[DEL] DELETE NEWS: {id_} DELETED")


def get_comment_by_id(id_: int):
    result = server_db_.session.get(Comment, id_)
    return result


def delete_comment_by_id(id_: int, cli: bool = False) -> bool:
    comment = server_db_.session.get(Comment, id_)
    if comment is not None:
        deleted_message = f"Comment {comment.content[:10]}.. by {comment.user.username} removed."
        server_db_.session.delete(server_db_.session.get(Comment, id_))
        server_db_.session.commit()
        if not cli:
            logger.warning(deleted_message)
        logger.debug("TRUE")
        return True
    logger.debug("FALSE")
    return False


def clear_news_db() -> None:
    server_db_.session.query(News).delete()
    server_db_.session.commit()


def clear_comments_db() -> None:
    server_db_.session.query(Comment).delete()
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
    logger.info(f"[ADD] NEWS CREATED: {new_news.title}")

def _init_news() -> bool:
    """
    Initializer function for cli.
    No internal use.
    """
    if not server_db_.session.query(News).count():
        news_dict = get_news_dict()
        # Fetch the lowest user_id from the User table
        from src.models.auth_model.auth_mod import User
        lowest_user_id = server_db_.session.query(User.id).order_by(User.id).first()
        
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
                user_id=lowest_user_id,
            )
            server_db_.session.add(news_item)
        server_db_.session.commit()
        return True
    
    return False

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
    logger.info(f"[ADD] COMMENT CREATED: {comment.content[:10]}.. by {comment.user.username}")
