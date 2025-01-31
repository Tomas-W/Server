import click
import json

from flask import Flask

from src.extensions import (
    server_db_,
    logger,
)

from src.models.auth_model.auth_mod import User
from src.models.schedule_model.schedule_mod import Employees
from src.models.schedule_model.schedule_mod_utils import (
    _init_employees,
    _init_schedule,
    update_employee_json,
)

from src.utils.schedule import (
    _get_schedule_paths,
    update_schedule,
)
from src.utils.misc_utils import crop_name
from src.utils.encryption_utils import decrypt_data

from config.settings import PATH, SERVER


@click.group()
def schedule():
    """Schedule CLI commands."""
    pass

def schedule_cli(app_: Flask) -> None:
    @schedule.command("init-schedule")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_schedule(v: bool, c: bool) -> None:
        """
        Initializes the Schedule Table.

        Usage: flask schedule init-schedule [--v] [--c]
        """
        paths = _get_schedule_paths()
        nr_weeks = 0

        for path in paths:
            try:
                # Open the encrypted schedule file in binary mode
                with open(path, "rb") as json_file:
                    encrypted_data = json_file.read()

                # Decrypt the data
                decrypted_data = decrypt_data(encrypted_data.decode())

                # Load the decrypted JSON data
                schedule_data = json.loads(decrypted_data)

                nr_weeks += len(schedule_data)

            except FileNotFoundError:
                click.echo(f"File not found: {path}")
                return
            except json.JSONDecodeError:
                click.echo(f"Error decoding JSON from file: {path}")
                return

        if not c and not click.confirm(
                f"Are you sure you want to add {nr_weeks} weeks to the Schedule Table?"):
            click.echo("Adding ScheduleItems cancelled.")
            return

        may_init_schedule: bool = _init_schedule()
        if not may_init_schedule:
            click.echo("Adding ScheduleItems failed.\n"
                       "Schedule Table not empty.")
            return

        logger.info(f"[CLI] INIT SCHEDULE: {nr_weeks} weeks added.")
        if v:
            click.echo(f"Successfully added {nr_weeks} weeks to the Schedule Table.")

    @schedule.command("add-week")
    @click.argument("week_number", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def add_week(week_number: int, c: bool, v: bool) -> None:
        """
        Updates the Schedule with the given week number.

        Usage: flask schedule add-week <week_number>
        """
        if not c and not click.confirm(
                f"Are you sure you want to add the Schedule for week {week_number}?"):
            click.echo("Adding Schedule cancelled.")
            return
        
        
        update_schedule(week_number)
        logger.info(f"[CLI] ADD SCHEDULE: week {week_number} added.")
        if v:
            click.echo(f"Successfully added Schedule for week {week_number}.")

    @schedule.command("init-employees")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_employees(v: bool, c: bool) -> None:
        """
        Adds Employees from employees.json to the Employees Table.

        Usage: flask schedule init-employees [--v] [--c]
        """
        with open(PATH.EMPLOYEES, "rb") as json_file:
            encrypted_data = json_file.read()

        decrypted_data = decrypt_data(encrypted_data.decode())
        employees_data = json.loads(decrypted_data)
        for employee, _ in employees_data.items():
            logger.debug(employee)
        
        
        nr_employees = len(employees_data)
        if not c and not click.confirm(
                f"Are you sure you want to add {nr_employees} Employees to the Employees Table?"):
            click.echo("Adding Employees cancelled.")
            return
        
        may_init_employees: bool = _init_employees()
        if not may_init_employees:
            click.echo("Adding Employees failed.\n"
                       "Employees Table not empty.")
            return
        
        logger.info(f"[CLI] INIT EMPLOYEES: {nr_employees} employees added.")
        if v:
            click.echo(f"Successfully added {nr_employees} Employees to the Employees Table.")
    
    @schedule.command("activate")
    @click.argument("user_id", type=int)
    @click.argument("name", type=str)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def activate(user_id: int, name: str, v: bool, c: bool) -> None:
        """
        Activates the Employee in the database and JSON.

        Usage: flask schedule activate <name> [--v] [--c]
        """
        if not c and not click.confirm(
                f"Are you sure you want to activate Employee {name}?"):
            click.echo("Activating Employee cancelled.")
            return
        
        employee_name = crop_name(name)
        employee = Employees.query.filter_by(name=employee_name).first()
        if not employee:
            click.echo(f"Employee {employee_name} not found.")
            return
        
        user = User.query.get(user_id)
        if not user:
            click.echo(f"User {user_id} not found.")
            return
        
        try:
            employee.set_is_activated(True)
            employee.email = user.email
            update_employee_json(employee_name, email=user.email)
            user.set_employee_name(employee_name)
            user.add_roles(SERVER.EMPLOYEE_ROLE)
            server_db_.session.commit()
        except Exception as e:
            click.echo(f"Failed to activate Employee {name}: {e}")
            return
        
        click.echo(f"Successfully activated Employee {name}.")
    
    @schedule.command("deactivate")
    @click.argument("user_id", type=int)
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def deactivate(user_id: int, v: bool, c: bool) -> None:
        """
        Deactivates the Employee in the database and JSON.

        Usage: flask schedule deactivate <user_id> [--v] [--c]
        """
        user = User.query.get(user_id)
        if not user:
            click.echo(f"User {user_id} not found.")
            return
        
        if not user.employee_name:
            click.echo(f"User {user_id} is not an Employee.")
            return

        if not c and not click.confirm(
                f"Are you sure you want to deactivate Employee {user.employee_name}?"):
            click.echo("Deactivating Employee cancelled.")
            return
        
        employee_name = crop_name(user.employee_name)
        employee = Employees.query.filter_by(name=employee_name).first()
        if not employee:
            click.echo(f"Employee {employee_name} not found.")
            return
        
        try:
            employee.set_is_activated(False)
            employee.email = None
            update_employee_json(employee_name, is_verified=False, email="")
            user.set_employee_name(None)
            user.remove_roles(SERVER.EMPLOYEE_ROLE)
            server_db_.session.commit()
        except Exception as e:
            click.echo(f"Failed to deactivate Employee {user.employee_name}: {e}")
            return
        
        click.echo(f"Successfully deactivated Employee {user.employee_name}.")


    app_.cli.add_command(schedule)

