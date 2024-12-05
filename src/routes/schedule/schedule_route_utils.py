import json
import os
import calendar

from datetime import datetime, timedelta
from flask import request
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from src.utils.selenium_utils import (
    get_undetectable_driver, movement
)
from src.extensions import logger
from config.settings import SCHEDULE_PATH


S_USERNAME = os.getenv("S_USERNAME")
S_PASSWORD = os.getenv("S_PASSWORD")
S_LOGIN_URL = os.getenv("S_LOGIN_URL")
S_SCHEDULE_URL = os.getenv("S_SCHEDULE_URL")


def get_requested_date(date: str | None = None) -> datetime.date:
    sub = request.args.get("sub", "False") == "True"
    add = request.args.get("add", "False") == "True"
    
    if not date:
        today_date = datetime.now().date()
        logger.log.info(f"date is: {today_date}")
        logger.log.info(type(today_date))
    else:
        today_date = datetime.strptime(date, "%Y-%m-%d").date()
        
    if sub:
        today_date -= timedelta(days=1)
    elif add:
        today_date += timedelta(days=1)

    return today_date


def get_week_number(date_str: str) -> int:
    """
    Returns the week number of the given date.
    Required format: 'dd-mm-yyyy'
    """
    date_obj = datetime.strptime(date_str, "%d-%m-%Y").date()
    return date_obj.isocalendar()[1]


def get_week_days() -> list[str]:
    """
    Returns the string representation of the days of the week.
    """
    day_names = [calendar.day_name[day] for day in range(7)]
    return day_names


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


def get_five_weeks_dates() -> list[list[str]]:
    today = datetime.today()
    days_since_monday = today.weekday()
    start_date = today - timedelta(days=days_since_monday + 14)
    end_date = start_date + timedelta(days=34)
    
    five_week_dates = []
    current_date = start_date
    while current_date <= end_date:
        week_dates = [(current_date + timedelta(days=i)).strftime("%d-%m-%Y") for i in range(7)]
        five_week_dates.append(week_dates)
        current_date += timedelta(days=7)
    
    return five_week_dates


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


def get_names_and_hours_per_day(driver: webdriver.Firefox,
                                date: str) -> tuple[list[str], list[str]]:
    """
    Returns a tuple of lists of names and hours for a given date.
    """
    url = f"{S_SCHEDULE_URL}{date}"
    driver.get(url)
    logger.log.info(f"Navigated to {url}")
    movement(driver)
    
    rows = driver.find_elements(By.CLASS_NAME, "employee-row")
    names = []
    hours = []
    
    for row in rows:
        name_element = row.find_element(By.CLASS_NAME, "name.d-inline")
        hour_elements = row.find_elements(By.CLASS_NAME, "shift-block-content")
        
        names.append(name_element.text)
        hours.append(hour_elements[0].text)
        
        if len(hour_elements) > 1:
            names.append(name_element.text)
            hours.append(hour_elements[1].text)
    
    logger.log.info("Names and hours saved")
    return names, hours


def save_schedule_to_json(names: list[str], hours: list[str], date: str) -> None:
    """
    Saves the names and hours to a json file.
    Groups days by week number.
    """
    week_number = get_week_number(date)

    week_data = {}
    days = get_week_days()
    for day, name_list, hour_list in zip(days, names, hours):
        week_data[day] = {
            "names": name_list,
            "hours": [hour.split("|")[0] for hour in hour_list]
        }

    data_to_save = {
        str(week_number): week_data
    }
    if os.path.exists(SCHEDULE_PATH):
        with open(SCHEDULE_PATH, "r") as json_file:
            existing_data = json.load(json_file)

        existing_data.update(data_to_save)

        with open(SCHEDULE_PATH, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)

    else:
        with open(SCHEDULE_PATH, "w") as json_file:
            json.dump(data_to_save, json_file, indent=4)


def update_schedule() -> None:
    """
    Looks for new schedule 2 weeks from now,
     collects names and hours for each day,
     saves them to a json file grouped by week number.
    """
    driver = get_undetectable_driver()
    log_in(driver)
    
    movement(driver)
    
    dates = get_new_schedule_dates()
    names = []
    hours = []

    for date in dates:
        names_elements, hours_elements = get_names_and_hours_per_day(driver, date)
        
        names.append([name.text for name in names_elements])
        hours.append([hour.text for hour in hours_elements])
        
        save_schedule_to_json(names, hours, date)
        logger.log.info(f"Saved: {date}")

    logger.log.info("Saved schedule to json")
    driver.quit()


def test_update_schedule() -> None:
    """
    Looks for new schedule 2 weeks from now,
     collects names and hours for each day,
     saves them to a json file grouped by week number.
    """
    driver = get_undetectable_driver()
    log_in(driver)
    
    movement(driver)
    
    weeks = get_five_weeks_dates()
    for week in weeks:
        names = []
        hours = []
        
        for date in week:
            names_elements, hours_elements = get_names_and_hours_per_day(driver, date)
            
            names.append(names_elements)
            hours.append(hours_elements)
            
        save_schedule_to_json(names, hours, date)
        logger.log.info(f"Saved: {get_week_number(date)}")

    logger.log.info("Saved schedule to json")
    driver.quit()
