import json
import os
import time

from datetime import datetime, timedelta, date

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from config.settings import SCHEDULE_PATH
from src.extensions import logger

USERNAME = os.getenv("S_USERNAME")
PASSWORD = os.getenv("S_PASSWORD")
LOGIN_URL = os.getenv("S_LOGIN_URL")
SCHEDULE_URL = os.getenv("S_SCHEDULE_URL")


def get_week_number(date_obj: date) -> int:
    return date_obj.isocalendar()[1]


def get_week_days() -> list[str]:
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    return [(start_of_week + timedelta(days=i)).strftime("%A") for i in range(7)]


def get_next_week_dates() -> list[str]:
    """Returns a list of the next week (mon-fri) in the format 'dd-mm-yyyy'"""
    today = datetime.today()
    days_until_monday = (7 - today.weekday() + 0) % 7
    next_monday = today + timedelta(days=days_until_monday)
    
    next_week_dates = [(next_monday + timedelta(days=i)).strftime("%d-%m-%Y") for i in range(7)]
    return next_week_dates


def get_five_week_dates() -> list[str]:
    """Returns a list of dates from the Monday two weeks ago to the Sunday two weeks from now in the format 'dd-mm-yyyy'"""
    today = datetime.today()
    days_since_monday = today.weekday()
    start_date = today - timedelta(days=days_since_monday + 14)  # Monday two weeks ago
    end_date = start_date + timedelta(days=35)  # Sunday two weeks from now
    
    four_week_dates = [(start_date + timedelta(days=i)).strftime("%d-%m-%Y") for i in range(28)]
    return four_week_dates


def get_driver():
    driver = webdriver.Firefox()
    return driver


def log_in(driver: webdriver.Firefox) -> None:    
    driver.get(LOGIN_URL)
    time.sleep(3)
    
    username_input = driver.find_element(By.ID, "loginUsername")
    username_input.send_keys(USERNAME)
    
    password_input = driver.find_element(By.ID, "loginPassword")
    password_input.send_keys(PASSWORD)
    
    time.sleep(1)
    login_btn = driver.find_element(By.ID, "login-button")
    login_btn.click()
    logger.log.info("Logged in to PMT")


def get_names_and_hours_per_day(driver: webdriver.Firefox,
                                date: str) -> tuple[list[str], list[str]]:
    url = f"{SCHEDULE_URL}{date}"
    driver.get(url)
    logger.log.info(f"Navigated to {url}")
    time.sleep(2)
    names = driver.find_elements(By.CLASS_NAME, 'name.d-inline')
    logger.log.info("Names saved")
    hours = driver.find_elements(By.CLASS_NAME, 'shift-block-content')
    logger.log.info("Hours saved")
    return names, hours


def save_schedule_to_json(names: list[str], hours: list[str]) -> None:
    today = date.today()
    week_number = get_week_number(today)

    week_data = {}
    days = get_week_days()
    for day, name_list, hour_list in zip(days, names, hours):
        week_data[day] = {
            "names": name_list,
            "hours": hour_list.split("|")[0]
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
    driver = get_driver()
    log_in(driver)
    
    dates = get_next_week_dates()
    names = []
    hours = []

    for date in dates:
        names_elements, hours_elements = get_names_and_hours_per_day(driver, date)
        
        names.append([name.text for name in names_elements])
        hours.append([hour.text for hour in hours_elements])
        
        logger.log.info(f"Saved: {date}")

    driver.quit()
    
    save_schedule_to_json(names, hours)
    logger.log.info("Saved schedule to json")


def test_update_schedule() -> None:
    driver = get_driver()
    log_in(driver)
    
    dates = get_five_week_dates()
    names = []
    hours = []

    for date in dates:
        names_elements, hours_elements = get_names_and_hours_per_day(driver, date)
        
        names.append([name.text for name in names_elements])
        hours.append([hour.text for hour in hours_elements])
        
        logger.log.info(f"Saved: {date}")

    driver.quit()
    
    save_schedule_to_json(names, hours)
    logger.log.info("Saved schedule to json")