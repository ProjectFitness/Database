"""Entrypoint:  python -m monitor [path/to/config.yaml] [--test]

Loads the watchlist, builds one shared HTTP client with a real desktop
User-Agent, and hands off to the polling engine. The watchlist reloads live:
edit and save config.yaml while the monitor runs and changes apply within
seconds, no restart.

--test fires a fake in-stock alert (toast + sound + browser open) so you can
verify notifications actually reach you BEFORE a real drop. Run it once after
setup, and again if you change Windows notification settings.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import httpx

from .engine import run
from .notifier import notify

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


async def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--test"]
    if "--test" in sys.argv[1:]:
        print("Firing test alert — you should hear a sound, see a toast, and get a browser tab.")
        notify(
            title="TEST: Pokemon Monitor is working",
            message="If you can see and HEAR this, you're ready for a real drop.",
            url="https://www.target.com",
            open_browser=True,
        )
        return

    config_path = Path(args[0]) if args else Path("config.yaml")
    if not config_path.exists():
        print(f"Config not found: {config_path}")
        sys.exit(1)

    print("Monitor starting. Edit config.yaml anytime — it reloads live. Ctrl+C to stop.\n")

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/html;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        await run(client, config_path)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
