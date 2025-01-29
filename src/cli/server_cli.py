import click
import os

from flask import (
    Flask,
    current_app,
)

from src.extensions import (
    logger,
    server_db_,
)

from src.cli.bakery_cli import bakery
from src.cli.news_cli import news
from src.cli.schedule_cli import schedule
from src.cli.user_cli import user


def server_cli(app_: Flask) -> None:
    @click.group()
    def server() -> None:
        """ CLI functionality for the Server. """
        pass

    @server.command("config-name")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def config_name(v: bool) -> None:
        """
        Returns the name of the active server Configuration.

        Usage: flask server config-name [--v]
        """
        config = current_app.config["INSTANCE"]

        if v:
            app_info = {
                "App name": current_app.name,
                "Environment": current_app.config["CONFIG_NAME"],
                "View functions": "\n" + "\n".join(
                    f"{' ' * 16} {view}" for view in current_app.view_functions)
            }
            for key, value in app_info.items():
                click.echo(f"{key:<15}: {value}")
            return

        click.echo(config.config_name())
    

    @server.command("rollback-db")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def rollback_db(v: bool, c: bool) -> None:
        """
        Rolls back the Database to the previous state.

        Usage: flask server rollback-db [--v]
        """
        if not c and not click.confirm(
                f"Are you sure you want to rollback the Database?"):
            click.echo("Database rollback cancelled.")
            return
        
        server_db_.session.rollback()
        logger.critical(f"[CLI] DATABASE ROLLBACK: Database rolled back.")
        if v:
            click.echo("Database rolled back.")
    
    @server.command("init-server")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_server(v: bool, c: bool) -> None:
        """
        Initializes the Server.
        Initializes the User, Bakery, News, Schedule, and Employees Tables.
        """
        # Set a flag to indicate we're running in CLI
        os.environ["FLASK_CLI"] = "1"

        # Override PGHOST for CLI if using internal hostname
        if os.environ.get("PGHOST") == "postgres.railway.internal":
            public_db_url = os.environ.get("DATABASE_PUBLIC_URL")
            if public_db_url:
                # Extract host from DATABASE_PUBLIC_URL
                public_host = public_db_url.split("@")[1].split(":")[0]
                os.environ["PGHOST"] = public_host

        try:
            ctx = click.get_current_context()
            ctx.invoke(user.commands['init-user'], v=v, c=c)
            ctx.invoke(news.commands['init-news'], v=v, c=c)
            ctx.invoke(bakery.commands['init-bakery'], v=v, c=c)
            ctx.invoke(schedule.commands['init-schedule'], v=v, c=c)
            ctx.invoke(schedule.commands['init-employees'], v=v, c=c)
        finally:
            # Clean up the environment variable
            del os.environ["FLASK_CLI"]

    app_.cli.add_command(server)
