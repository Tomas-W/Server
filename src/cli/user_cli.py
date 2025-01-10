import click
from sqlalchemy import inspect
from flask import Flask
from src.extensions import server_db_
from src.models.auth_model.auth_mod import User

from src.models.auth_model.auth_mod_utils import (
    delete_user_by_id, _init_user
)


def user_cli(app_: Flask) -> None:
    """Configures User CLI commands."""

    @click.group()
    def user() -> None:
        """CLI functionality for the User table"""
        pass

    @user.command("init-user")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_user(v: bool, c: bool) -> None:
        """
        Initializes the first user.

        Usage: flask user init-user [--v] [--c]
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

    @user.command("repr")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def repr(id_: int, v: bool) -> None:
        """
        Takes a User ID and returns its cli_repr.

        Usage: flask user repr <id_> [--v]
        """
        user: User | None = server_db_.session.get(User, id_)
        if user is None:
            click.echo(f"No User with id {id_} found.")
            return
        
        user_repr = user.cli_repr()
        click.echo(user_repr)
    
    @user.command("delete")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def delete(id_: int, c: bool, v: bool) -> None:
        """
        Takes a User ID and deletes the record from the table.

        Usage: flask user delete <user id> [--v] [--c]
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
        

    @user.command("get-col-by-id")
    @click.argument("id_", type=int)
    @click.argument("col_name", type=str)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def get_col_by_id(id_: int, col_name: str, v: bool) -> None:
        """
        Takes a User ID and column name and returns the value.

        Usage: flask user get-col-by-id <user id> <column name> [--v]
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
    
    
    @user.command("set-col-by-id")
    @click.argument("id_", type=int)
    @click.argument("col_name", type=str)
    @click.argument("col_value", type=str)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def set_col_by_id(id_: int, col_name: str, col_value: str, v: bool) -> None:
        """
        Takes a User ID, column name, and value, 
            and sets the column to the value using the corresponding method.

        Usage: flask user set-col-by-id <user id> <column name> <value> [--v]
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

    app_.cli.add_command(user)
