"""Pokemon Center — NOTIFY ONLY by design.

Pokemon Center is heavily anti-bot, so we keep this deliberately light: a gentle
poll of the product page, no auto-open, no aggressive retries. On a drop you get a
toast + the link and you take it from there manually.

We look for common out-of-stock signals in the page text. Pokemon Center changes
its frontend periodically; if these markers stop matching you'll see UNKNOWN in the
logs and we re-tune the signal then. UNKNOWN is never treated as a drop.
"""
from __future__ import annotations

from .base import Checker, Result, Stock

OOS_MARKERS = (
    "sold out",
    "out of stock",
    "currently unavailable",
    "notify me when available",
)
IN_MARKERS = (
    "add to cart",
    "add to bag",
)


class PokemonCenterChecker(Checker):
    retailer = "pokemoncenter"
    auto_open = False  # notify-only, on purpose

    async def check(self, client, watch: dict) -> Result:
        url = watch["url"]
        try:
            resp = await client.get(url, timeout=12)
        except Exception as exc:
            return Result(Stock.UNKNOWN, url, f"request error: {exc}")

        if resp.status_code != 200:
            return Result(Stock.UNKNOWN, url, f"HTTP {resp.status_code} (likely bot block)")

        text = resp.text.lower()
        if any(marker in text for marker in OOS_MARKERS):
            return Result(Stock.OUT, url, "sold out marker present")
        if any(marker in text for marker in IN_MARKERS):
            return Result(Stock.IN, url, "add-to-cart present")
        return Result(Stock.UNKNOWN, url, "no clear stock marker")
