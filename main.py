"""FBA product research pipeline: AliExpress -> Amazon (+ Seller Amp /
Helium 10 extension overlays) -> Keepa -> DataDive -> scored Excel output.

Requires Chrome already running with remote debugging enabled (see
README.md / launch_chrome_debug.bat) so the script reuses your logged-in
Amazon/Keepa/DataDive sessions and your Seller Amp / Helium 10 extensions.
"""

import argparse
import csv
import sys

import calculator
import config
from browser import get_driver, random_delay
from excel_writer import write_excel
from scrapers.aliexpress import scrape_aliexpress
from scrapers.amazon import search_amazon
from scrapers.datadive import scrape_datadive
from scrapers.helium10 import scrape_helium10
from scrapers.keepa import scrape_keepa
from scrapers.selleramp import scrape_selleramp


def _shorten_query(title: str, max_words: int = 6) -> str:
    """AliExpress titles are often SEO keyword-stuffed run-ons ("Customized
    Durable Reliable Lawn Mower High Efficiency Powerful Engine..."), which
    make terrible Amazon search queries. Take just the first few words as
    a rough approximation of the actual product name."""
    words = title.split()
    return " ".join(words[:max_words])


def process_product(driver, *, aliexpress_url: str = None, keyword: str = None, free_only: bool = False) -> dict:
    row = {}

    if aliexpress_url:
        print(f"  -> AliExpress: {aliexpress_url}")
        row.update(scrape_aliexpress(driver, aliexpress_url))
        search_query = row.get("title") or keyword
    else:
        row["source_url"] = None
        row["title"] = keyword
        search_query = keyword

    if not search_query:
        if row.get("_debug_page_title") is not None:
            print(f"  !! AliExpress title extraction failed. "
                  f"Browser tab title: {row['_debug_page_title']!r}, "
                  f"URL: {row['_debug_current_url']}")
            print("  !! This usually means a captcha, shipping-country "
                  "picker, or bot-check appeared instead of the product page.")
        print("  !! No title/keyword available, skipping Amazon lookup")
        return calculator.compute_metrics(row)

    amazon_query = _shorten_query(search_query)
    print(f"  -> Amazon search: {amazon_query}")
    random_delay()
    row.update(search_amazon(driver, amazon_query))
    if not row.get("amazon_url"):
        print(f"  !! Amazon search returned no result. "
              f"Browser tab title: {row.get('_debug_page_title')!r}, "
              f"URL: {row.get('_debug_current_url')}")
        print("  !! This usually means a captcha/bot-check page instead of "
              "real search results, or Amazon showed a 'no results' page.")
    else:
        print(f"     matched: {row.get('amazon_title')!r}")
        print(f"     price={row.get('amazon_price')}  bsr={row.get('bsr')}  "
              f"rating={row.get('rating')}  reviews={row.get('review_count')}")

    if free_only:
        if not row.get("amazon_title"):
            row["amazon_title"] = row.get("title") or search_query
        return calculator.compute_metrics(row)

    # Seller Amp / Helium 10 are read as extension overlays on the Amazon
    # product page we're already sitting on -- no navigation, just a wait
    # for the extension to inject its panel.
    print("  -> Seller Amp overlay")
    row.update(scrape_selleramp(driver))

    print("  -> Helium 10 overlay")
    row.update(scrape_helium10(driver))

    print("  -> Keepa lookup")
    random_delay()
    row.update(scrape_keepa(driver, row.get("amazon_url")))

    print("  -> DataDive lookup")
    random_delay()
    row.update(scrape_datadive(driver, search_query))

    if not row.get("amazon_title"):
        row["amazon_title"] = row.get("title") or search_query

    return calculator.compute_metrics(row)


def collect_paste_urls() -> list[str]:
    print("Paste AliExpress URLs one per line. Blank line to finish.")
    urls = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        urls.append(line)
    return urls


def collect_csv_urls(path: str) -> list[str]:
    urls = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip():
                urls.append(row[0].strip())
    return urls


def main():
    parser = argparse.ArgumentParser(description="Amazon FBA product research pipeline")
    parser.add_argument("--csv", help="Path to a CSV of AliExpress URLs (one per row, first column)")
    parser.add_argument("--keywords", help="Comma-separated product keywords (no AliExpress URL)")
    parser.add_argument("--output", default=config.OUTPUT_XLSX, help="Output .xlsx path")
    parser.add_argument(
        "--free-only",
        action="store_true",
        help="Only scrape AliExpress + Amazon; skip Keepa/Seller Amp/Helium 10/DataDive (no accounts needed)",
    )
    args = parser.parse_args()

    jobs = []  # list of (aliexpress_url, keyword)

    if args.csv:
        for url in collect_csv_urls(args.csv):
            jobs.append((url, None))
    if args.keywords:
        for kw in args.keywords.split(","):
            kw = kw.strip()
            if kw:
                jobs.append((None, kw))

    if not args.csv and not args.keywords:
        for url in collect_paste_urls():
            jobs.append((url, None))

    if not jobs:
        print("No input provided. Use --csv, --keywords, or paste URLs interactively.")
        sys.exit(1)

    print(f"\nConnecting to Chrome on {config.CHROME_DEBUG_ADDRESS} ...")
    try:
        driver = get_driver()
    except Exception as exc:
        print(f"Could not attach to Chrome: {exc}")
        print("Make sure Chrome is running with --remote-debugging-port="
              f"{config.CHROME_DEBUG_PORT} (see README.md).")
        sys.exit(1)

    original_tab = driver.current_window_handle
    rows = []
    for i, (url, keyword) in enumerate(jobs, start=1):
        print(f"\n[{i}/{len(jobs)}] Processing...")
        try:
            row = process_product(driver, aliexpress_url=url, keyword=keyword, free_only=args.free_only)
        except Exception as exc:
            print(f"  !! Error processing this product: {exc}")
            row = {"source_url": url, "title": keyword, "score": "SKIP"}
        rows.append(row)

    output_path = write_excel(rows, args.output)
    print(f"\nDone. {len(rows)} product(s) written to {output_path}")


if __name__ == "__main__":
    main()
