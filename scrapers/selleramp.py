import re

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import config
from browser import wait_for_extension_panel


def _parse_pct(text: str) -> float | None:
    if not text:
        return None
    match = re.search(r"-?[\d,]+\.?\d*", text.replace(",", ""))
    return float(match.group()) if match else None


def scrape_selleramp(driver) -> dict:
    """Reads Seller Amp's (SAS) extension overlay on the CURRENT page --
    call this right after amazon.search_amazon(), while the driver is
    still sitting on the Amazon product page it just opened. Requires the
    Seller Amp extension installed and logged in inside the debug Chrome
    profile (see README) -- a fresh profile has no extensions by default.

    Selectors here are unverified placeholders (see config.py) since I
    don't have a live Seller Amp session to confirm the real DOM against."""
    data = {
        "selleramp_margin_pct": None,
        "selleramp_roi_pct": None,
        "selleramp_monthly_sales_est": None,
    }

    sel = config.SELECTORS["selleramp"]
    panel = wait_for_extension_panel(driver, sel["panel"])
    if panel is None:
        return data

    try:
        data["selleramp_margin_pct"] = _parse_pct(
            panel.find_element(By.CSS_SELECTOR, sel["margin_pct"]).text
        )
    except NoSuchElementException:
        pass

    try:
        data["selleramp_roi_pct"] = _parse_pct(
            panel.find_element(By.CSS_SELECTOR, sel["roi_pct"]).text
        )
    except NoSuchElementException:
        pass

    try:
        sales_text = panel.find_element(By.CSS_SELECTOR, sel["monthly_sales_est"]).text
        match = re.search(r"[\d,]+", sales_text)
        data["selleramp_monthly_sales_est"] = int(match.group().replace(",", "")) if match else None
    except NoSuchElementException:
        pass

    return data
