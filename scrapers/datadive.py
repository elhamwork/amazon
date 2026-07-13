import re
import urllib.parse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import config
from browser import human_scroll, random_delay


def _parse_num(text: str) -> float | None:
    if not text:
        return None
    match = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
    return float(match.group()) if match else None


def scrape_datadive(driver, keyword: str) -> dict:
    """Searches DataDive for `keyword` and reads the top keyword row's
    search volume and PPC bid. Requires you to already be logged into
    DataDive in the attached Chrome session.

    config.DATADIVE_BASE_URL and the selectors in config.SELECTORS['datadive']
    are placeholders -- confirm DataDive's real search URL and DOM structure
    once you have an account open, then update config.py."""
    data = {
        "datadive_top_keyword": None,
        "datadive_search_volume": None,
        "datadive_ppc_bid": None,
    }

    search_url = f"{config.DATADIVE_BASE_URL}/search?q={urllib.parse.quote(keyword)}"
    driver.get(search_url)
    random_delay()
    human_scroll(driver)

    sel = config.SELECTORS["datadive"]
    try:
        row = driver.find_element(By.CSS_SELECTOR, sel["keyword_row"])
    except NoSuchElementException:
        return data

    cells = [c.text.strip() for c in row.find_elements(By.TAG_NAME, "td")]
    if cells:
        data["datadive_top_keyword"] = cells[0]

    try:
        volume_text = row.find_element(By.CSS_SELECTOR, sel["search_volume"]).text
        data["datadive_search_volume"] = _parse_num(volume_text)
    except NoSuchElementException:
        pass

    try:
        bid_text = row.find_element(By.CSS_SELECTOR, sel["ppc_bid"]).text
        data["datadive_ppc_bid"] = _parse_num(bid_text)
    except NoSuchElementException:
        pass

    return data
