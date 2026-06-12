"""Walmart availability by reading the product page's embedded JSON.

Walmart inlines product state in a <script id="__NEXT_DATA__"> blob. We pull
availabilityStatus out of that rather than scraping rendered HTML.

Honest caveat: Walmart sits behind Akamai bot detection. Polite, jittered polling
from a residential IP is usually fine, but expect intermittent 403s. We treat any
block as UNKNOWN (never a false drop) and the engine backs off automatically.
"""
from __future__ import annotations

import json
import re

from .base import Checker, Result, Stock

_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)


def _find_availability(node):
    """Walk the nested __NEXT_DATA__ tree for the first availabilityStatus."""
    if isinstance(node, dict):
        if "availabilityStatus" in node and isinstance(node["availabilityStatus"], str):
            return node["availabilityStatus"]
        for value in node.values():
            found = _find_availability(value)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = _find_availability(item)
            if found:
                return found
    return None


class WalmartChecker(Checker):
    retailer = "walmart"
    auto_open = True

    async def check(self, client, watch: dict) -> Result:
        url = watch["url"]
        try:
            resp = await client.get(url, timeout=12)
        except Exception as exc:
            return Result(Stock.UNKNOWN, url, f"request error: {exc}")

        if resp.status_code != 200:
            return Result(Stock.UNKNOWN, url, f"HTTP {resp.status_code} (likely bot block)")

        match = _NEXT_DATA_RE.search(resp.text)
        if not match:
            return Result(Stock.UNKNOWN, url, "no __NEXT_DATA__ (page shape changed or blocked)")

        try:
            status = _find_availability(json.loads(match.group(1)))
        except ValueError as exc:
            return Result(Stock.UNKNOWN, url, f"bad JSON: {exc}")

        if not status:
            return Result(Stock.UNKNOWN, url, "availabilityStatus not found")
        if status.upper() == "IN_STOCK":
            return Result(Stock.IN, url, "in stock")
        return Result(Stock.OUT, url, status)
