"""Desktop alerting: Windows toast + sound, and optional auto-open browser.

Auto-open is per-retailer (Target/Walmart yes, Pokemon Center no). On non-Windows
machines the toast falls back to a console bell + print so the monitor still runs
during development.
"""
from __future__ import annotations

import platform
import sys
import webbrowser

_IS_WINDOWS = platform.system() == "Windows"

if _IS_WINDOWS:
    try:
        from winotify import Notification, audio
    except ImportError:  # surfaced clearly at startup by __main__
        Notification = None
        audio = None


def notify(title: str, message: str, url: str, open_browser: bool) -> None:
    if _IS_WINDOWS and Notification is not None:
        toast = Notification(
            app_id="Pokemon Monitor",
            title=title,
            msg=message,
            launch=url,  # clicking the toast opens the product page
        )
        toast.set_audio(audio.LoopingAlarm, loop=False)
        toast.add_actions(label="Open product", launch=url)
        toast.show()
    else:
        # Dev fallback: terminal bell + line so behavior is visible off-Windows.
        sys.stdout.write("\a")
        sys.stdout.flush()
        print(f"[ALERT] {title} | {message} | {url}")

    if open_browser:
        webbrowser.open_new_tab(url)
