import calendar
import json
import os
from datetime import datetime, timedelta
from flask_login import current_user
from src.routes.schedule.schedule_route_utils import _week_days, _week_from_date
from src.extensions import server_db_, logger
from config.settings import (
    EMPLOYEES_PATH, EMPLOYEE_ROLE, SCHEDULE_FOLDER
)


def save_schedule_to_db(date: str, names: list[str], hours: list[str],
                        break_times: list[str], work_times: list[str]) -> None:
    from src.models.schedule_model.schedule_mod import Schedule
    week_number = _week_from_date(date)
    day = _day_from_date(date)
    date_obj = datetime.strptime(date, "%d-%m-%Y").date()
    schedule_item = Schedule(date=date_obj,
                            week_number=week_number,
                            day=day,
                            names=names,
                            hours=hours,
                            break_times=break_times,
                            work_times=work_times)
    server_db_.session.add(schedule_item)
    server_db_.session.commit()
    logger.log.info(f"Saved schedule to db for date: '{date}'")


def update_employee(name: str, email: str | None = None) -> bool:
    """ Updates the employee in the database. """
    from src.models.schedule_model.schedule_mod import Employees
    employee_name = Employees.crop_name(name)
    employee = Employees.query.filter_by(name=employee_name).first()
    if employee:
        employee.activate_employee(email)
        current_user.set_employee_name(employee_name)
        current_user.add_roles(EMPLOYEE_ROLE)
        return True
    else:
        logger.log.error(f"Employee {employee_name} not found")
        return False


def add_employee(name: str, email: str) -> None:
    """ Adds a new Employee to the database. """
    from src.models.schedule_model.schedule_mod import Employees
    employee = Employees(email=email,
                        name=name,
                        is_activated=True)
    server_db_.session.add(employee)
    server_db_.session.commit()


def add_employee_json(name: str, email: str = None, is_verified: bool = None) -> None:
    """ Adds a new Employee to the employees json file. """
    with open(EMPLOYEES_PATH, "r") as json_file:
        employees_data = json.load(json_file)
    
    email = email if email is not None else ""
    is_verified = is_verified if is_verified is not None else False
    employees_data[name] = {"email": email, "is_verified": is_verified}
    
    sorted_employees_data = dict(sorted(employees_data.items()))
    with open(EMPLOYEES_PATH, "w") as json_file:
        json.dump(sorted_employees_data, json_file, indent=4)


def update_employee_json(name: str, email: str | None = None,
                         is_verified: bool | None = None) -> None:
    """ Updates the Employee in the Employees json file. """
    with open(EMPLOYEES_PATH, "r") as json_file:
        employees_data = json.load(json_file)
    
    if name in employees_data:
        if email is not None:
            employees_data[name]["email"] = email
        if is_verified is not None:
            employees_data[name]["is_verified"] = is_verified
    
    with open(EMPLOYEES_PATH, "w") as json_file:
        json.dump(employees_data, json_file, indent=4)


def _get_schedule_paths() -> list[str]:
    """ Returns the paths of the schedule files in the schedule folder. """
    files = os.listdir(SCHEDULE_FOLDER)
    schedule_files = [file for file in files if file.startswith("schedule") and file.endswith(".json")]
    schedule_paths = [os.path.join(SCHEDULE_FOLDER, path) for path in schedule_files]
    return schedule_paths


def _date_from_week_and_day(week_number: int, day: str) -> datetime:
    """ Returns the date of the first day of the given week. """
    first_day_of_year = datetime(datetime.now().year, 1, 1)
    week_days = _week_days()
    days_to_add = (week_number - 1) * 7 + week_days.index(day)
    return first_day_of_year + timedelta(days=days_to_add)


def _day_from_date(date_str: str) -> str:
    """
    Returns the day of the week for the given date.
    Required format: 'dd-mm-yyyy'
    """
    date_obj = datetime.strptime(date_str, "%d-%m-%Y").date()
    return calendar.day_name[date_obj.weekday()]


def _init_employees() -> bool | None:
    """
    Initializes the employees in the database. Used in cli.
    """
    from src.models.schedule_model.schedule_mod import Employees
    
    if not server_db_.session.query(Employees).count():
        try:
            with open(EMPLOYEES_PATH, "r") as json_file:
                employees_data = json.load(json_file)
        except FileNotFoundError:
            logger.log.error(f"File {EMPLOYEES_PATH} not found")
            return False
    
        for employee, _ in employees_data.items():
            employee_obj = Employees(name=employee)
            server_db_.session.add(employee_obj)
        server_db_.session.commit()
        return True
    else:
        return False


def _init_schedule() -> bool | None:
    """
    Initializes the schedule in the database. Used in cli.
    """
    from src.models.schedule_model.schedule_mod import Schedule
    
    if not server_db_.session.query(Schedule).count():
        schedule_paths = _get_schedule_paths()
        for path in schedule_paths:
            with open(path, "r") as json_file:
                schedule_data = json.load(json_file)
            
            for week_number, week_data in schedule_data.items():
                for day, day_data in week_data.items():
                    date = _date_from_week_and_day(int(week_number), day).date()
                    names = day_data["names"]
                    hours = day_data["hours"]
                    break_times = day_data["break_times"]
                    work_times = day_data["work_times"]
                    
                    schedule_item = Schedule(date=date,
                                            week_number=week_number,
                                            day=day,
                                            names=names,
                                            hours=hours,
                                            break_times=break_times,
                                            work_times=work_times)
                    server_db_.session.add(schedule_item)
        server_db_.session.commit()
        return True
    else:
        return False

