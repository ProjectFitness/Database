"""Polling engine: one independent loop per watch, running concurrently.

Each loop sleeps `interval` seconds plus random jitter (so we don't poll on a
robotic fixed cadence), and applies exponential backoff when a checker returns
UNKNOWN repeatedly (a stand-in for blocks / errors) so we ease off instead of
hammering a retailer that's pushing back.
"""
from __future__ import annotations

import asyncio
import random
from datetime import datetime

from .checkers.base import Stock
from .notifier import notify
from .state import StateTracker

JITTER_FRAC = 0.35          # +/- 35% of the interval
MAX_BACKOFF_MULTIPLIER = 8  # cap when repeatedly blocked


def _log(retailer: str, name: str, detail: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{ts}  [{retailer:<13}] {name[:40]:<40} {detail}")


async def _watch_loop(client, checker, watch: dict, state: StateTracker) -> None:
    key = f"{checker.retailer}:{watch.get('tcin') or watch.get('url')}"
    base = float(watch.get("interval", 30))
    consecutive_unknown = 0

    while True:
        result = await checker.check(client, watch)
        _log(checker.retailer, watch["name"], result.detail)

        if result.stock is Stock.UNKNOWN:
            consecutive_unknown = min(consecutive_unknown + 1, 6)
        else:
            consecutive_unknown = 0

        if state.should_alert(key, result.stock):
            _log(checker.retailer, watch["name"], ">>> IN STOCK — alerting")
            notify(
                title=f"IN STOCK: {watch['name']}",
                message=f"{checker.retailer.title()} — {result.detail}",
                url=result.url,
                open_browser=checker.auto_open,
            )

        backoff = min(2 ** consecutive_unknown, MAX_BACKOFF_MULTIPLIER) if consecutive_unknown else 1
        delay = base * backoff
        delay += random.uniform(-JITTER_FRAC, JITTER_FRAC) * delay
        await asyncio.sleep(max(delay, 1.0))


async def run(client, watches: list[dict], cooldown: int = 60) -> None:
    state = StateTracker(cooldown_seconds=cooldown)
    from .checkers import REGISTRY

    tasks = []
    for watch in watches:
        checker_cls = REGISTRY.get(watch["retailer"])
        if checker_cls is None:
            _log(watch["retailer"], watch.get("name", "?"), "no checker for retailer — skipping")
            continue
        tasks.append(_watch_loop(client, checker_cls(), watch, state))

    if not tasks:
        print("No valid watches configured. Edit config.yaml and try again.")
        return
    await asyncio.gather(*tasks)
