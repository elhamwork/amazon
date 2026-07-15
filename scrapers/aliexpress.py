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


def _extract_title(driver, sel: dict) -> str | None:
    """AliExpress pages often have multiple <h1> tags, some empty/hidden,
    so the first match isn't reliable. Try every <h1> for real text, then
    fall back to the browser tab title (usually "<product name> -
    AliExpress ...") since that's present even when the DOM selector is
    stale."""
    wait_for_element(driver, sel["title"], timeout=10)
    for el in driver.find_elements(By.CSS_SELECTOR, sel["title"]):
        text = el.text.strip()
        if text:
            return text

    tab_title = driver.title.strip()
    if tab_title:
        for suffix in (" - AliExpress", " | AliExpress"):
            if suffix in tab_title:
                return tab_title.split(suffix)[0].strip()
        return tab_title

    return None


def scrape_aliexpress(driver, url: str) -> dict:
    """Scrapes a single AliExpress product page. Returns dict with
    raw fields; any field that can't be found comes back as None so
    downstream code (and the spreadsheet) can flag it rather than crash.
    Always includes _debug_page_title/_debug_current_url so callers can
    show what actually loaded when scraping comes up empty."""
    driver.get(url)

    sel = config.SELECTORS["aliexpress"]
    data = {
        "source_url": url,
        "title": None,
        "aliexpress_price": None,
        "shipping_cost": None,
        "moq": None,
        "_debug_page_title": driver.title,
        "_debug_current_url": driver.current_url,
    }

    data["title"] = _extract_title(driver, sel)
    data["_debug_page_title"] = driver.title
    data["_debug_current_url"] = driver.current_url

    if data["title"] is None:
        return data

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
