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
    delete_user_by_id, _init_user
)
from src.models.schedule_model.schedule_mod_utils import (
    _init_schedule, _init_employees, _get_schedule_paths
)
from src.routes.bakery.bakery_items import get_bakery_dict
from src.routes.news.news_items import get_news_dict

from config.settings import (
    EMPLOYEES_PATH
)


def _auth_cli(app_: Flask) -> None:
    """Configures authentication CLI commands."""

    @click.group()
    def auth() -> None:
        """CLI functionality for the User table"""
        pass
    
    @auth.command("user-repr")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def user_repr(id_: int, v: bool) -> None:
        """
        Takes a User ID and returns its cli_repr.

        Usage: flask auth user-repr <id_> [--v]
        """
        user: User | None = server_db_.session.get(User, id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
            return

        click.echo(user.cli_repr())
                 

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
        if user is None:
            click.echo(f"No User with id {id_} found.")
            return

        user_repr = user.cli_repr()
        confirmation_message = f"Are you sure you want to delete User:\n{user_repr}?"
        
        if not c and not click.confirm(confirmation_message):
            click.echo("User deletion cancelled.")
            return

        delete_user_by_id(id_)
        if v:
            click.echo(f"User has been removed from the table.")
        

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
            user_repr = user.cli_repr()
            click.echo(f"{user_repr}")

        click.echo(f"Column name : '{col_name}'.")
        click.echo(f"Column value: '{col_value}'.")
    
    
    @auth.command("set-col-by-id")
    @click.argument("id_", type=int)
    @click.argument("col_name", type=str)
    @click.argument("col_value", type=str)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def set_col_by_id(id_: int, col_name: str, col_value: str, v: bool) -> None:
        """
        Takes a User ID, column name, and value, and sets the column to the value using the corresponding method.

        Usage: flask auth set-col-by-id <user id> <column name> <value> [--v]
        """
        user: User | None = server_db_.session.get(User, id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
            return

        method_name = f"set_{col_name}"
        if not hasattr(user, method_name):
            click.echo(f"Method '{method_name}' does not exist for User.")
            if v:
                methods = [method for method in dir(user) if method.startswith("set_")]
                click.echo("Available methods are:")
                for method in methods:
                    click.echo(f"- {method}")
            return

        method = getattr(user, method_name)
        try:
            method(col_value)
            server_db_.session.commit()
            click.echo(f"Column '{col_name}' set to '{col_value}' for User ID {id_}.")
        except ValueError as e:
            click.echo(f"Error: {e}")

        if v:
            user_repr = user.cli_repr()
            click.echo(f"Updated User: {user_repr}")

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
    
    
    @server.command("remove-news")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def remove_news(c: bool, v: bool) -> None:
        """
        Removes all news items from the News Table.

        Usage: flask server remove-news [--v] [--c]
        """
        item_count = server_db_.session.query(News).count()
        
        if not c and not click.confirm(
                f"Are you sure you want to remove {item_count} items from the News Table?"):
            click.echo("Removing News Items cancelled.")
            return

        clear_news_db()
        if v:
            click.echo(f"Successfully removed {item_count} items from the News Table.")
    
    
    @server.command("remove-news-item")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def remove_news_item(id_: int, c: bool, v: bool) -> None:
        """
        Removes a news item from the News Table by ID.

        Usage: flask server remove-news-item <id_> [--v] [--c]
        """
        news_item = get_news_by_id(id_)
        if not news_item:
            click.echo(f"No NewsItem with id {id_} found.")
            return

        news_repr = news_item.cli_repr()
        if not c and not click.confirm(
                f"Are you sure you want to remove NewsItem:\n{news_repr}?"):
            click.echo("NewsItem removal cancelled.")
            return
        
        delete_news_by_id(id_)
        if v:
            click.echo(f"Successfully removed NewsItem: {news_repr}.")
    
    
    @server.command("remove-bakery")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def remove_bakery(c: bool, v: bool) -> None:
        """
        Removes all bakery items from the BakeryItems Table.

        Usage: flask server remove-bakery [--v] [--c]
        """
        item_count = server_db_.session.query(BakeryItem).count()
        
        if not c and not click.confirm(
                f"Are you sure you want to remove {item_count} items from the BakeryItems Table?"):
            click.echo("Removing BakeryItems cancelled.")
            return

        clear_bakery_db()
        if v:
            click.echo(f"Successfully removed {item_count} items from the BakeryItems Table.")

    @server.command("remove-bakery-item")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def remove_bakery_item(id_: int, c: bool, v: bool) -> None:
        """
        Removes a bakery item from the BakeryItems Table by ID.

        Usage: flask server remove-bakery-item <id_> [--v] [--c]
        """
        bakery_item = get_item_by_id(id_)
        if not bakery_item:
            click.echo(f"No BakeryItem with id {id_} found.")
            return
        
        bakery_repr = bakery_item.cli_repr()
        if not c and not click.confirm(
                f"Are you sure you want to remove BakeryItem:\n{bakery_repr}?"):
            click.echo("BakeryItem removal cancelled.")
            return

        delete_item_by_id(id_)
        if v:
            click.echo(f"Successfully removed BakeryItem: {bakery_repr}.")
    

    @server.command("init-user")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_user(v: bool, c: bool) -> None:
        """
        Initializes the first user.

        Usage: flask server init-user [--v] [--c]
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

    @server.command("init-news")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_news(c: bool, v: bool) -> None:
        """
        Adds news items to the News Table.
        
        Usage: flask server init-news [--v] [--c]
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

    @server.command("init-bakery")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_bakery(c: bool, v: bool) -> None:
        """
        Adds bakery items to the BakeryItems Table.

        Usage: flask server init-bakery [--v] [--c]
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

    @server.command("init-schedule")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_schedule(c: bool, v: bool) -> None:
        """
        Adds schedule items to the Schedule Table.

        Usage: flask server init-schedule [--v] [--c]
        """
        paths = _get_schedule_paths()
        nr_weeks = 0
        for path in paths:
            with open(path, "r") as json_file:
                schedule_data = json.load(json_file)
            nr_weeks += len(schedule_data)
        
        if not c and not click.confirm(
                f"Are you sure you want to add {nr_weeks} weeks to the Schedule Table?"):
            click.echo("Adding Schedule Items cancelled.")
            return
        
        may_init_schedule: bool | None = _init_schedule()
        if not may_init_schedule:
            click.echo("Adding Schedule Items failed.\n"
                       "Schedule table not empty.")
            return
        
        if v:
            click.echo(f"Successfully added {nr_weeks} weeks to the Schedule Table.")

    @server.command("init-employees")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_employees(v: bool, c: bool) -> None:
        """
        Adds employees to the Employees Table.

        Usage: flask server init-employees [--v] [--c]
        """
        with open(EMPLOYEES_PATH, "r") as json_file:
            employees_data = json.load(json_file)
        
        nr_employees = len(employees_data)
        if not c and not click.confirm(
                f"Are you sure you want to add {nr_employees} employees to the Employees Table?"):
            click.echo("Adding Employees cancelled.")
            return
        
        may_init_employees: bool | None = _init_employees()
        if not may_init_employees:
            click.echo("Adding Employees failed.\n"
                       "Employees table not empty.")
            return
        
        if v:
            click.echo(f"Successfully added {nr_employees} employees to the Employees Table.")

    @server.command("init-server")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_server(v: bool, c: bool) -> None:
        """
        Initializes the server.
        Initializes the User, BakeryItems, News, Schedule, and Employees tables.

        Usage: flask server init-server [--v] [--c]
        """
        ctx = click.get_current_context()
        ctx.invoke(init_user, v=v, c=c)
        ctx.invoke(init_bakery, v=v, c=c)
        ctx.invoke(init_news, v=v, c=c)
        ctx.invoke(init_schedule, v=v, c=c)
        ctx.invoke(init_employees, v=v, c=c)

    app_.cli.add_command(server)
