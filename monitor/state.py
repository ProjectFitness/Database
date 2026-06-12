"""Tracks per-watch stock state so we fire exactly once per drop.

Rules:
  - Alert only on a real OOS -> IN_STOCK transition.
  - UNKNOWN never counts as a transition (a bot-block must not look like a drop).
  - After firing, hold a cooldown so a flickering page doesn't spam you.
  - Re-arm once the item goes OUT again, ready for the next drop.
"""
from __future__ import annotations

import time

from .checkers.base import Stock


class StateTracker:
    def __init__(self, cooldown_seconds: int = 60):
        self.cooldown = cooldown_seconds
        self._last_known: dict[str, Stock] = {}
        self._last_alert: dict[str, float] = {}

    def last_known(self, key: str) -> Stock | None:
        return self._last_known.get(key)

    def should_alert(self, key: str, stock: Stock) -> bool:
        prev = self._last_known.get(key)

        # Only advance "last known" on a definite signal; ignore UNKNOWN.
        if stock is not Stock.UNKNOWN:
            self._last_known[key] = stock

        if stock is not Stock.IN:
            return False
        if prev is Stock.IN:
            return False  # already in stock, already alerted

        last = self._last_alert.get(key, 0.0)
        if time.monotonic() - last < self.cooldown:
            return False

        self._last_alert[key] = time.monotonic()
        return True
