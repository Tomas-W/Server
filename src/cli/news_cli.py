import click

from flask import Flask
from src.extensions import (
    logger,
    server_db_,
)

from src.models.news_model.news_mod import (
    Comment,
    News,
)
from src.models.news_model.news_mod_utils import (
    _init_news,
    clear_comments_db,
    clear_news_db,
    delete_comment_by_id,
    delete_news_by_id,
    get_comment_by_id,
    get_news_by_id,
)
from src.routes.news.news_items import get_news_dict


@click.group()
def news():
    """News CLI commands."""
    pass

def news_cli(app_: Flask) -> None:
    @news.command("init-news")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_news(v: bool, c: bool) -> None:
        """
        Initializes the News Table.

        Usage: flask news init-news [--v] [--c]
        """
        news_dict = get_news_dict()
        item_count = len(news_dict)
        
        if not c and not click.confirm(
                f"Are you sure you want to add {item_count} items to the News Table?"):
            click.echo("Adding NewsItems cancelled.")
            return

        may_init_news: bool = _init_news()
        if not may_init_news:
            click.echo("Adding NewsItems failed.\n"
                       "News Table not empty.")
            return
        
        logger.info(f"[CLI] INIT NEWS: {item_count} items added.")
        if v:
            click.echo(f"Successfully added {item_count} NewsItems to the News Table.")


    @news.command("news-repr")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def news_repr(id_: int, v: bool) -> None:
        """
        Shows the repr of a NewsItem.

        Usage: flask news news-repr <id_> [--v]
        """
        news_item = get_news_by_id(id_)
        if not news_item:
            click.echo(f"No NewsItem with ID {id_} found.")
            return
        if v:
            click.echo(news_item.cli_repr())
        else:
            click.echo(news_item.title)
    

    @news.command("delete-news")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def delete_news(id_: int, c: bool, v: bool) -> None:
        """
        Removes a NewsItem from the News Table.

        Usage: flask news delete-news <id_> [--v] [--c]
        """
        news_item = get_news_by_id(id_)
        if not news_item:
            click.echo(f"No NewsItem with ID {id_} found.")
            return

        news_repr = news_item.cli_repr()
        if not c and not click.confirm(
                f"Are you sure you want to remove NewsItem:\n"
                f"{news_repr}?"):
            click.echo("NewsItem removal cancelled.")
            return
        
        delete_news_by_id(id_, cli=True)
        logger.warning(f"[CLI] DELETE NEWS: {news_item.title[:10]} removed.")
        if v:
            click.echo(f"Successfully removed NewsItem: {news_repr}.")


    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def clear_news(c: bool, v: bool) -> None:
        """
        Removes all NewsItems from the News Table.

        Usage: flask news clear-news [--v] [--c]
        """
        item_count = server_db_.session.query(News).count()
        
        if not c and not click.confirm(
                f"Are you sure you want to remove {item_count} NewsItems from the News Table?"):
            click.echo("Removing NewsItems cancelled.")
            return

        clear_news_db()
        logger.warning(f"[CLI] CLEAR NEWS: {item_count} items removed.")
        if v:
            click.echo(f"Successfully removed {item_count} NewsItems from the News Table.")
    

    @news.command("comment-repr")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def comment_repr(id_: int, v: bool) -> None:
        """
        Shows the repr of a Comment.

        Usage: flask news comment-repr <id_> [--v]
        """
        comment = get_comment_by_id(id_)
        if not comment:
            click.echo(f"No Comment with ID {id_} found.")
            return
        if v:
            click.echo(comment.cli_repr())
        else:
            click.echo(comment.content)
    

    @news.command("delete-comment")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def delete_comment(id_: int, c: bool, v: bool) -> None:
        """
        Removes a CommentItem from the Comments Table.

        Usage: flask news delete-comment <id_> [--v] [--c]
        """
        comment = get_comment_by_id(id_)
        if not comment:
            click.echo(f"No Comment with ID {id_} found.")
            return
        
        if not c and not click.confirm(
                f"Are you sure you want to remove Comment:\n"
                f"{comment.cli_repr()}?"):
            click.echo("Comment removal cancelled.")
            return
        
        delete_comment_by_id(id_, cli=True)
        logger.warning(f"[CLI] DELETE COMMENT: {comment.content[:10]} by {comment.author} removed.")
        if v:
            click.echo(f"Successfully removed Comment:\n"
                       f"{comment.cli_repr()}.")


    @news.command("clear-comments")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def clear_comments(c: bool, v: bool) -> None:
        """
        Removes all CommentItems from the Comments Table.

        Usage: flask news clear-comments [--v] [--c]
        """
        comment_count = server_db_.session.query(Comment).count()
        if not c and not click.confirm(
                f"Are you sure you want to remove {comment_count} CommentItems from the Comments Table?"):
            click.echo("Removing Comments cancelled.")
            return
        
        clear_comments_db()
        logger.warning(f"[CLI] CLEAR COMMENTS: {comment_count} items removed.")
        if v:
            click.echo(f"Successfully removed {comment_count} CommentItems from the Comments Table.")


    app_.cli.add_command(news)
