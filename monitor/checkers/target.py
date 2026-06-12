"""Target availability via the RedSky aggregations API (read-only JSON).

This is the reliable one. RedSky is the same backend target.com's own product
pages call for fulfillment info. We read shipping availability and (if a store is
resolved for the zip) in-store availability.

NOTE: RedSky requires a `key` query param — a public web key target.com ships in
its own frontend. These rotate occasionally. If Target checks start returning
UNKNOWN with a 401/403, grab the current key: open a Target product page, open
DevTools -> Network, filter "redsky", and copy the `key=` value into REDSKY_KEY.
"""
from __future__ import annotations

from .base import Checker, Result, Stock

REDSKY_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96"  # public web key; rotates — see module docstring
FULFILLMENT_URL = (
    "https://redsky.target.com/redsky_aggregations/v1/web/pdp_fulfillment_v1"
)


class TargetChecker(Checker):
    retailer = "target"
    auto_open = True

    async def check(self, client, watch: dict) -> Result:
        tcin = str(watch["tcin"])
        zip_code = str(watch.get("_zip", ""))
        product_url = f"https://www.target.com/p/-/A-{tcin}"

        params = {
            "key": REDSKY_KEY,
            "tcin": tcin,
            "is_bot": "false",
            "zip": zip_code,
            "state": "",
            "pricing_store_id": "",
            "has_pricing_store_id": "false",
        }
        try:
            resp = await client.get(FULFILLMENT_URL, params=params, timeout=10)
        except Exception as exc:  # network error -> UNKNOWN, never a false drop
            return Result(Stock.UNKNOWN, product_url, f"request error: {exc}")

        if resp.status_code != 200:
            return Result(Stock.UNKNOWN, product_url, f"HTTP {resp.status_code}")

        try:
            fulfillment = resp.json()["data"]["product"]["fulfillment"]
        except (KeyError, ValueError) as exc:
            return Result(Stock.UNKNOWN, product_url, f"unexpected payload: {exc}")

        shipping = fulfillment.get("shipping_options", {})
        ship_status = shipping.get("availability_status", "")
        store_options = fulfillment.get("store_options", [])
        store_in_stock = any(
            so.get("order_pickup", {}).get("availability_status") == "IN_STOCK"
            or so.get("in_store_only", {}).get("availability_status") == "IN_STOCK"
            for so in store_options
        )

        if ship_status == "IN_STOCK" or store_in_stock:
            where = "ship" if ship_status == "IN_STOCK" else "store"
            return Result(Stock.IN, product_url, f"in stock ({where})")
        return Result(Stock.OUT, product_url, f"ship={ship_status or 'n/a'}")
