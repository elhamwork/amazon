import re

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import config
from browser import human_scroll, random_delay


def _extract_asin(amazon_url: str | None) -> str | None:
    if not amazon_url:
        return None
    match = re.search(r"/dp/([A-Z0-9]{10})", amazon_url)
    return match.group(1) if match else None


def _parse_num(text: str) -> float | None:
    if not text or text.strip() in ("-", ""):
        return None
    match = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
    return float(match.group()) if match else None


def _trend(current: float | None, avg: float | None) -> str:
    if current is None or avg is None:
        return "unknown"
    if current < avg * 0.97:
        return "down"
    if current > avg * 1.03:
        return "up"
    return "stable"


def scrape_keepa(driver, amazon_url: str | None) -> dict:
    """Reads Keepa's product stats table (DOM text, not the canvas chart --
    the chart itself isn't reliably scrapable). Requires you to already be
    logged into Keepa in the attached Chrome session.

    Note: scraping Keepa's site instead of their official API is against
    their ToS and more fragile than the API -- see README for the tradeoff."""
    data = {
        "keepa_price_trend": "unknown",
        "keepa_bsr_trend": "unknown",
        "keepa_buybox_pct": None,
    }

    asin = _extract_asin(amazon_url)
    if not asin:
        return data

    driver.get(f"https://keepa.com/#!product/1-{asin}")
    random_delay()
    human_scroll(driver)

    sel = config.SELECTORS["keepa"]
    stats = {}
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, sel["stats_table_rows"])
        for row in rows:
            cells = [c.text.strip() for c in row.find_elements(By.TAG_NAME, "td")]
            if len(cells) >= 3:
                stats[cells[0]] = cells[1:]
    except NoSuchElementException:
        pass

    if "Amazon" in stats or "New" in stats:
        price_row = stats.get("Amazon") or stats.get("New")
        current = _parse_num(price_row[0]) if len(price_row) > 0 else None
        avg_30 = _parse_num(price_row[1]) if len(price_row) > 1 else None
        data["keepa_price_trend"] = _trend(current, avg_30)

    if "Sales Rank" in stats:
        bsr_row = stats["Sales Rank"]
        current = _parse_num(bsr_row[0]) if len(bsr_row) > 0 else None
        avg_30 = _parse_num(bsr_row[1]) if len(bsr_row) > 1 else None
        # lower BSR is "better", so trend direction is inverted vs price
        data["keepa_bsr_trend"] = _trend(avg_30, current) if current and avg_30 else "unknown"

    try:
        buybox_text = driver.find_element(By.CSS_SELECTOR, sel["buybox_pct"]).text
        match = re.search(r"(\d+)%", buybox_text)
        data["keepa_buybox_pct"] = int(match.group(1)) if match else None
    except NoSuchElementException:
        pass

    return data
