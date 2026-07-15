"""Attaches Selenium to a Chrome window you already launched with
--remote-debugging-port, so Keepa/Amazon/extension sessions you're
already logged into are reused as-is — no separate bot login, no
headless fingerprint to hide."""

import random
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
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


def wait_for_element(driver: webdriver.Chrome, css_selector: str, timeout: float = 8):
    """Generic wait for a CSS selector to appear -- use this instead of an
    immediate find_element() right after driver.get(), since slow-loading
    pages (AliExpress especially) often aren't fully rendered yet when the
    next line of code runs."""
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
    except TimeoutException:
        return None


def wait_for_extension_panel(driver: webdriver.Chrome, css_selector: str, timeout: float = None):
    """Chrome extensions (Seller Amp, Helium 10) inject their overlay
    asynchronously after page load, so a plain find_element right away
    often races the injection. Returns the element, or None if it never
    shows up within the timeout -- callers should treat None as "extension
    not installed/logged in/selector stale" rather than crash."""
    timeout = timeout if timeout is not None else config.EXTENSION_INJECT_TIMEOUT
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
    except TimeoutException:
        return None


def new_tab(driver: webdriver.Chrome, url: str) -> str:
    """Opens url in a new tab, switches to it, returns the tab handle."""
    driver.switch_to.new_window("tab")
    driver.get(url)
    return driver.current_window_handle


def close_tab(driver: webdriver.Chrome, handle: str, return_to: str) -> None:
    driver.switch_to.window(handle)
    driver.close()
    driver.switch_to.window(return_to)
