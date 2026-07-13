import re

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import config
from browser import wait_for_extension_panel


def _parse_num(text: str) -> float | None:
    if not text:
        return None
    match = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
    return float(match.group()) if match else None


def scrape_helium10(driver) -> dict:
    """Reads Helium 10's (Xray) extension overlay on the CURRENT page --
    call this right after amazon.search_amazon(), same as Seller Amp,
    while still sitting on the Amazon product page. Requires the Helium 10
    extension installed and logged in inside the debug Chrome profile.

    Selectors here are unverified placeholders (see config.py) since I
    don't have a live Helium 10 session to confirm the real DOM against."""
    data = {
        "helium10_monthly_sales_est": None,
        "helium10_monthly_revenue_est": None,
        "helium10_review_velocity": None,
    }

    sel = config.SELECTORS["helium10"]
    panel = wait_for_extension_panel(driver, sel["panel"])
    if panel is None:
        return data

    try:
        sales_text = panel.find_element(By.CSS_SELECTOR, sel["monthly_sales_est"]).text
        data["helium10_monthly_sales_est"] = _parse_num(sales_text)
    except NoSuchElementException:
        pass

    try:
        revenue_text = panel.find_element(By.CSS_SELECTOR, sel["monthly_revenue_est"]).text
        data["helium10_monthly_revenue_est"] = _parse_num(revenue_text)
    except NoSuchElementException:
        pass

    try:
        velocity_text = panel.find_element(By.CSS_SELECTOR, sel["review_velocity"]).text
        data["helium10_review_velocity"] = _parse_num(velocity_text)
    except NoSuchElementException:
        pass

    return data
