"""Target availability via the RedSky aggregations API (read-only JSON).

This is the reliable one. RedSky is the same backend target.com's own product
pages call for fulfillment info. We check BOTH shipping availability and
in-store/pickup availability at the store nearest the configured zip.

Store resolution: on first check we call RedSky's nearby-stores endpoint once to
turn the zip into a store id + name, cache it, and include it in every
fulfillment check from then on. If the lookup fails we fall back to zip-only
(shipping) checks and retry the lookup on the next poll.

NOTE: RedSky requires a `key` query param — a public web key target.com ships in
its own frontend. Target rotates these and actively kills keys that get passed
around scraper tutorials (a dead/blocked key returns HTTP 410 or 404). Use YOUR
OWN fresh key: set `redsky_key` in config.yaml. To grab it: open any Target
product page, DevTools -> Network, filter "redsky", click a request, and copy
the `key=` value from its URL. No restart needed — config reloads live.
"""
from __future__ import annotations

from .base import Checker, Result, Stock

# Fallback default; override via `redsky_key` in config.yaml with your own.
REDSKY_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96"


def set_redsky_key(key: str) -> None:
    global REDSKY_KEY
    if key:
        REDSKY_KEY = key.strip()


FULFILLMENT_URL = (
    "https://redsky.target.com/redsky_aggregations/v1/web/pdp_fulfillment_v1"
)
NEARBY_STORES_URL = (
    "https://redsky.target.com/redsky_aggregations/v1/web/nearby_stores_v1"
)
STORE_SEARCH_MILES = 25


class TargetChecker(Checker):
    retailer = "target"
    auto_open = True

    def __init__(self) -> None:
        # (store_id, store_name) for the store nearest the zip; None = not yet
        # resolved (retry next poll), empty id = lookup gave nothing usable.
        self._store: tuple[str, str] | None = None

    async def _resolve_store(self, client, zip_code: str) -> None:
        if self._store is not None or not zip_code:
            return
        params = {
            "key": REDSKY_KEY,
            "place": zip_code,
            "limit": "1",
            "within": str(STORE_SEARCH_MILES),
            "channel": "WEB",
        }
        try:
            resp = await client.get(NEARBY_STORES_URL, params=params, timeout=10)
            stores = resp.json()["data"]["nearby_stores"]["stores"]
            store = stores[0]
            self._store = (str(store["store_id"]), store.get("location_name", "local store"))
        except Exception:
            self._store = None  # retry on next poll; zip-only check still works

    async def check(self, client, watch: dict) -> Result:
        tcin = str(watch["tcin"])
        zip_code = str(watch.get("_zip", ""))
        product_url = f"https://www.target.com/p/-/A-{tcin}"

        await self._resolve_store(client, zip_code)
        store_id, store_name = self._store if self._store else ("", "")

        params = {
            "key": REDSKY_KEY,
            "tcin": tcin,
            "is_bot": "false",
            "zip": zip_code,
            "state": "",
            "store_id": store_id,
            "pricing_store_id": store_id,
            "has_pricing_store_id": "true" if store_id else "false",
        }
        try:
            resp = await client.get(FULFILLMENT_URL, params=params, timeout=10)
        except Exception as exc:  # network error -> UNKNOWN, never a false drop
            return Result(Stock.UNKNOWN, product_url, f"request error: {exc}")

        if resp.status_code in (404, 410):
            return Result(
                Stock.UNKNOWN,
                product_url,
                f"HTTP {resp.status_code} — RedSky key dead/blocked; set a fresh redsky_key in config.yaml",
            )
        if resp.status_code != 200:
            return Result(Stock.UNKNOWN, product_url, f"HTTP {resp.status_code}")

        try:
            fulfillment = resp.json()["data"]["product"]["fulfillment"]
        except (KeyError, ValueError) as exc:
            return Result(Stock.UNKNOWN, product_url, f"unexpected payload: {exc}")

        ship_in_stock = (
            fulfillment.get("shipping_options", {}).get("availability_status")
            == "IN_STOCK"
        )
        pickup_stores = []
        for so in fulfillment.get("store_options", []):
            available = (
                so.get("order_pickup", {}).get("availability_status") == "IN_STOCK"
                or so.get("in_store_only", {}).get("availability_status") == "IN_STOCK"
            )
            if available:
                pickup_stores.append(so.get("location_name") or store_name or "store")

        if ship_in_stock or pickup_stores:
            where = []
            if ship_in_stock:
                where.append("ship")
            if pickup_stores:
                where.append("pickup @ " + ", ".join(pickup_stores[:3]))
            return Result(Stock.IN, product_url, "in stock: " + "; ".join(where))

        status = fulfillment.get("shipping_options", {}).get("availability_status")
        store_note = f", {store_name}: out" if store_id else ""
        return Result(Stock.OUT, product_url, f"ship={status or 'n/a'}{store_note}")
