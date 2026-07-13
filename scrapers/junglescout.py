import re
import urllib.parse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import config
from browser import human_scroll, random_delay


def _parse_int(text: str) -> int | None:
    if not text:
        return None
    match = re.search(r"[\d,]+", text)
    return int(match.group().replace(",", "")) if match else None


def scrape_junglescout(driver, keyword: str) -> dict:
    """Searches Jungle Scout's web app Product/Supplier Database for the
    given keyword and reads the top result row. Requires you to already be
    logged into Jungle Scout in the attached Chrome session.

    Jungle Scout's app is a heavy SPA and its data-testid attributes change
    across releases -- if this returns all None, open devtools on a real
    search result and update config.SELECTORS['junglescout']."""
    data = {
        "js_monthly_sales_est": None,
        "js_demand_score": None,
    }

    search_url = f"https://www.junglescout.com/database/?search={urllib.parse.quote(keyword)}"
    driver.get(search_url)
    random_delay()
    human_scroll(driver)

    sel = config.SELECTORS["junglescout"]
    try:
        row = driver.find_element(By.CSS_SELECTOR, sel["result_row"])
    except NoSuchElementException:
        return data

    try:
        sales_text = row.find_element(By.CSS_SELECTOR, sel["monthly_sales"]).text
        data["js_monthly_sales_est"] = _parse_int(sales_text)
    except NoSuchElementException:
        pass

    try:
        score_text = row.find_element(By.CSS_SELECTOR, sel["demand_score"]).text
        data["js_demand_score"] = _parse_int(score_text)
    except NoSuchElementException:
        pass

    return data
