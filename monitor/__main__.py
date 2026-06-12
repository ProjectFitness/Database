"""Entrypoint:  python -m monitor [path/to/config.yaml]

Loads the watchlist, builds one shared HTTP client with a real desktop
User-Agent, and hands off to the polling engine.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import httpx
import yaml

from .engine import run

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


def load_watches(config_path: Path) -> tuple[list[dict], int]:
    with config_path.open() as fh:
        cfg = yaml.safe_load(fh)

    zip_code = str(cfg.get("zip", ""))
    cooldown = int(cfg.get("cooldown", 60))
    watches = cfg.get("watches", []) or []
    for w in watches:
        w["_zip"] = zip_code  # Target needs it; harmless elsewhere
    return watches, cooldown


async def main() -> None:
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("config.yaml")
    if not config_path.exists():
        print(f"Config not found: {config_path}")
        sys.exit(1)

    watches, cooldown = load_watches(config_path)
    print(f"Monitoring {len(watches)} product(s). Ctrl+C to stop.\n")

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/html;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        await run(client, watches, cooldown=cooldown)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
