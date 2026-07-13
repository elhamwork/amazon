"""Attaches Selenium to a Chrome window you already launched with
--remote-debugging-port, so Keepa/Jungle Scout/Amazon sessions you're
already logged into are reused as-is — no separate bot login, no
headless fingerprint to hide."""

import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import config


def get_driver() -> webdriver.Chrome:
    options = Options()
    options.debugger_address = config.CHROME_DEBUG_ADDRESS
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def random_delay(min_seconds: float = None, max_seconds: float = None) -> None:
    lo = min_seconds if min_seconds is not None else config.MIN_DELAY_SECONDS
    hi = max_seconds if max_seconds is not None else config.MAX_DELAY_SECONDS
    time.sleep(random.uniform(lo, hi))


def human_scroll(driver: webdriver.Chrome) -> None:
    steps = random.randint(*config.SCROLL_STEPS)
    for _ in range(steps):
        pixels = random.randint(300, 900)
        driver.execute_script(f"window.scrollBy(0, {pixels});")
        time.sleep(random.uniform(*config.SCROLL_PAUSE_SECONDS))


def new_tab(driver: webdriver.Chrome, url: str) -> str:
    """Opens url in a new tab, switches to it, returns the tab handle."""
    driver.switch_to.new_window("tab")
    driver.get(url)
    return driver.current_window_handle


def close_tab(driver: webdriver.Chrome, handle: str, return_to: str) -> None:
    driver.switch_to.window(handle)
    driver.close()
    driver.switch_to.window(return_to)
