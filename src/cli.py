import click
from flask import Flask, current_app
from sqlalchemy import inspect

from src.bakery.bakery_items import get_bakery_dict
from src.extensions import server_db_, argon2_
from src.models.auth_mod import User
from src.models.bakery_mod import BakeryItem
from src.home.news_items import _get_news_dict
from src.models.news_mod import News

def _auth_cli(app_: Flask) -> None:
    """Configures authentication CLI commands."""

    @click.group()
    def auth() -> None:
        """CLI functionality for the User table"""
        pass
    
    @auth.command("add-news")
    @click.option("--c", is_flag=True,
                  help="Confirm User deletion without prompting.")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def add_news(c: bool, v: bool) -> None:
        """
        Adds news items to the News Table.
        """
        dict_ = _get_news_dict()
        item_count = len(dict_)
        
        if not c and not click.confirm(
                f"Are you sure you want to add {item_count} items to the News Table?"):
            click.echo("Adding News Items cancelled.")
            return

        for item_name, item_details in dict_.items():
            news_item = News(
                title=item_details["title"],
                code=item_details["code"],
                important=item_details["important"],
                grid_cols=item_details["grid_cols"],
                grid_rows=item_details["grid_rows"],
                info_cols=item_details["info_cols"],
                info_rows=item_details["info_rows"],
                author=item_details["author"]
            )
            server_db_.session.add(news_item)
        server_db_.session.commit()
        
        if v:
            click.echo(f"Successfully added {item_count} items to the News Table.")

    @auth.command("add-bakery")
    @click.option("--c", is_flag=True,
                  help="Confirm User deletion without prompting.")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def add_bakery(c: bool, v: bool) -> None:
        """
        Adds bakery items to the BakeryItems Table.

        Usage: flask auth add-bakery [--v]
        """
        dict_ = get_bakery_dict()
        item_count = len(dict_)
        
        if not c and not click.confirm(
                f"Are you sure you want to add {item_count} items to the BakeryItems Table?"):
            click.echo("Adding BakeryItems cancelled.")
            return

        for item_name, item_details in dict_.items():
            bakery_item = BakeryItem(
                name=item_name,
                category=item_details["category"],
                program=item_details["program"],
                nasa=item_details["nasa"],
                price=item_details["price"],
                type="-".join(item_details["type"]),
                tags="-".join(item_details["tags"]),
                package_type=item_details["package_type"],
                per_package=item_details["per_package"],
                rack_type=item_details["rack_type"],
                per_rack=item_details["per_rack"],
                defrost_time=item_details["defrost_time"],
                cooldown_time=item_details["cooldown_time"],
                make_halves=item_details["make_halves"],
                vegan=item_details["vegan"],
                lactose_free=item_details["lactose_free"],
                nutri_score=item_details["nutri_score"],
                contains="-".join(item_details["contains"]),
                may_contain="-".join(item_details["may_contain"]),
                image=item_details["image"]
            )
            server_db_.session.add(bakery_item)
        server_db_.session.commit()
        if v:
            click.echo(f"Successfully added {item_count} items to the BakeryItems Table.")

    @auth.command("remove-bakery")
    @click.option("--c", is_flag=True,
                  help="Confirm removal without prompting.")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def remove_bakery(c: bool, v: bool) -> None:
        """
        Removes all bakery items from the BakeryItems Table.

        Usage: flask auth remove-bakery [--c] [--v]
        """
        item_count = server_db_.session.query(BakeryItem).count()
        
        if not c and not click.confirm(
                f"Are you sure you want to remove {item_count} items from the BakeryItems Table?"):
            click.echo("Removing BakeryItems cancelled.")
            return

        server_db_.session.query(BakeryItem).delete()
        server_db_.session.commit()
        if v:
            click.echo(f"Successfully removed {item_count} items from the BakeryItems Table.")

    @auth.command("remove-bakery-item")
    @click.argument("id_", type=int)
    @click.option("--c", is_flag=True,
                  help="Confirm removal without prompting.")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def remove_bakery_item(id_: int, c: bool, v: bool) -> None:
        """
        Removes a bakery item from the BakeryItems Table by ID.

        Usage: flask auth remove-bakery-item <id_> [--c] [--v]
        :param id_: ID of the bakery item to remove
        """
        bakery_item = BakeryItem.get_item_by_id(id_)
        if not bakery_item:
            click.echo(f"No BakeryItem with id {id_} found.")
            return

        if not c and not click.confirm(
                f"Are you sure you want to remove BakeryItem:\n{repr(bakery_item)}?"):
            click.echo("BakeryItem removal cancelled.")
            return

        server_db_.session.delete(bakery_item)
        server_db_.session.commit()
        if v:
            click.echo(f"Successfully removed BakeryItem: {repr(bakery_item)}.")
    
    @auth.command("info")
    @click.argument("id_", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def info(id_: int, v: bool) -> None:
        """
        Takes a User ID and returns its __repr__.

        Usage: flask auth info <id_> [--v]
        :param id_: User ID
        :param v: Enables verbose mode (optional)
        """
        user: User = server_db_.session.get(User, id_)
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
    @click.option("--c", is_flag=True,
                  help="Confirm User deletion without prompting.")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def delete_user(id_: int, c: bool, v: bool) -> None:
        """
        Takes a User ID and deletes the record from the table.

        Usage: flask auth delete-user <user id> [--c] [--v]
        :param id_: User ID.
        :param c: Confirm without prompt (optional)
        :param v: Enables verbose mode (optional)
        """
        user: User = server_db_.session.get(User, id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
            return

        if not c and not click.confirm(
                f"Are you sure you want to delete User: {repr(user)}?"):
            click.echo("User deletion cancelled.")
            return

        if v:
            click.echo(f"Deleting user: {repr(user)}")

        server_db_.session.delete(user)
        server_db_.session.commit()

        click.echo(f"User: {repr(user)} has been removed from the table.")
        return

    @auth.command("get-col-by-id")
    @click.argument("id_", type=int)
    @click.argument("col_name", type=str)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def get_col_by_id(id_: int, col_name: str, v: bool) -> None:
        """
        Takes a User ID and column name and returns the value.

        Usage: flask auth get-col-by-id <user id> [--v]
        :param id_: User ID
        :param col_name: Name of the column
        :param v: Enables verbose mode (optional)
        """
        user: User = server_db_.session.get(User, id_)
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

        click.echo(f"Column name: '{col_name}'.")
        click.echo(f"Column value: '{col_value}'.")
        return

    @auth.command("set-email-verified")
    @click.argument("id_", type=int)
    @click.argument("new_val", type=bool)
    @click.option("--c", is_flag=True,
                  help="Confirm setting value without prompting.")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def set_email_verified(id_: int, new_val: bool, c: bool, v: bool) -> None:
        """
        Takes a User id and a bool and sets the email_verified column accordingly.

        Usage: flask auth set-email-verified <id_> <new_val> [--c] [--v]
        :param id_: User ID
        :param new_val: New value of the email_verified column
        :param c: Confirm without prompt (optional)
        :param v: Enables verbose mode (optional)
        """
        col_name = "email_verified"
        if new_val not in [0, 1]:
            click.echo(f"Param new_val must be of type bool but got '{new_val}'.")
            return

        user: User = server_db_.session.get(User, id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
            return

        if not c and not click.confirm(
                f"Are you sure you want to set '{col_name}' to {new_val}?"):
            click.echo("Setting value cancelled.")
            return

        old_val = getattr(user, col_name)
        setattr(user, col_name, new_val)
        server_db_.session.commit()
        if v:
            click.echo(repr(user))

        click.echo(f"Changed '{col_name}' from '{old_val}' to '{new_val}'.")
        return

    @auth.command("set-f-name")
    @click.argument("id_", type=int)
    @click.argument("fast_name", type=str)
    @click.option("--c", is_flag=True,
                  help="Confirm User deletion without prompting.")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def set_f_name(id_: int, fast_name: str, c: bool, v: bool) -> None:
        """
        Takes a User id and a string (3 < len < 17) and sets the fast_name of the User.

        Usage: flask auth set-f-name <user id> <fast_name> [--c] [--v]
        :param id_: User ID
        :param fast_name: Users fast_name
        :param c: Confirm without prompt (optional)
        :param v: Enables verbose mode (optional)
        """
        col_name = "fast_name"
        if not 3 < len(fast_name) < 17:
            click.echo(f"'{col_name}' length must be between 3 and 17 characters.")
            return

        user: User = server_db_.session.get(User, id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
            return

        if v:
            click.echo(f"Applying to: {user.username} with {col_name}: {user.fast_name}")
        
        if not c and not click.confirm(
                f"Are you sure you want to set '{col_name}' to '{fast_name}'?"):
            click.echo("Setting value cancelled.")
            return

        user.set_f_name(fast_name)
        if v:
            click.echo(repr(user))

        click.echo(f"Set '{col_name}' to '{fast_name}'.")
        return

    @auth.command("set-f-code")
    @click.argument("id_", type=int)
    @click.argument("fast_code", type=str)
    @click.option("--c", is_flag=True,
                  help="Confirm setting value without prompting.")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    def set_f_code(id_: int, fast_code: str, c: bool, v: bool) -> None:
        """
        Takes a User id and a 5-digit number and sets the fast_code of the user.

        Usage: flask auth set-f-code <user id> <5-digit fast_code>
        :param id_: User ID
        :param fast_code: 5 digit login code
        :param c: Confirm without prompt (optional)
        :param v: Enables verbose mode (optional)
        """
        col_name = "fast_code"
        if not fast_code.isdigit() or len(fast_code) != 5:
            click.echo(f"'{col_name}' must be a 5-digit number.")
            return

        user: User = server_db_.session.get(User, id_)
        if not user:
            click.echo(f"No User with id {id_} found.")
            return
        
        if v:
            click.echo(f"Applying to: {user.username} with fast_name: {user.fast_name}")

        if not c and not click.confirm(
                f"Are you sure you want to set '{col_name}' to '{fast_code}'?"):
            click.echo("Setting value cancelled.")
            return

        hashed_code = argon2_.hash(fast_code)
        setattr(user, col_name, hashed_code)
        server_db_.session.commit()
        if v:
            click.echo(repr(user))

        click.echo(f"Set '{col_name}' to '{fast_code}'.")
        return
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
        :param v: Enables verbose mode (optional)
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
        return

    @server.command("init")
    def init() -> None:
        """
        Sets the fast_name of the first user to 'tomas' and the fast_code to argon2_.hash("00000").

        Usage: flask server set_first_user_fast_info
        """
        user: User = server_db_.session.execute(
            server_db_.select(User).limit(1)).scalar_one_or_none()
        if not user:
            click.echo("No users found.")
            return

        user.fast_name = 'test'
        user.fast_code = argon2_.hash("00000")
        server_db_.session.commit()

        click.echo(f"User: {repr(user)}")
        click.echo(f"Set fast_name to 'test' and fast_code to hashed '00000'.")
        return

    app_.cli.add_command(server)
