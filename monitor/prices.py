"""Daily TCGplayer market-price snapshots for sealed product, via tcgcsv.com.

tcgcsv.com republishes TCGplayer's catalog and prices once a day (~20:00 UTC) as
plain JSON — no API key, which matters because TCGplayer's own API is closed to
new developers. Pokemon is category 3:

    https://tcgcsv.com/tcgplayer/3/groups               -> sets ("groups")
    https://tcgcsv.com/tcgplayer/3/{groupId}/products   -> products incl. sealed
    https://tcgcsv.com/tcgplayer/3/{groupId}/prices     -> marketPrice by productId

Config (config.yaml):

    tcg_prices:
      - set: "Prismatic Evolutions"      # substring match against group names
        match: ["Elite Trainer Box"]     # substring match against product names

Each snapshot appends rows to prices.csv. Over weeks this gives you the market
trend for exactly the sealed items you're buying — your own data on whether the
hype is rising or dying, which is the number that decides hold vs. flip.

Also runnable on demand:  python -m monitor.prices
"""
from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path

BASE = "https://tcgcsv.com/tcgplayer/3"
PRICES_CSV = Path("prices.csv")


def _results(payload) -> list:
    # tcgcsv mirrors TCGplayer's envelope: {"success":..., "results":[...]}
    if isinstance(payload, dict):
        return payload.get("results", []) or []
    return payload or []


async def _get_json(client, url: str):
    resp = await client.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


async def snapshot(client, price_watches: list[dict]) -> int:
    """Fetch current market prices for all configured watches; returns rows written."""
    if not price_watches:
        return 0

    groups = _results(await _get_json(client, f"{BASE}/groups"))
    rows: list[list] = []
    today = date.today().isoformat()

    for pw in price_watches:
        set_needle = str(pw.get("set", "")).lower()
        needles = [str(m).lower() for m in pw.get("match", [])]
        if not set_needle or not needles:
            continue

        matched_groups = [g for g in groups if set_needle in str(g.get("name", "")).lower()]
        for group in matched_groups:
            gid = group["groupId"]
            products = _results(await _get_json(client, f"{BASE}/{gid}/products"))
            prices = _results(await _get_json(client, f"{BASE}/{gid}/prices"))
            market = {p["productId"]: p for p in prices}

            for prod in products:
                name = str(prod.get("name", ""))
                if not any(n in name.lower() for n in needles):
                    continue
                price = market.get(prod["productId"], {})
                rows.append([
                    today,
                    group.get("name", ""),
                    name,
                    prod["productId"],
                    price.get("marketPrice", ""),
                    price.get("lowPrice", ""),
                ])

    if rows:
        new_file = not PRICES_CSV.exists()
        with PRICES_CSV.open("a", newline="") as fh:
            writer = csv.writer(fh)
            if new_file:
                writer.writerow(["date", "set", "product", "product_id", "market_price", "low_price"])
            writer.writerows(rows)
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"{ts}  [prices       ] snapshot: {len(rows)} sealed price(s) -> {PRICES_CSV}")
    return len(rows)


if __name__ == "__main__":
    import asyncio
    import sys

    import httpx

    from .config import load

    async def _main() -> None:
        config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("config.yaml")
        _, settings = load(config_path)
        async with httpx.AsyncClient(follow_redirects=True) as client:
            n = await snapshot(client, settings["tcg_prices"])
        if n == 0:
            print("No prices written — check the tcg_prices section of config.yaml.")

    asyncio.run(_main())
