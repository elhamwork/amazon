"""FBA product research pipeline: AliExpress -> Amazon -> Keepa -> Jungle
Scout -> scored Excel output.

Requires Chrome already running with remote debugging enabled (see
README.md / launch_chrome_debug.bat) so the script reuses your logged-in
Keepa and Jungle Scout sessions.
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
from scrapers.junglescout import scrape_junglescout
from scrapers.keepa import scrape_keepa


def process_product(driver, *, aliexpress_url: str = None, keyword: str = None) -> dict:
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
        print("  !! No title/keyword available, skipping Amazon/Keepa/Jungle Scout lookups")
        return calculator.compute_metrics(row)

    print(f"  -> Amazon search: {search_query}")
    random_delay()
    row.update(search_amazon(driver, search_query))

    print("  -> Keepa lookup")
    random_delay()
    row.update(scrape_keepa(driver, row.get("amazon_url")))

    print("  -> Jungle Scout lookup")
    random_delay()
    row.update(scrape_junglescout(driver, search_query))

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
            row = process_product(driver, aliexpress_url=url, keyword=keyword)
        except Exception as exc:
            print(f"  !! Error processing this product: {exc}")
            row = {"source_url": url, "title": keyword, "score": "SKIP"}
        rows.append(row)

    output_path = write_excel(rows, args.output)
    print(f"\nDone. {len(rows)} product(s) written to {output_path}")


if __name__ == "__main__":
    main()
