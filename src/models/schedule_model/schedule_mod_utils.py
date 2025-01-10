import json
import os
from flask_login import current_user

from src.utils.schedule import _date_from_week_day_year
from src.extensions import server_db_, logger
from config.settings import (
    EMPLOYEES_PATH, EMPLOYEE_ROLE
)


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
    from src.utils.schedule import _date_from_week_day_year, _get_schedule_paths
    
    if not server_db_.session.query(Schedule).count():
        schedule_paths = _get_schedule_paths()
        
        for path in schedule_paths:
            # Extract filename from path
            filename = os.path.basename(path)
            year = int(filename.split('schedule')[1].split('.json')[0])

            with open(path, "r") as json_file:
                schedule_data = json.load(json_file)
            
            for week_number, week_data in schedule_data.items():
                for day, day_data in week_data.items():
                    # Use the year from the filename in date calculation
                    date = _date_from_week_day_year(int(week_number), day, year).date()
                    names = day_data["names"]
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

        server_db_.session.commit()
        return True
    else:
        return False

