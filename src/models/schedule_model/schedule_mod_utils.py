import json
from datetime import datetime, timedelta
from flask_login import current_user
from src.routes.schedule.schedule_route_utils import get_week_days
from src.extensions import server_db_, logger
from config.settings import (
    SCHEDULE_PATH, EMPLOYEES_PATH, EMPLOYEE_ROLE
)



def update_employee(name: str, email: str | None = None) -> bool:
    from src.models.schedule_model.schedule_mod import Employees
    employee_name = Employees.crop_name(name)
    employee = Employees.query.filter_by(name=employee_name).first()
    if employee:
        employee.activate_employee(email)
        current_user.set_schedule_name(employee_name)
        current_user.add_roles(EMPLOYEE_ROLE)
        return True
    else:
        logger.log.error(f"Employee {employee_name} not found")
        return False


def add_employee(name: str, email: str) -> None:
    from src.models.schedule_model.schedule_mod import Employees
    employee = Employees(email=email,
                        name=name,
                        is_activated=True)
    server_db_.session.add(employee)
    server_db_.session.commit()


def add_employee_json(name: str, email: str, is_verified: bool) -> None:
    with open(EMPLOYEES_PATH, "r") as json_file:
        employees_data = json.load(json_file)
    
    employees_data[name] = {"email": "", "is_verified": False}
    
    sorted_employees_data = dict(sorted(employees_data.items()))
    
    with open(EMPLOYEES_PATH, "w") as json_file:
        json.dump(sorted_employees_data, json_file, indent=4)


def update_employee_json(name: str, email: str | None = None, is_verified: bool | None = None) -> None:
    with open(EMPLOYEES_PATH, "r") as json_file:
        employees_data = json.load(json_file)
    
    if name in employees_data:
        if email is not None:
            employees_data[name]["email"] = email
        if is_verified is not None:
            employees_data[name]["is_verified"] = is_verified
    
    with open(EMPLOYEES_PATH, "w") as json_file:
        json.dump(employees_data, json_file, indent=4)


def get_date_from_week_number(week_number: int, day: str) -> datetime:
    first_day_of_year = datetime(datetime.now().year, 1, 1)
    week_days = get_week_days()
    days_to_add = (week_number - 1) * 7 + week_days.index(day)
    return first_day_of_year + timedelta(days=days_to_add)


def _init_employees() -> None:
    """
    Initializes the employees in the database. Used in cli.
    """
    from src.models.schedule_model.schedule_mod import Employees
    with open(EMPLOYEES_PATH, "r") as json_file:
        employees_data = json.load(json_file)
    
    for employee, data in employees_data.items():
        employee_obj = Employees(name=employee)
        server_db_.session.add(employee_obj)
    server_db_.session.commit()


def _init_schedule() -> None:
    """
    Initializes the schedule in the database. Used in cli.
    """
    from src.models.schedule_model.schedule_mod import Schedule
    with open(SCHEDULE_PATH, "r") as json_file:
        schedule_data = json.load(json_file)
    
    for week_number, week_data in schedule_data.items():
        for day, day_data in week_data.items():
            names = day_data["names"]
            hours = [hour.split("|")[0] for hour in day_data["hours"]]
            date = get_date_from_week_number(int(week_number), day).date()
            
            schedule_item = Schedule(date=date,
                                     week_number=week_number,
                                     day=day,
                                     names=names,
                                     hours=hours)
            server_db_.session.add(schedule_item)
    server_db_.session.commit()
    
    
