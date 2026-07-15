import re

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import config
from browser import human_scroll, random_delay, wait_for_element


def _clean_price(text: str) -> float | None:
    if not text:
        return None
    match = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
    return float(match.group()) if match else None


def scrape_aliexpress(driver, url: str) -> dict:
    """Scrapes a single AliExpress product page. Returns dict with
    raw fields; any field that can't be found comes back as None so
    downstream code (and the spreadsheet) can flag it rather than crash."""
    driver.get(url)

    sel = config.SELECTORS["aliexpress"]
    data = {
        "source_url": url,
        "title": None,
        "aliexpress_price": None,
        "shipping_cost": None,
        "moq": None,
    }

    title_el = wait_for_element(driver, sel["title"], timeout=10)
    if title_el is None:
        # Page didn't render an h1 in time -- likely a captcha, country
        # picker, or bot-detection interstitial instead of the real
        # product page. Surface what actually loaded so it's debuggable
        # without switching to the browser window.
        data["_debug_page_title"] = driver.title
        data["_debug_current_url"] = driver.current_url
        return data
    data["title"] = title_el.text.strip()

    random_delay()
    human_scroll(driver)

    try:
        price_text = driver.find_element(By.CSS_SELECTOR, sel["price"]).text
        data["aliexpress_price"] = _clean_price(price_text)
    except NoSuchElementException:
        pass

    try:
        shipping_text = driver.find_element(By.CSS_SELECTOR, sel["shipping"]).text
        data["shipping_cost"] = _clean_price(shipping_text)
    except NoSuchElementException:
        data["shipping_cost"] = 0.0

    try:
        moq_text = driver.find_element(By.CSS_SELECTOR, sel["moq"]).text
        match = re.search(r"\d+", moq_text)
        data["moq"] = int(match.group()) if match else 1
    except NoSuchElementException:
        data["moq"] = 1

    return data
