import re
import urllib.parse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import config
from browser import human_scroll, random_delay, wait_for_element


def _clean_price(text: str) -> float | None:
    if not text:
        return None
    match = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
    return float(match.group()) if match else None


def _find_bsr(driver) -> int | None:
    sel = config.SELECTORS["amazon"]
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, sel["bsr_row"])
        for row in rows:
            text = row.text
            if "Best Sellers Rank" in text or "Best Seller" in text:
                match = re.search(r"#([\d,]+)", text)
                if match:
                    return int(match.group(1).replace(",", ""))
    except NoSuchElementException:
        pass
    return None


def search_amazon(driver, query: str) -> dict:
    """Searches Amazon for `query` (an AliExpress product title, usually),
    opens the top organic result, and scrapes it. Amazon has no reliable
    way to match "the same product" from a title alone -- this takes the
    first non-sponsored result as the closest comparable listing. Treat
    the result as a competitor/comparable, not a guaranteed exact match."""
    search_url = f"https://www.amazon.com/s?k={urllib.parse.quote(query)}"
    driver.get(search_url)

    sel = config.SELECTORS["amazon"]
    data = {
        "amazon_price": None,
        "bsr": None,
        "rating": None,
        "review_count": None,
        "seller_count": None,
        "fba_listed": None,
        "amazon_title": None,
        "amazon_url": None,
        "_debug_page_title": driver.title,
        "_debug_current_url": driver.current_url,
    }

    link = wait_for_element(driver, sel["search_result_link"], timeout=10)
    data["_debug_page_title"] = driver.title
    data["_debug_current_url"] = driver.current_url
    if link is None:
        # No search result rendered in time -- likely a captcha/bot-check
        # page, or the search selector is stale. See _debug_* fields.
        return data

    data["amazon_url"] = link.get_attribute("href")
    link.click()

    random_delay()
    human_scroll(driver)
    data["_debug_page_title"] = driver.title
    data["_debug_current_url"] = driver.current_url

    try:
        data["amazon_title"] = driver.find_element(By.CSS_SELECTOR, sel["title"]).text.strip()
    except NoSuchElementException:
        pass

    try:
        price_text = driver.find_element(By.CSS_SELECTOR, sel["price"]).text
        data["amazon_price"] = _clean_price(price_text)
    except NoSuchElementException:
        pass

    try:
        rating_text = driver.find_element(By.CSS_SELECTOR, sel["rating"]).get_attribute("textContent")
        match = re.search(r"[\d.]+", rating_text)
        data["rating"] = float(match.group()) if match else None
    except NoSuchElementException:
        pass

    try:
        review_text = driver.find_element(By.CSS_SELECTOR, sel["review_count"]).text
        match = re.search(r"[\d,]+", review_text)
        data["review_count"] = int(match.group().replace(",", "")) if match else None
    except NoSuchElementException:
        pass

    data["bsr"] = _find_bsr(driver)

    try:
        fba_text = driver.find_element(By.CSS_SELECTOR, sel["fba_badge"]).text
        data["fba_listed"] = "Fulfilled by Amazon" in fba_text or "Amazon.com" in fba_text
    except NoSuchElementException:
        data["fba_listed"] = None

    return data
