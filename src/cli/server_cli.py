import click

from flask import (
    Flask,
    current_app,
)

from src.extensions import (
    logger,
    server_db_,
)

from src.cli.bakery_cli import bakery_cli
from src.cli.news_cli import news_cli
from src.cli.schedule_cli import schedule_cli
from src.cli.user_cli import user_cli


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

        Usage: flask server init-server [--v] [--c]
        """
        ctx = click.get_current_context()

        ctx.invoke(user_cli.commands['init-user'], v=v, c=c)
        ctx.invoke(news_cli.commands['init-news'], v=v, c=c)
        ctx.invoke(bakery_cli.commands['init-bakery'], v=v, c=c)
        ctx.invoke(schedule_cli.commands['init-schedule'], v=v, c=c)
        ctx.invoke(schedule_cli.commands['init-employees'], v=v, c=c)

    app_.cli.add_command(server)
