"""Common interface and result type for all retailer checkers."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Stock(Enum):
    IN = "in_stock"
    OUT = "out_of_stock"
    UNKNOWN = "unknown"  # blocked, error, or couldn't parse — never treated as a drop


@dataclass
class Result:
    stock: Stock
    url: str           # the page a human should land on to buy
    detail: str = ""   # human-readable note for logs (price, store, error reason)


class Checker:
    """Subclass per retailer. `auto_open` decides whether a drop pops a browser tab."""

    retailer: str = "base"
    auto_open: bool = False

    async def check(self, client, watch: dict) -> Result:
        raise NotImplementedError
