import json
import os
import calendar
import time
from datetime import datetime, timedelta
from flask import request
from flask_login import current_user
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from src.utils.selenium_utils import (
    get_undetectable_driver, movement
)

from src.extensions import logger
from config.settings import SCHEDULE_PATH, SCHEDULE_FOLDER


S_USERNAME = os.getenv("S_USERNAME")
S_PASSWORD = os.getenv("S_PASSWORD")
S_LOGIN_URL = os.getenv("S_LOGIN_URL")
S_SCHEDULE_URL = os.getenv("S_SCHEDULE_URL")


def get_personal_schedule_dicts() -> list[list[dict]]:
    """
    Returns the personal schedule for the current week up to the latest week.
    """
    from src.models.schedule_model.schedule_mod import Schedule
    current_week_num = _week_from_date(_now())
    latest_schedules = Schedule.query.filter(Schedule.week_number >= current_week_num).order_by(Schedule.date.desc()).all()[::-1]
    
    schedules = []
    for i in range(0, len(latest_schedules), 7):
        week = latest_schedules[i:i+7]
        week_dicts = [schedule.to_personal_dict(current_user.schedule_name) for schedule in week]
        schedules.append(week_dicts)
    
    return schedules


def personal_dicts_to_calendar_dicts(personal_dicts: list[dict]) -> list[dict]:
    pass


def get_requested_date(date: str | None = None) -> datetime.date:
    """
    Returns the date requested by the user by 
     adding or subtracting 1 day from the previous date.
    """
    sub = request.args.get("sub", "False") == "True"
    add = request.args.get("add", "False") == "True"
    
    if not date:
        today_date = datetime.now().date()
    else:
        today_date = datetime.strptime(date, "%d-%m-%Y").date()
        
    if sub:
        today_date -= timedelta(days=1)
    elif add:
        today_date += timedelta(days=1)

    return today_date


def update_schedule() -> None:
    """
    Looks for new schedule 2 weeks from now,
     collects names and hours for each day,
     saves them to a json file grouped by week number.
    """
    from src.models.schedule_model.schedule_mod_utils import save_schedule_to_db
    driver = get_undetectable_driver()
    log_in(driver)
    movement(driver)
    
    dates = get_new_schedule_dates()
    names_list = []
    hours_list = []
    break_times_list = []
    work_times_list = []
    date = dates[-1]

    for date in dates:
        names, hours, break_times, work_times = get_schedule_info_per_date(driver, date)
        
        names_list.append([name for name in names])
        hours_list.append([hour for hour in hours])
        break_times_list.append([break_time for break_time in break_times])
        work_times_list.append([work_time for work_time in work_times])
        
        save_schedule_to_db(date, names, hours, break_times, work_times)
        
    save_schedule_to_json(date, names_list, hours_list, break_times_list, work_times_list)

    logger.log.info("New schedule has been added to JSON")
    driver.quit()


def get_new_schedule_dates() -> list[str]:
    """
    Returns a list of dates in the format 'dd-mm-yyyy' for the newest schedule.
    New schedule is the week 2 weeks from now.
    """
    today = datetime.today()
    days_until_monday = (7 - today.weekday() + 0) % 7
    next_monday = today + timedelta(days=days_until_monday + 14)
    
    next_week_dates = [(next_monday + timedelta(days=i)).strftime("%d-%m-%Y") for i in range(7)]
    return next_week_dates


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
    logger.log.info("Logged in to PMT")
    time.sleep(2)


def get_schedule_info_per_date(driver: webdriver.Firefox,
                                date: str) -> tuple[list[str], list[str], list[str], list[str]]:
    """
    Returns a tuple of lists of names, hours, break times and work times for a given date.
    Date format: 'dd-mm-yyyy'
    """
    url = f"{S_SCHEDULE_URL}{date}"
    driver.get(url)
    logger.log.info(f"Navigated to: '{url}'")
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
    
    logger.log.info(f"Collected schedule data for: '{date}'")
    return names, hours, break_times, work_times


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
    if os.path.exists(schedule_path):
        with open(schedule_path, "r") as json_file:
            existing_data = json.load(json_file)

        existing_data.update(data_to_save)
        with open(schedule_path, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)

    else:
        with open(schedule_path, "w") as json_file:
            json.dump(data_to_save, json_file, indent=4)
    
    logger.log.info(f"Saved schedule to json for week: '{week_number}'")


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
    if _week_from_date(date) == 1:
        year = date[-4:]
        path = f"{SCHEDULE_PATH.split('.')[0]}{year}.json"
        return path
    
    files = os.listdir(SCHEDULE_FOLDER)
    schedule_files = [int(file.split(".")[0][-4:]) for file in files if file.startswith("schedule") and file.endswith(".json")]
    latest_year = max(schedule_files)
    return os.path.join(SCHEDULE_FOLDER, f"schedule{latest_year}.json")
