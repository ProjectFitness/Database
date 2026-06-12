"""Watchlist loading, shared by startup and live reload."""
from __future__ import annotations

from pathlib import Path

import yaml


def load(config_path: Path) -> tuple[list[dict], int]:
    with config_path.open() as fh:
        cfg = yaml.safe_load(fh) or {}

    zip_code = str(cfg.get("zip", ""))
    cooldown = int(cfg.get("cooldown", 60))
    watches = cfg.get("watches", []) or []
    for w in watches:
        w["_zip"] = zip_code  # Target needs it; harmless elsewhere
    return watches, cooldown


def watch_key(watch: dict) -> str:
    return f"{watch['retailer']}:{watch.get('tcin') or watch.get('url')}"
