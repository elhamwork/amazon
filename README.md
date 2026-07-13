# Amazon FBA Product Research Pipeline

Scrapes AliExpress -> Amazon -> Keepa -> Jungle Scout for each product and
outputs a color-coded GO / WATCH / SKIP spreadsheet.

## Before you read anything else: selector fragility & ToS

- Amazon, Keepa, and Jungle Scout all change their frontend markup regularly.
  Every CSS selector this project uses lives in one place, `config.py` ->
  `SELECTORS`, specifically so you can fix things fast when a site update
  breaks a scraper (a field silently coming back blank in the output is
  almost always a stale selector — open devtools on that page and check).
- **Amazon's ToS prohibits automated scraping.** This is a common practice
  among sellers doing personal research, but it carries IP-block risk.
- **Keepa sells an official API (~$20/mo)** specifically so people don't
  scrape their site. This project scrapes Keepa's DOM instead per your
  choice — know that this is against Keepa's ToS, more fragile than their
  API (their real data is behind a canvas chart this can't read; it's
  reading the summary stats table instead), and puts your Keepa account's
  standing at some risk. Swapping in the real API later is a clean
  contained change (just rewrite `scrapers/keepa.py`).
- **Jungle Scout** — same category of risk, using your paid logged-in
  session instead of an official integration.
- If you resell this tool to clients, make clear to them that ToS
  compliance/account risk is theirs to accept, not something this code
  guarantees around.

## Setup

```
pip install -r requirements.txt
```

## 1. Launch Chrome in debug mode

Run `launch_chrome_debug.bat` (double-click it, or run from a terminal).
This opens a **separate** Chrome window/profile with remote debugging on
port 9222. The first time, log into Amazon, Keepa, and Jungle Scout in
*this* window — the profile persists, so you only do this once.

Leave this Chrome window open while the script runs.

## 2. Run the pipeline

Paste URLs interactively (default, no flags):

```
python main.py
```

Then paste AliExpress URLs one per line, blank line to finish.

From a CSV (one AliExpress URL per row, first column):

```
python main.py --csv products.csv
```

By keyword only (no AliExpress step, useful for checking an idea before
you've found a supplier):

```
python main.py --keywords "silicone phone case,magnetic charging cable"
```

Custom output path:

```
python main.py --csv products.csv --output my_batch.xlsx
```

## Output

`fba_research_output.xlsx` (or your `--output` path) with one row per
product: title, AliExpress price, Amazon price, estimated FBA fee, net
profit, margin %, BSR, review count, rating, seller count, FBA badge,
Jungle Scout monthly sales estimate, Keepa price/BSR trend, and a
GO/WATCH/SKIP score, with rows colored green/yellow/red to match.

## Scoring logic (edit in `config.py` / `calculator.py`)

- **GO**: margin > 30% AND BSR < 50,000
- **WATCH**: margin 15–30% OR BSR 50,000–150,000
- **SKIP**: everything else, and anything where Amazon price couldn't be
  found at all (treat these as "needs manual check", not "bad product")

FBA fee estimate is a rough model (15% referral + $3.22 flat fulfillment,
sub-1lb standard tier) — swap in the real fee for your product's actual
size tier for anything you're seriously considering.

## Known limitations

- Amazon matching is by title search, taking the top organic result —
  it's a "closest comparable listing," not a guaranteed exact match.
  Spot-check anything before acting on it.
- Selector-based scraping breaks when these sites update their UI. If a
  column comes back empty across the board, check `config.py` selectors
  first.
- Captchas: AliExpress and Amazon may occasionally show one. The script
  doesn't solve captchas automatically — if a run stalls, check the
  Chrome window.
