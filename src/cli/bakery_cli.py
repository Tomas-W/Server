import click
from flask import Flask

from src.extensions import logger, server_db_
from src.models.bakery_model.bakery_mod import BakeryItem
from src.models.bakery_model.bakery_mod_utils import (
    get_bakery_dict, _init_bakery, clear_bakery_db
)


def bakery_cli(app_: Flask) -> None:
    @click.group()
    def bakery() -> None:
        """CLI functionality for the Bakery Table"""
        pass

    @bakery.command("init-bakery")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_bakery(c: bool, v: bool) -> None:
        """
        Adds BakeryItems from bakery_items.py to the Bakery Table.

        Usage: flask bakery init-bakery [--v] [--c]
        """
        dict_ = get_bakery_dict()
        item_count = len(dict_)
        
        if not c and not click.confirm(
                f"Are you sure you want to add {item_count} items to the Bakery Table?"):
            click.echo("Adding BakeryItems cancelled.")
            return

        may_init_bakery: bool = _init_bakery()
        if not may_init_bakery:
            click.echo("Adding BakeryItems failed.\n"
                       "BakeryItems table not empty.")
            return
        
        logger.info(f"[CLI] INIT BAKERY: {item_count} items added.")
        if v:
            click.echo(f"Successfully added {item_count} items to the Bakery Table.")
    
    @bakery.command("clear-bakery")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def clear_bakery(c: bool, v: bool) -> None:
        """
        Removes all BakeryItems from the Bakery Table.
        """
        item_count = server_db_.session.query(BakeryItem).count()
        if not c and not click.confirm(
                f"Are you sure you want to remove {item_count} BakeryItems from the Bakery Table?"):
            click.echo("Removing BakeryItems cancelled.")
            return

        clear_bakery_db()
        logger.warning(f"[CLI] CLEAR BAKERY: {item_count} items removed.")
        if v:
            click.echo(f"Successfully removed {item_count} BakeryItems from the Bakery Table.")

    app_.cli.add_command(bakery)
