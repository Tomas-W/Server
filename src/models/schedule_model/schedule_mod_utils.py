import json
import os
import random

from datetime import datetime
from flask import flash
from flask_login import current_user
from unidecode import unidecode

from src.models.schedule_model.schedule_mod import (
    Employees,
    Schedule,
)

from src.extensions import (
    server_db_,
    cache_,
    logger,
)

from src.models.auth_model.auth_mod_utils import get_user_by_employee_name
from src.models.schedule_model.schedule_mod import update_employee_json

from src.utils.schedule import (
    _date_from_week_day_year,
    _get_schedule_paths,
)
from src.utils.misc_utils import crop_name

from config.settings import (
    PATH,
    SERVER,
    Environ,
)

from src.utils.schedule import check_for_new_employees
from src.utils.encryption_utils import decrypt_data


@cache_.cached(timeout=0)
def get_schedule_bounds():
    """Returns earliest and latest schedule from database"""
    earliest = Schedule.query.order_by(Schedule.date.asc()).first()
    latest = Schedule.query.order_by(Schedule.date.desc()).first()
    return earliest, latest


def get_calendar_on_duty_days(dates: list[str]) -> list[str]:
    """
    Returns the list of dates where the current user is on duty.
    """
    date_objects = [datetime.strptime(date, '%d-%m-%Y').date() for date in dates]
    schedules = Schedule.query.filter(Schedule.date.in_(date_objects)).all()
    
    on_duty_dates = []
    for schedule in schedules:
        names = schedule.names.split('|')
        if current_user.employee_name in names:
            on_duty_dates.append(schedule.date.strftime('%d-%m-%Y'))
    
    return on_duty_dates


def activate_employee(name: str, code: str) -> bool:
    """ Activates the Employee in the database and JSON. """
    employee_name = crop_name(name)
    employee = Employees.query.filter_by(name=employee_name).first()
    if employee:
        if code == str(employee.code):
            employee.activate(current_user.email)
            current_user.set_employee_name(employee_name)
            current_user.add_roles(SERVER.EMPLOYEE_ROLE)
            return True
        else:
            flash("Invalid code")
            return False
    else:
        flash(f"Employee '{name}' not found")
        return False


def deactivate_employee(name: str) -> bool:
    """ Deactivates the Employee in the database and JSON. """
    employee_name = crop_name(name)
    employee = Employees.query.filter_by(name=employee_name).first()
    if employee:
        employee.deactivate()
        current_user.set_employee_name("")
        current_user.remove_roles(SERVER.EMPLOYEE_ROLE)
        return True
    else:
        return False


def deactivate_employee_cli(name: str):
    """ Deactivates the Employee in the database and JSON. """
    employee_name = crop_name(name)
    employee = Employees.query.filter_by(name=employee_name).first()
    if employee:
        employee.set_is_activated(False)
        employee.email = None
        update_employee_json(employee_name, is_verified=False, email="")
        user = get_user_by_employee_name(employee_name)
        if user:
            user.set_employee_name(None)
            user.remove_roles(SERVER.EMPLOYEE_ROLE)
            server_db_.session.commit()
            return True
    return False


def _init_employees() -> bool:
    """
    Initializes the employees in the database. Used in cli.
    """
    if not server_db_.session.query(Employees).count():
        try:
            with open(PATH.EMPLOYEES, "rb") as json_file:
                encrypted_data = json_file.read()
                employees_data = json.loads(decrypt_data(encrypted_data).decode())
        except FileNotFoundError:
            logger.exception(f"[SYS] FILE {PATH.EMPLOYEES} NOT FOUND")
            return False
        except json.JSONDecodeError:
            logger.exception(f"[SYS] ERROR DECODING JSON FROM FILE {PATH.EMPLOYEES}")
            return False
    
        for employee, _ in employees_data.items():
            code = random.randint(10000, 99999)
            employee_obj = Employees(name=employee, code=code)
            server_db_.session.add(employee_obj)
        server_db_.session.commit()
        return True
    else:
        return False


def _init_schedule() -> bool:
    """
    Initializes the schedule in the database. Used in cli.
    """
    if not server_db_.session.query(Schedule).count():
        schedule_paths = _get_schedule_paths()
        
        for path in schedule_paths:
            filename = os.path.basename(path)
            year = int(filename.split('schedule')[1].split('.json')[0])

            try:
                with open(path, "rb") as json_file:
                    encrypted_data = json_file.read()
                    schedule_data = json.loads(decrypt_data(encrypted_data).decode())
            except FileNotFoundError:
                logger.exception(f"[SYS] FILE {path} NOT FOUND")
                return False
            except json.JSONDecodeError:
                logger.exception(f"[SYS] ERROR DECODING JSON FROM FILE {path}")
                return False
            
            for week_number, week_data in schedule_data.items():
                for day, day_data in week_data.items():
                    # Use the year from the filename in date calculation
                    date = _date_from_week_day_year(int(week_number), day, year).date()
                    names = day_data["names"]
                    names = [unidecode(name) for name in names]
                    hours = day_data["hours"]
                    break_times = day_data["break_times"]
                    work_times = day_data["work_times"]
                    
                    schedule_item = Schedule(
                        date=date,
                        week_number=week_number,
                        day=day,
                        names=names,
                        hours=hours,
                        break_times=break_times,
                        work_times=work_times
                    )
                    server_db_.session.add(schedule_item)
                    unique_names = set(name for name in names)
                    logger.debug(f"[DEBUG] UNIQUE NAMES: {unique_names}")
                    check_for_new_employees(unique_names)

        server_db_.session.commit()
        return True
    else:
        return False

