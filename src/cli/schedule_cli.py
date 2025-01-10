import click
import json
from flask import Flask

from src.models.schedule_model.schedule_mod_utils import (
    _init_schedule, _init_employees
)
from src.utils.schedule import _get_schedule_paths, update_schedule
from config.settings import (
    EMPLOYEES_PATH
)


def schedule_cli(app_: Flask) -> None:
    @click.group()
    def schedule() -> None:
        """CLI functionality for the Schedule Table"""
        pass

    @schedule.command("init-schedule")
    @click.option("--v", is_flag=True, help="Enables verbose mode.")
    @click.option("--c", is_flag=True, help="Confirm without prompting.")
    def init_schedule(c: bool, v: bool) -> None:
        """
        Adds Schedules from schedule*.json to the Schedule Table.

        Usage: flask schedule init-schedule [--v] [--c]
        """
        paths = _get_schedule_paths()
        nr_weeks = 0
        for path in paths:
            with open(path, "r") as json_file:
                schedule_data = json.load(json_file)
            nr_weeks += len(schedule_data)
        
        if not c and not click.confirm(
                f"Are you sure you want to add {nr_weeks} weeks to the Schedule Table?"):
            click.echo("Adding ScheduleItems cancelled.")
            return
        
        may_init_schedule: bool | None = _init_schedule()
        if not may_init_schedule:
            click.echo("Adding ScheduleItems failed.\n"
                       "Schedule Table not empty.")
            return
        
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
        with open(EMPLOYEES_PATH, "r") as json_file:
            employees_data = json.load(json_file)
        
        nr_employees = len(employees_data)
        if not c and not click.confirm(
                f"Are you sure you want to add {nr_employees} Employees to the Employees Table?"):
            click.echo("Adding Employees cancelled.")
            return
        
        may_init_employees: bool | None = _init_employees()
        if not may_init_employees:
            click.echo("Adding Employees failed.\n"
                       "Employees Table not empty.")
            return
        
        if v:
            click.echo(f"Successfully added {nr_employees} Employees to the Employees Table.")

    app_.cli.add_command(schedule)
