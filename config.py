"""Central config: thresholds, timing, and the one place to fix selectors
when a site's DOM changes (Amazon/Keepa/Jungle Scout update their markup
often — expect to edit the SELECTORS dicts below over time)."""

CHROME_DEBUG_PORT = 9222
CHROME_DEBUG_ADDRESS = f"127.0.0.1:{CHROME_DEBUG_PORT}"

# --- Timing / human-like behavior ---
MIN_DELAY_SECONDS = 2.0
MAX_DELAY_SECONDS = 5.0
SCROLL_STEPS = (3, 6)          # random number of scroll increments per page
SCROLL_PAUSE_SECONDS = (0.3, 0.9)

# --- FBA fee model (rough standard-size, sub-1lb tier) ---
REFERRAL_FEE_RATE = 0.15
FULFILLMENT_FEE_FLAT = 3.22

# --- Scoring thresholds ---
GO_MIN_MARGIN_PCT = 30
WATCH_MIN_MARGIN_PCT = 15
GO_MAX_BSR = 50_000
WATCH_MAX_BSR = 150_000

OUTPUT_XLSX = "fba_research_output.xlsx"

# --- CSS/XPath selectors, grouped per site. These are best-effort as of
# this build and WILL need updates as these sites change their frontends.
SELECTORS = {
    "aliexpress": {
        "title": "h1",
        "price": "[class*='price--current']",
        "shipping": "[class*='dynamic-shipping']",
        "moq": "[class*='quantity']",
    },
    "amazon": {
        "search_result_link": "div[data-component-type='s-search-result'] h2 a",
        "title": "#productTitle",
        "price": ".a-price .a-offscreen",
        "bsr_row": "#detailBonusBestSeller_feature_div, #productDetails_detailBullets_sections1 tr",
        "rating": "#acrPopover .a-icon-alt",
        "review_count": "#acrCustomerReviewText",
        "fba_badge": "#fulfillerInfoFeature_feature_div, #merchant-info",
    },
    "keepa": {
        "stats_table_rows": "table.tableSeparate tr, .productStatsTable tr",
        "buybox_pct": "[title*='Buy Box']",
    },
    "junglescout": {
        "result_row": "[data-testid='product-database-row'], table tbody tr",
        "monthly_sales": "[data-testid='estimated-sales']",
        "demand_score": "[data-testid='opportunity-score'], [data-testid='demand-score']",
    },
}
