"""Central config: thresholds, timing, and the one place to fix selectors
when a site's DOM changes (Amazon/Keepa/Seller Amp/Helium 10/DataDive
update their markup often — expect to edit the SELECTORS dicts below
over time)."""

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

# How long (seconds) to wait for a Chrome extension (Seller Amp, Helium 10)
# to inject its overlay into the Amazon page before giving up on that field.
EXTENSION_INJECT_TIMEOUT = 6

# TODO: set this to your actual DataDive app URL once you confirm it --
# this is a placeholder and DataDive's real login/search URL may differ.
DATADIVE_BASE_URL = "https://members.datadive.tools"

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
    # Seller Amp (SAS) is normally used as a Chrome extension that injects a
    # data panel onto the Amazon product page. These selectors are UNVERIFIED
    # placeholders -- install the extension in the debug Chrome profile,
    # open devtools on a real Amazon product page, and update these to match
    # the real injected panel's class/id names.
    "selleramp": {
        "panel": "#selleramp-widget, .sas-overlay-panel, [id*='selleramp']",
        "margin_pct": "[class*='sas-margin'], [class*='profit-margin']",
        "roi_pct": "[class*='sas-roi'], [class*='roi-value']",
        "monthly_sales_est": "[class*='sas-sales-est'], [class*='sas-monthly-sales']",
    },
    # Helium 10 (Xray) also runs as a Chrome extension, overlaying a widget
    # on Amazon product/search pages. Same caveat as Seller Amp above --
    # verify against the real DOM after installing/logging into the
    # extension in the debug Chrome profile.
    "helium10": {
        "panel": "#h10-xray-widget, [id*='helium10'], [class*='xray-panel']",
        "monthly_sales_est": "[class*='h10-sales-est'], [class*='xray-sales']",
        "monthly_revenue_est": "[class*='h10-revenue'], [class*='xray-revenue']",
        "review_velocity": "[class*='h10-review-velocity']",
    },
    # DataDive is a separate web app (keyword/PPC research). URL + selectors
    # are placeholders -- confirm the real search URL and DOM once you have
    # a DataDive account open in the debug Chrome profile.
    "datadive": {
        "keyword_row": "table tbody tr, [data-testid='keyword-row']",
        "search_volume": "[data-testid='search-volume'], [class*='search-volume']",
        "ppc_bid": "[data-testid='ppc-bid'], [class*='ppc-bid'], [class*='suggested-bid']",
    },
}
