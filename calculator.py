import config


def estimate_fba_fee(amazon_price: float) -> float:
    referral_fee = amazon_price * config.REFERRAL_FEE_RATE
    return round(referral_fee + config.FULFILLMENT_FEE_FLAT, 2)


def compute_metrics(row: dict) -> dict:
    """Fills in fba_fee, net_profit, margin_pct, and score on `row` in place
    (mutates and returns). Any missing required input leaves the
    money fields as None and scores the product SKIP so it's visibly
    flagged as needing manual review rather than silently dropped."""
    amazon_price = row.get("amazon_price")
    aliexpress_price = row.get("aliexpress_price") or 0
    shipping_cost = row.get("shipping_cost") or 0
    bsr = row.get("bsr")

    if not amazon_price:
        row["fba_fee"] = None
        row["net_profit"] = None
        row["margin_pct"] = None
        row["score"] = "SKIP"
        return row

    fba_fee = estimate_fba_fee(amazon_price)
    landed_cost = aliexpress_price + shipping_cost
    net_profit = round(amazon_price - landed_cost - fba_fee, 2)
    margin_pct = round((net_profit / amazon_price) * 100, 1) if amazon_price else None

    row["fba_fee"] = fba_fee
    row["net_profit"] = net_profit
    row["margin_pct"] = margin_pct
    row["score"] = _score(margin_pct, bsr)
    return row


def _score(margin_pct: float | None, bsr: int | None) -> str:
    if margin_pct is None:
        return "SKIP"

    is_go_margin = margin_pct > config.GO_MIN_MARGIN_PCT
    is_go_bsr = bsr is not None and bsr < config.GO_MAX_BSR
    if is_go_margin and is_go_bsr:
        return "GO"

    is_watch_margin = config.WATCH_MIN_MARGIN_PCT <= margin_pct <= config.GO_MIN_MARGIN_PCT
    is_watch_bsr = bsr is not None and config.GO_MAX_BSR <= bsr <= config.WATCH_MAX_BSR
    if is_watch_margin or is_watch_bsr:
        return "WATCH"

    return "SKIP"
