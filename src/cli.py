import click
import json
from flask import Flask, current_app
from sqlalchemy import inspect

from src.extensions import server_db_
from src.models.auth_model.auth_mod import User
from src.models.bakery_model.bakery_mod import BakeryItem
from src.models.bakery_model.bakery_mod_utils import (
    get_item_by_id, delete_item_by_id, _init_bakery, clear_bakery_db
)
from src.models.news_model.news_mod import News
from src.models.news_model.news_mod_utils import (
    get_news_by_id, delete_news_by_id, _init_news, clear_news_db
)
from src.models.auth_model.auth_mod_utils import (
    delete_user_by_id, _init_user, update_schedule_name, update_schedule_name
)
from src.models.schedule_model.schedule_mod_utils import _init_schedule
from src.routes.bakery.bakery_items import get_bakery_dict
from src.routes.news.news_items import get_news_dict

from config.settings import (
    MIN_FAST_NAME_LENGTH, MAX_FAST_NAME_LENGTH, FAST_CODE_LENGTH, SCHEDULE_PATH
)


def _auth_cli(app_: Flask) -> None:
    """Configures authentication CLI commands."""

    @click.group()
    def auth() -> None:
        """CLI functionality for the User table"""
        pass
    
    @auth.command("init-user")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_user(v: bool, c: bool) -> None:
        """
        Initializes the first user.

        Usage: flask auth init-user [--v] [--c]
        """
        if not c and not click.confirm(
                f"Are you sure you want to init the first user?"):
            click.echo("User creation cancelled.")
            return
        
        user_repr: str | None = _init_user()
        if not user_repr:
            click.echo("User creation failed.\n"
                       "User table not empty.")
            return
        if v:
            click.echo(f"User created: {user_repr}")

    
    @auth.command("init-news")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_news(c: bool, v: bool) -> None:
        """
        Adds news items to the News Table.
        
        Usage: flask auth init-news [--v] [--c]
        """
        news_dict = get_news_dict()
        item_count = len(news_dict)
        
        if not c and not click.confirm(
                f"Are you sure you want to add {item_count} items to the News Table?"):
            click.echo("Adding News Items cancelled.")
            return

        may_init_news: bool | None = _init_news()
        if not may_init_news:
            click.echo("Adding News Items failed.\n"
                       "News table not empty.")
            return
        
        if v:
            click.echo(f"Successfully added {item_count} items to the News Table.")


    @auth.command("init-bakery")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_bakery(c: bool, v: bool) -> None:
        """
        Adds bakery items to the BakeryItems Table.

        Usage: flask auth init-bakery [--v] [--c]
        """
        dict_ = get_bakery_dict()
        item_count = len(dict_)
        
        if not c and not click.confirm(
                f"Are you sure you want to add {item_count} items to the BakeryItems Table?"):
            click.echo("Adding BakeryItems cancelled.")
            return

        may_init_bakery: bool | None = _init_bakery()
        if not may_init_bakery:
            click.echo("Adding BakeryItems failed.\n"
                       "BakeryItems table not empty.")
            return
        
        if v:
            click.echo(f"Successfully added {item_count} items to the BakeryItems Table.")

    
    @auth.command("init-schedule")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_schedule(c: bool, v: bool) -> None:
        """
        Adds schedule items to the Schedule Table.
        """
        with open(SCHEDULE_PATH, "r") as json_file:
            schedule_data = json.load(json_file)
        
        if not c and not click.confirm(
                f"Are you sure you want to add {len(schedule_data)} weeks to the Schedule Table?"):
            click.echo("Adding Schedule Items cancelled.")
            return
        
        _init_schedule()
        
        if v:
            click.echo(f"Successfully added {len(schedule_data)} items to the Schedule Table.")
        
        
    @auth.command("set-schedule-name")
    @click.argument("id_", type=int)
    @click.argument("name", type=str)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def set_schedule_name(id_: int, name: str, c: bool, v: bool) -> None:
        """
        Sets the schedule name for user with <id_>.
        """
        user: User | None = server_db_.session.get(User, id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
            return
        
        if not c and not click.confirm(
                f"Are you sure you want to set the schedule name for User:\n{repr(user)}\nto\n'{name}'?\n"):
            click.echo("Setting schedule name cancelled.")
            return
        
        update_schedule_name(id_, name)
        if v:
            click.echo(repr(user))
        
        
    
    @auth.command("remove-news")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def remove_news(c: bool, v: bool) -> None:
        """
        Removes all news items from the News Table.

        Usage: flask auth remove-news [--v] [--c]
        """
        item_count = server_db_.session.query(News).count()
        
        if not c and not click.confirm(
                f"Are you sure you want to remove {item_count} items from the News Table?"):
            click.echo("Removing News Items cancelled.")
            return

        clear_news_db()
        if v:
            click.echo(f"Successfully removed {item_count} items from the News Table.")
    
    
    @auth.command("remove-news-item")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def remove_news_item(id_: int, c: bool, v: bool) -> None:
        """
        Removes a news item from the News Table by ID.

        Usage: flask auth remove-news-item <id_> [--v] [--c]
        """
        news_item = get_news_by_id(id_)
        if not news_item:
            click.echo(f"No NewsItem with id {id_} found.")
            return

        if not c and not click.confirm(
                f"Are you sure you want to remove NewsItem:\n{repr(news_item)}?"):
            click.echo("NewsItem removal cancelled.")
            return
        
        delete_news_by_id(id_)
        if v:
            click.echo(f"Successfully removed NewsItem: {repr(news_item)}.")
    
    
    @auth.command("remove-bakery")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def remove_bakery(c: bool, v: bool) -> None:
        """
        Removes all bakery items from the BakeryItems Table.

        Usage: flask auth remove-bakery [--v] [--c]
        """
        item_count = server_db_.session.query(BakeryItem).count()
        
        if not c and not click.confirm(
                f"Are you sure you want to remove {item_count} items from the BakeryItems Table?"):
            click.echo("Removing BakeryItems cancelled.")
            return

        clear_bakery_db()
        if v:
            click.echo(f"Successfully removed {item_count} items from the BakeryItems Table.")

    @auth.command("remove-bakery-item")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def remove_bakery_item(id_: int, c: bool, v: bool) -> None:
        """
        Removes a bakery item from the BakeryItems Table by ID.

        Usage: flask auth remove-bakery-item <id_> [--v] [--c]
        """
        bakery_item = get_item_by_id(id_)
        if not bakery_item:
            click.echo(f"No BakeryItem with id {id_} found.")
            return

        if not c and not click.confirm(
                f"Are you sure you want to remove BakeryItem:\n{repr(bakery_item)}?"):
            click.echo("BakeryItem removal cancelled.")
            return

        delete_item_by_id(id_)
        if v:
            click.echo(f"Successfully removed BakeryItem: {repr(bakery_item)}.")
    
    
    @auth.command("info")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def info(id_: int, v: bool) -> None:
        """
        Takes a User ID and returns its __repr__.

        Usage: flask auth info <id_> [--v]
        """
        user: User | None = server_db_.session.get(User, id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
            return

        if v:
            user_info = {
                "__repr__": repr(user),
                "ID": user.id,
                "Username": user.username,
                "Email": user.email,
                "Email Verified": user.email_verified,
                "Remember me": user.remember_me
            }
            for key, value in user_info.items():
                click.echo(f"{key:<15}: {value}")
            return

        click.echo(repr(user))            

    @auth.command("delete-user")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def delete_user(id_: int, c: bool, v: bool) -> None:
        """
        Takes a User ID and deletes the record from the table.

        Usage: flask auth delete-user <user id> [--v] [--c]
        """
        user: User | None = server_db_.session.get(User, id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
            return

        if not c and not click.confirm(
                f"Are you sure you want to delete User: {repr(user)}?"):
            click.echo("User deletion cancelled.")
            return

        delete_user_by_id(id_)
        if v:
            click.echo(f"User: {repr(user)} has been removed from the table.")
        

    @auth.command("get-col-by-id")
    @click.argument("id_", type=int)
    @click.argument("col_name", type=str)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def get_col_by_id(id_: int, col_name: str, v: bool) -> None:
        """
        Takes a User ID and column name and returns the value.

        Usage: flask auth get-col-by-id <user id> <column name> [--v]
        """
        user: User | None = server_db_.session.get(User, id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
            return

        if not hasattr(user, col_name):
            click.echo(f"'{col_name}' does not exist in User table.")
            if v:
                columns = [column.key for column in inspect(User).attrs]
                click.echo("Available columns are:")
                for col in columns:
                    click.echo(f"- {col}")
            return

        col_value = getattr(user, col_name)
        if v:
            click.echo(repr(user))

        click.echo(f"Column name : '{col_name}'.")
        click.echo(f"Column value: '{col_value}'.")


    @auth.command("set-email-verified")
    @click.argument("id_", type=int)
    @click.argument("new_val", type=bool)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def set_email_verified(id_: int, new_val: bool, c: bool, v: bool) -> None:
        """
        Takes a User id and a bool and sets the email_verified column accordingly.

        Usage: flask auth set-email-verified <id_> <new_val> [--v] [--c]
        """
        col_name = "email_verified"
        if new_val not in [0, 1]:
            click.echo(f"Param new_val must be of type bool but got '{new_val}'.")
            return

        user: User | None = server_db_.session.get(User, id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
            return

        if not c and not click.confirm(
                f"Are you sure you want to set '{col_name}' to {new_val}?"):
            click.echo("Setting value cancelled.")
            return

        old_val = getattr(user, col_name)
        user.set_email_verified(new_val)
        if v:
            click.echo(repr(user))
            click.echo(f"Changed '{col_name}' from '{old_val}' to '{new_val}'.")
            

    @auth.command("set-f-name")
    @click.argument("id_", type=int)
    @click.argument("fast_name", type=str)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def set_fast_name(id_: int, fast_name: str, c: bool, v: bool) -> None:
        """
        Takes a User id and a string (len bound) and sets the fast_name of the User.

        Usage: flask auth set-f-name <user id> <fast_name> [--v] [--c]
        """
        col_name = "fast_name"
        if not MIN_FAST_NAME_LENGTH < len(fast_name) < MAX_FAST_NAME_LENGTH:
            click.echo(f"'{col_name}' length must be between {MIN_FAST_NAME_LENGTH} and {MAX_FAST_NAME_LENGTH} characters.")
            return

        user: User | None = server_db_.session.get(User, id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
            return
        
        if not c and not click.confirm(
                f"Are you sure you want to set '{col_name}' to '{fast_name}'?"):
            click.echo("Setting value cancelled.")
            return

        user.set_fast_name(fast_name)
        if v:
            click.echo(repr(user))
            click.echo(f"Set '{col_name}' to '{fast_name}'.")


    @auth.command("set-f-code")
    @click.argument("id_", type=int)
    @click.argument("fast_code", type=str)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def set_fast_code(id_: int, fast_code: str, c: bool, v: bool) -> None:
        """
        Takes a User id and a 5-digit number and sets the fast_code of the user.

        Usage: flask auth set-f-code <user id> <fast_code> [--v] [--c]
        """
        col_name = "fast_code"
        if not fast_code.isdigit() or len(fast_code) != FAST_CODE_LENGTH:
            click.echo(f"'{col_name}' must be a {FAST_CODE_LENGTH}-digit number.")
            return

        user: User | None = server_db_.session.get_or_none(User, id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
            return

        if not c and not click.confirm(
                f"Are you sure you want to set '{col_name}' to '{fast_code}'?"):
            click.echo("Setting value cancelled.")
            return

        user.set_fast_code(fast_code)
        if v:
            click.echo(repr(user))
            click.echo(f"Set '{col_name}' to '{fast_code}'.")

    app_.cli.add_command(auth)


def _server_cli(app_: Flask) -> None:
    @click.group()
    def server() -> None:
        """CLI functionality for server settings"""
        pass

    @server.command("config-name")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def config_name(v: bool) -> None:
        """
        Returns the name of the active server configuration.

        Usage: flask server config-name [--v]
        """
        config = current_app.config["INSTANCE"]

        if v:
            app_info = {
                "App name": current_app.name,
                "Debug mode": current_app.debug,
                "View functions": "\n" + "\n".join(
                    f"{' ' * 16} {view}" for view in current_app.view_functions)
            }
            for key, value in app_info.items():
                click.echo(f"{key:<15}: {value}")
            return

        click.echo(config.config_name())

    @server.command("init-server")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_server(v: bool, c: bool) -> None:
        ctx = click.get_current_context()
        ctx.invoke(app_.cli.commands["auth"].commands["init-user"], v=v, c=c)
        ctx.invoke(app_.cli.commands["auth"].commands["init-bakery"], v=v, c=c)
        ctx.invoke(app_.cli.commands["auth"].commands["init-news"], v=v, c=c)

    app_.cli.add_command(server)
