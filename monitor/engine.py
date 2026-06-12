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
import csv
import random
import time
from datetime import datetime
from pathlib import Path

from . import config as config_mod
from .checkers import REGISTRY
from .checkers.base import Stock
from .notifier import notify, set_ntfy_topic
from .prices import snapshot
from .state import StateTracker

PRICE_SNAPSHOT_SECONDS = 24 * 3600  # tcgcsv updates once a day

JITTER_FRAC = 0.35           # +/- 35% of the interval
MAX_BACKOFF_MULTIPLIER = 8   # cap when repeatedly blocked
CONFIG_POLL_SECONDS = 2.0    # how often we look for config.yaml changes
CRASH_HOLDDOWN_SECONDS = 30  # wait before restarting a crashed watch loop


def _log(retailer: str, name: str, detail: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{ts}  [{retailer:<13}] {name[:40]:<40} {detail}")


EVENTS_CSV = Path("events.csv")


def _record_event(retailer: str, name: str, event: str, detail: str) -> None:
    """Append a stock transition to events.csv — over weeks this becomes your
    own per-store restock-pattern dataset (day of week + hour included so the
    pattern falls out of a pivot table)."""
    now = datetime.now().astimezone()
    new_file = not EVENTS_CSV.exists()
    with EVENTS_CSV.open("a", newline="") as fh:
        writer = csv.writer(fh)
        if new_file:
            writer.writerow(["timestamp", "day_of_week", "hour", "retailer", "product", "event", "detail"])
        writer.writerow([
            now.isoformat(timespec="seconds"),
            now.strftime("%A"),
            now.hour,
            retailer,
            name,
            event,
            detail,
        ])


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

        prev = state.last_known(key)
        if result.stock is not Stock.UNKNOWN and prev is not None and result.stock is not prev:
            _record_event(
                checker.retailer,
                watch["name"],
                "restock" if result.stock is Stock.IN else "sellout",
                result.detail,
            )

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


async def _price_loop(client, config_path: Path) -> None:
    """Daily market-price snapshot for the sealed items in config (tcg_prices).
    Reads config fresh each cycle so edits apply without restart. Failures are
    logged and retried in an hour — price history is nice-to-have, never worth
    crashing the stock watchers over."""
    while True:
        delay = PRICE_SNAPSHOT_SECONDS
        try:
            _, settings = config_mod.load(config_path)
            wrote = await snapshot(client, settings["tcg_prices"])
            if not wrote and not settings["tcg_prices"]:
                delay = 3600  # nothing configured yet; check again hourly
        except Exception as exc:
            _log("prices", "daily snapshot", f"failed ({exc}) — retrying in 1h")
            delay = 3600
        await asyncio.sleep(delay)


async def run(client, config_path: Path) -> None:
    state = StateTracker()
    asyncio.create_task(_price_loop(client, config_path))
    tasks: dict[str, asyncio.Task] = {}
    snapshots: dict[str, dict] = {}
    crash_times: dict[str, float] = {}
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
                watches, settings = config_mod.load(config_path)
            except Exception as exc:
                print(f"config reload failed ({exc}) — keeping previous watchlist")
                watches = None

            if watches is not None:
                state.cooldown = settings["cooldown"]
                set_ntfy_topic(settings["ntfy_topic"])
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

        # Resurrect any watch loop that died on an unexpected exception — a
        # parser bug on one product must never silently stop its watch. The
        # hold-down keeps a permanently broken watch from restart-spamming.
        for key, task in list(tasks.items()):
            if task.done() and not task.cancelled():
                w = snapshots.get(key)
                if w is None:
                    tasks.pop(key)
                    continue
                crashed_at = crash_times.get(key)
                if crashed_at is None:
                    crash_times[key] = time.monotonic()
                    _log(
                        w["retailer"],
                        w.get("name", key),
                        f"watch crashed ({task.exception()!r}) — restarting in {CRASH_HOLDDOWN_SECONDS}s",
                    )
                elif time.monotonic() - crashed_at >= CRASH_HOLDDOWN_SECONDS:
                    crash_times.pop(key, None)
                    tasks[key] = asyncio.create_task(
                        _watch_loop(client, REGISTRY[w["retailer"]](), w, state, key)
                    )

        await asyncio.sleep(CONFIG_POLL_SECONDS)
