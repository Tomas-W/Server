import click
from flask import Flask, current_app

from src.models.auth_mod import User


def _auth_cli(app_: Flask) -> None:
    @click.group()
    def auth() -> None:
        """Contains all cli functionality for the auth table"""
        pass

    @auth.command("info")
    @click.argument("id_", type=int)
    @click.option("--verbose", is_flag=True, help="Enables verbose mode.")
    def info(id_, verbose) -> None:
        """
        Takes a User id and returns its __repr__.
        Verbose adds columns.
        """
        user: User = User.query.get(id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
        else:
            if not verbose:
                click.echo(repr(user))
            else:
                click.echo(f"{'__repr__':<15}: {repr(user)}")
                click.echo(f"{'ID':<15}: {user.id}")
                click.echo(f"{'Username':<15}: {user.username}")
                click.echo(f"{'Email':<15}: {user.email}")
                click.echo(f"{'Email Verified':<15}: {user.email_verified}")

    @auth.command("get_col_by_id")
    @click.argument("id_", type=int)
    @click.argument("col_name", type=str)
    @click.option("--verbose", is_flag=True, help="Enables verbose mode.")
    def get_col_by_id(id_: int, col_name: str, verbose: bool) -> None:
        """
        Takes a User id and a column name and returns its value.
        Verbose adds __repr__
        usage: flask auth get_col_by_id <user id> <column name>
        """
        user = User.query.get(id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
        else:
            column_value = getattr(user, col_name, None)
            if column_value is None:
                click.echo(f"Column '{col_name}' does not exist in auth table.")
            else:
                if verbose:
                    click.echo(repr(user))
                    click.echo(f"{col_name}: {column_value}")
                else:
                    click.echo(f"{col_name}: {column_value}")

    @auth.command("set_email_verified")
    @click.argument("id_", type=int)
    @click.argument("new_val", type=bool)
    @click.option("--verbose", is_flag=True, help="Enables verbose mode.")
    def set_email_verified(id_: int, new_val: bool, verbose: bool) -> None:
        """
        Takes a User id and a column name and returns its value.
        Verbose adds __repr__
        usage: flask auth col_val <user id> <column name>
        """
        if not new_val == 0 or new_val == 1:
            click.echo(f"Param status must be of type bool"
                       f"but got '{new_val}'.")
        user: User = User.query.get(id_)
        col_name = "email_verified"
        if not user:
            click.echo(f"No User with id {id_} found.")
        else:
            old_val = getattr(user, "email_verified")
            setattr(user, "email_verified", new_val)
            if verbose:
                click.echo(repr(user))
                click.echo(f"Changed '{col_name}' column"
                           f" from '{old_val}' to '{new_val}'.")
            else:
                click.echo(f"Changed '{col_name}' to '{new_val}'.")

    app_.cli.add_command(auth)


def _server_cli(app_: Flask) -> None:
    @click.group()
    def server() -> None:
        """Custom cli commands"""
        pass

    @server.command("config_name")
    @click.option("--verbose", is_flag=True, help="Enables verbose mode.")
    def config_name(verbose: bool) -> None:
        """
        Returns the name of the active server configuration.
        Verbose adds
        """
        config = current_app.config["INSTANCE"]
        click.echo(config.config_name())
        if verbose:
            click.echo(f"SQLAlchemy db URI: {app_.config["SQLALCHEMY_DATABASE_URI"]}")

    app_.cli.add_command(server)
