import calendar
import json
import os
import time

from datetime import (
    datetime,
    timedelta,
)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.extensions import logger, server_db_

from src.utils.misc_utils import crop_name
from src.utils.selenium_utils import (
    get_undetectable_driver, movement
)

from config.settings import DIR, PATH


S_USERNAME = os.getenv("S_USERNAME")
S_PASSWORD = os.getenv("S_PASSWORD")
S_LOGIN_URL = os.getenv("S_LOGIN_URL")
S_SCHEDULE_URL = os.getenv("S_SCHEDULE_URL")


def update_schedule(week_number: int | None = None) -> None:
    """
    If week_number is not provided the schedule 2 weeks from now is collected.
    Data is saved to the database and json file.
    New employees are added to the database and json file.
    """
    driver = get_undetectable_driver()
    log_in(driver)
    movement(driver)
    
    if week_number is None:
        dates = get_new_schedule_dates()
        logger.info(f"[ADD] Getting new schedules for week: {_week_from_date(dates[0])}")
    else:
        dates = get_new_schedule_dates_by_week(week_number)
        logger.info(f"[ADD] Getting new schedules for week: {week_number}")

    names_list = []
    hours_list = []
    break_times_list = []
    work_times_list = []
    date = dates[-1]

    for date in dates:
        names, hours, break_times, work_times = get_schedule_info_per_date(driver, date)
        names = [crop_name(name) for name in names]
        
        names_list.append([name for name in names])
        hours_list.append([hour for hour in hours])
        break_times_list.append([break_time for break_time in break_times])
        work_times_list.append([work_time for work_time in work_times])
        
        
        save_schedule_to_db(date, names, hours, break_times, work_times)

    save_schedule_to_json(date, names_list, hours_list, break_times_list, work_times_list)

    driver.quit()
    
    unique_names = set(name for sublist in names_list for name in sublist)
    check_for_new_employees(unique_names)


def log_in(driver: webdriver.Firefox) -> None:
    """ Logs in to PMT. """
    driver.get(S_LOGIN_URL)
    movement(driver)
    
    username_input = driver.find_element(By.ID, "loginUsername")
    username_input.send_keys(S_USERNAME)
    password_input = driver.find_element(By.ID, "loginPassword")
    password_input.send_keys(S_PASSWORD)
    
    movement(driver)
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "login-button"))
    )
    driver.execute_script("arguments[0].click();", login_btn)
    logger.info("[ADD] Logged in to PMT")
    time.sleep(2)


def get_new_schedule_dates() -> list[str]:
    """
    Returns a list of dates in the format 'dd-mm-yyyy' for the newest schedule.
    New schedule is the week 2 weeks from now.
    """
    today = datetime.today()
    days_until_monday = (7 - today.weekday() + 0) % 7
    next_monday = today + timedelta(days=days_until_monday + 7)
    
    next_schedule_dates = [(next_monday + timedelta(days=i)).strftime("%d-%m-%Y") for i in range(7)]
    return next_schedule_dates


def get_new_schedule_dates_by_week(week_number: int) -> list[str]:
    """
    Returns a list of dates in the format 'dd-mm-yyyy' for the schedule
    corresponding to the given week number.
    """
    today = datetime.today()
    first_weekday = datetime(today.year, 1, 1).weekday()
    days_until_first_monday = (7 - first_weekday) % 7
    first_monday = datetime(today.year, 1, 1) + timedelta(days=days_until_first_monday)
    
    week_start_date = first_monday + timedelta(weeks=week_number - 2)
    week_dates = [(week_start_date + timedelta(days=i)).strftime("%d-%m-%Y") for i in range(7)]
    
    return week_dates


def get_schedule_info_per_date(driver: webdriver.Firefox,
                                date: str) -> tuple[list[str], list[str], list[str], list[str]]:
    """
    Returns a tuple of lists of names, hours, break times and work times for a given date.
    Date format: 'dd-mm-yyyy'
    """
    url = f"{S_SCHEDULE_URL}{date}"
    driver.get(url)
    logger.info(f"Navigated to: '{url}'")
    movement(driver)
    
    rows = driver.find_elements(By.CLASS_NAME, "employee-row")
    names = []
    hours = []
    break_times = []
    work_times = []
    
    for row in rows:
        name_element = row.find_element(By.CLASS_NAME, "name.d-inline")
        names.append(name_element.text)
        
        hour_elements = row.find_elements(By.CLASS_NAME, "shift-block-content")
        hours.append(hour_elements[0].text.split("|")[0])
        
        break_time_element = row.find_element(By.CLASS_NAME, "break")
        break_times.append(break_time_element.text)
        
        work_time_element = row.find_element(By.CLASS_NAME, "worked")
        work_times.append(work_time_element.text)
        
        if len(hour_elements) > 1:
            names.append(name_element.text)
            hours.append(hour_elements[1].text.split("|")[0].strip())
    
    logger.info(f"Collected schedule data for: '{date}'")
    return names, hours, break_times, work_times


def save_schedule_to_db(date: str, names: list[str], hours: list[str],
                        break_times: list[str], work_times: list[str]) -> None:
    """
    Saves schedule data per date to the database.
    """
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
    logger.info(f"[ADD] Saved schedule to db for date: {date}")


