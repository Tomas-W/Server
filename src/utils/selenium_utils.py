from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import random
import time

from src.extensions import logger


def movement(driver: webdriver.Firefox) -> None:
    """
    Scrolls the page and waits for a random amount of time.
    """
    random_sleep()
    human_like_scroll(driver)
    random_sleep()


def get_undetectable_driver(proxy: str | None = None) -> webdriver.Firefox:
    """
    Returns a driver with a random user agent and a random window size.
    """
    options = FirefoxOptions()
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
    ]
    
    options.set_preference("general.useragent.override", random.choice(user_agents))
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    
    if proxy:
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.http", proxy)
        options.set_preference("network.proxy.http_port", 80)
    
    driver = webdriver.Firefox(options=options)
    
    window_sizes = [(1920, 1080), (1366, 768), (1536, 864), (1440, 900)]
    random_size = random.choice(window_sizes)
    driver.set_window_size(*random_size)

    logger.info(f"[ADD] Driver created with window size: {random_size}")
    return driver


def random_sleep(min_seconds: float = 1, max_seconds: float = 2) -> None:
    """
    Sleeps for a random amount of time between min_seconds and max_seconds.
    """
    time.sleep(random.uniform(min_seconds, max_seconds))


def human_like_scroll(driver: webdriver.Firefox) -> None:
    """
    Scrolls the page in a human-like manner.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        scroll_amount = random.randint(100, 800)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        random_sleep(0.1, 0.3)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
