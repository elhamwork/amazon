# Amazon FBA Product Research Pipeline

Scrapes AliExpress -> Amazon -> Keepa -> Seller Amp -> Helium 10 -> DataDive
for each product and outputs a color-coded GO / WATCH / SKIP spreadsheet.

Seller Amp and Helium 10 are read as **Chrome extension overlays** on the
Amazon product page itself (not separate site navigations) since that's
how they're normally used.

## Before you read anything else: selector fragility & ToS

- All 6 sites/extensions change their frontend markup regularly. Every
  CSS selector this project uses lives in one place, `config.py` ->
  `SELECTORS`, specifically so you can fix things fast when a site update
  breaks a scraper (a field silently coming back blank in the output is
  almost always a stale selector — open devtools on that page and check).
- **Seller Amp, Helium 10, and DataDive selectors are unverified
  placeholders.** I don't have a live logged-in session to any of the
  three to confirm their real DOM against — Amazon and Keepa's selectors
  are based on well-documented, stable structure, but these three are
  best-effort guesses you'll need to correct on your first real run (see
  "First-run selector fixup" below).
- **Amazon's ToS prohibits automated scraping.** Common practice for
  personal research, but it carries IP-block risk.
- **Keepa sells an official API (~$20/mo)** specifically so people don't
  scrape their site. This project scrapes Keepa's DOM instead per your
  earlier choice — that's against Keepa's ToS, more fragile than their
  API, and puts your Keepa account's standing at some risk. Swapping in
  the real API later is a contained change (rewrite `scrapers/keepa.py`).
- **Seller Amp, Helium 10, DataDive** — same category of risk: this reads
  data out of tools you're already paying for, via your own logged-in
  session/extensions, instead of an official integration (Helium 10 does
  have some API access on higher tiers if you want a more stable path
  later).
- If you resell this tool to clients, make clear to them that ToS
  compliance/account risk is theirs to accept, not something this code
  guarantees around.

## Setup

```
pip install -r requirements.txt
```

## 1. Launch Chrome in debug mode

**Windows:** run `launch_chrome_debug.bat` (double-click it, or run from
a terminal).

**Mac:** run `./launch_chrome_debug.sh` from Terminal (run `chmod +x
launch_chrome_debug.sh` once first if it's not already executable).

Either way, this opens a **separate, brand-new** Chrome profile with
remote debugging on port 9222. Because it's a fresh profile, it starts
with **no extensions installed** — the first time, in *this* window you
need to:

1. Log into Amazon, Keepa, and DataDive.
2. Install the Seller Amp (SAS) and Helium 10 Chrome extensions from the
   Chrome Web Store and log into both.

This profile persists across runs, so you only do this setup once.

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
Keepa price/BSR trend, Seller Amp margin/ROI/sales estimate, Helium 10
sales/revenue estimate and review velocity, DataDive top keyword/search
volume/PPC bid, and a GO/WATCH/SKIP score — rows colored green/yellow/red
to match.

## Scoring logic (edit in `config.py` / `calculator.py`)

- **GO**: margin > 30% AND BSR < 50,000
- **WATCH**: margin 15–30% OR BSR 50,000–150,000
- **SKIP**: everything else, and anything where Amazon price couldn't be
  found at all (treat these as "needs manual check", not "bad product")

Note: the score only factors in margin and BSR (the two numbers every
product has). Seller Amp / Helium 10 / DataDive columns are shown for
your own read but don't currently feed the score — add them into
`calculator._score()` if you want them to.

FBA fee estimate is a rough model (15% referral + $3.22 flat fulfillment,
sub-1lb standard tier) — swap in the real fee for your product's actual
size tier for anything you're seriously considering.

## First-run selector fixup

Run the script once on a single product. Whichever of Seller Amp / Helium
10 / DataDive columns come back blank:

1. Open the relevant page/panel manually in the debug Chrome window.
2. Right-click the data point (e.g. Seller Amp's margin number) -> Inspect.
3. Note its class/id, and update the matching entry in
   `config.SELECTORS` (e.g. `SELECTORS["selleramp"]["margin_pct"]`).
4. Re-run.

DataDive additionally needs `config.DATADIVE_BASE_URL` set to the real
app URL/search path once you confirm it.

## Known limitations

- Amazon matching is by title search, taking the top organic result —
  it's a "closest comparable listing," not a guaranteed exact match.
  Spot-check anything before acting on it.
- Selector-based scraping breaks when these sites update their UI. If a
  column comes back empty across the board, check `config.py` selectors
  first.
- Seller Amp / Helium 10 overlays inject asynchronously after page load;
  the script waits up to `config.EXTENSION_INJECT_TIMEOUT` seconds (6s
  default) for the panel to appear before giving up on that product's
  fields. Slow connections may need a higher value.
- Captchas: AliExpress and Amazon may occasionally show one. The script
  doesn't solve captchas automatically — if a run stalls, check the
  Chrome window.