def save_schedule_to_json(date: str, names: list[str], hours: list[str],
                          break_times: list[str], work_times: list[str]) -> None:
    """
    Saves schedule data to a json file.
    Grouped by week number.
    """
    week_number = _week_from_date(date)
    schedule_path = _schedule_path_from_date(date)

    week_data = {}
    days = _week_days()
    for day, name_list, hour_list, break_time_list, work_time_list in \
        zip(days, names, hours, break_times, work_times):
        week_data[day] = {
            "names": name_list,
            "hours": hour_list,
            "break_times": break_time_list,
            "work_times": work_time_list
        }

    data_to_save = {
        str(week_number): week_data
    }
    
    try:
        if os.path.exists(schedule_path):
            try:
                with open(schedule_path, "r", encoding="utf-8") as json_file:
                    existing_data = json.load(json_file)
            except json.JSONDecodeError:
                existing_data = {}

            existing_data.update(data_to_save)
            with open(schedule_path, "w", encoding="utf-8") as json_file:
                json.dump(existing_data, json_file, indent=4)
        else:
            with open(schedule_path, "w", encoding="utf-8") as json_file:
                json.dump(data_to_save, json_file, indent=4)
                
        logger.info(f"[ADD] Saved schedule to json for week: {week_number}")
    
    except PermissionError:
        logger.critical(f"[SYS] PERMISSION DENIED when accessing: {schedule_path}")
        return
    except Exception as e:
        logger.warning(f"[ERROR] UNEXPECTED ERROR saving schedule to json: {str(e)}")
        return


def check_for_new_employees(names: list[str]) -> None:
    """
    Checks for new employees in the schedule and adds them to the DB and JSON.
    """
    if not names:
        return
    
    from src.models.schedule_model.schedule_mod import Employees
    names = [crop_name(name) for name in names]
    for name in names:
        if not Employees.query.filter_by(name=name).first():
            Employees.add_employee(name)
            add_employee_json(name)


def add_employee_json(name: str, email: str = None, is_verified: bool = None) -> None:
    """ Adds a new Employee to the employees json file. """
    with open(PATH.EMPLOYEES, "r") as json_file:
        employees_data = json.load(json_file)
    
    email = email if email is not None else ""
    is_verified = is_verified if is_verified is not None else False
    employees_data[name] = {"email": email, "is_verified": is_verified}
    
    sorted_employees_data = dict(sorted(employees_data.items()))
    try:
        with open(PATH.EMPLOYEES, "w") as json_file:
            json.dump(sorted_employees_data, json_file, indent=4)
    except PermissionError:
        logger.critical(f"[SYS] PERMISSION DENIED when accessing: {PATH.EMPLOYEES}")
        return
    except Exception as e:
        logger.warning(f"[ERROR] UNEXPECTED ERROR adding Employees to json: {str(e)}")
        return


def _now() -> datetime.date:
    """ Returns the current date in the format 'dd-mm-yyyy'. """
    return datetime.now().strftime("%d-%m-%Y")


def _week_days() -> list[str]:
    """
    Returns the string representation of the days of the week.
    """
    day_names = [calendar.day_name[day] for day in range(7)]
    return day_names


def _week_from_date(date_str: str) -> int:
    """
    Returns the week number of the given date.
    Required format: 'dd-mm-yyyy'
    """
    date_obj = datetime.strptime(date_str, "%d-%m-%Y").date()
    return date_obj.isocalendar()[1]


def _schedule_path_from_date(date: str) -> str:
    """
    Returns the path to the schedule's JSON file for the given date.
    """
    if _week_from_date(date) == 1:
        year = date[-4:]
        path = f"schedule{year}.json"
        return os.path.join(DIR.SCHEDULE, path)
    
    files = os.listdir(DIR.SCHEDULE)
    schedule_files = [int(file.split(".")[0][-4:]) for file in files if file.startswith("schedule") and file.endswith(".json")]
    latest_year = max(schedule_files)
    return os.path.join(DIR.SCHEDULE, f"schedule{latest_year}.json")


def update_employee_json(name: str, email: str | None = None,
                         is_verified: bool | None = None) -> None:
    """ Updates the Employee in the Employees json file. """
    with open(PATH.EMPLOYEES, "r") as json_file:
        employees_data = json.load(json_file)
    
    if name in employees_data:
        if email is not None:
            employees_data[name]["email"] = email
        if is_verified is not None:
            employees_data[name]["is_verified"] = is_verified
    
    try:
        with open(PATH.EMPLOYEES, "w") as json_file:
            json.dump(employees_data, json_file, indent=4)
    except PermissionError:
        logger.critical(f"[SYS] PERMISSION DENIED when accessing: {PATH.EMPLOYEES}")
        return
    except Exception as e:
        logger.warning(f"[ERROR] UNEXPECTED ERROR updating Employees in json: {str(e)}")
        return


def _get_schedule_paths() -> list[str]:
    """ Returns the paths of the schedule files in the schedule folder. """
    files = os.listdir(DIR.SCHEDULE)
    schedule_files = [file for file in files if file.startswith("schedule") and file.endswith(".json")]
    schedule_paths = [os.path.join(DIR.SCHEDULE, path) for path in schedule_files]
    return schedule_paths


def _date_from_week_day_year(week_number: int, day: str, year: int) -> datetime:
    """ Returns the date of the first day of the given week. """
    first_day_of_year = datetime(year, 1, 1)
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