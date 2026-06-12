"""Polling engine: one independent loop per watch, plus live config reload.

Each watch loop sleeps `interval` seconds plus random jitter (so we don't poll on
a robotic fixed cadence), and applies exponential backoff when a checker returns
UNKNOWN repeatedly (a stand-in for blocks / errors) so we ease off instead of
hammering a retailer that's pushing back.

A supervisor loop watches config.yaml's mtime: save the file and new watches
start immediately, removed ones stop, edited ones restart with the new settings —
no restart needed when a SKU drops on X and you're adding it in a hurry. If a
reload fails to parse (e.g. saved mid-edit), the previous watchlist keeps running.
"""
from __future__ import annotations

import asyncio
import random
from datetime import datetime
from pathlib import Path

from . import config as config_mod
from .checkers import REGISTRY
from .checkers.base import Stock
from .notifier import notify
from .state import StateTracker

JITTER_FRAC = 0.35           # +/- 35% of the interval
MAX_BACKOFF_MULTIPLIER = 8   # cap when repeatedly blocked
CONFIG_POLL_SECONDS = 2.0    # how often we look for config.yaml changes


def _log(retailer: str, name: str, detail: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{ts}  [{retailer:<13}] {name[:40]:<40} {detail}")


async def _watch_loop(client, checker, watch: dict, state: StateTracker, key: str) -> None:
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


async def run(client, config_path: Path) -> None:
    state = StateTracker()
    tasks: dict[str, asyncio.Task] = {}
    snapshots: dict[str, dict] = {}
    last_mtime: float | None = None

    while True:
        try:
            mtime = config_path.stat().st_mtime
        except OSError:
            mtime = last_mtime  # file briefly missing during an editor save

        if mtime != last_mtime:
            first_load = last_mtime is None
            last_mtime = mtime
            try:
                watches, cooldown = config_mod.load(config_path)
            except Exception as exc:
                print(f"config reload failed ({exc}) — keeping previous watchlist")
                watches = None

            if watches is not None:
                state.cooldown = cooldown
                desired: dict[str, tuple[dict, type]] = {}
                for w in watches:
                    checker_cls = REGISTRY.get(w.get("retailer", ""))
                    if checker_cls is None:
                        _log(str(w.get("retailer")), w.get("name", "?"), "no checker for retailer — skipping")
                        continue
                    desired[config_mod.watch_key(w)] = (w, checker_cls)

                for key in list(tasks):
                    if key not in desired or snapshots.get(key) != desired[key][0]:
                        tasks.pop(key).cancel()
                        snapshots.pop(key, None)
                        if key not in desired:
                            _log(key.split(":", 1)[0], key, "removed from watchlist")

                for key, (w, checker_cls) in desired.items():
                    if key not in tasks:
                        tasks[key] = asyncio.create_task(
                            _watch_loop(client, checker_cls(), w, state, key)
                        )
                        snapshots[key] = dict(w)
                        _log(w["retailer"], w["name"], f"watching (every ~{w.get('interval', 30)}s)")

                if not first_load:
                    print(f"-- config reloaded: {len(tasks)} watch(es) active --")
                elif not tasks:
                    print("No valid watches configured. Edit config.yaml — it reloads live.")

        await asyncio.sleep(CONFIG_POLL_SECONDS)
