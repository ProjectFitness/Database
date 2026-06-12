"""Desktop alerting: Windows toast + sound, optional auto-open browser, and
optional phone push via ntfy.sh.

Auto-open is per-retailer (Target/Walmart yes, Pokemon Center no). On non-Windows
machines the toast falls back to a console bell + print so the monitor still runs
during development.

Phone push: set `ntfy_topic` in config.yaml to any hard-to-guess string, install
the ntfy app on your phone, and subscribe to that same topic. Drops then reach
you anywhere, not just at the PC. The push is sent from a background thread so a
slow network can never stall the watch loops. Treat the topic name like a
password — anyone who knows it can see your alerts.
"""
from __future__ import annotations

import platform
import sys
import threading
import urllib.request
import webbrowser

_IS_WINDOWS = platform.system() == "Windows"

NTFY_TOPIC = ""  # set from config by the engine; empty = phone push disabled


def set_ntfy_topic(topic: str) -> None:
    global NTFY_TOPIC
    NTFY_TOPIC = topic.strip()


def _push_phone(title: str, message: str, url: str) -> None:
    req = urllib.request.Request(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode(),
        headers={
            "Title": title,
            "Click": url,
            "Priority": "urgent",
            "Tags": "rotating_light",
        },
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as exc:
        print(f"[notify] phone push failed: {exc}")

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

    if NTFY_TOPIC:
        threading.Thread(
            target=_push_phone, args=(title, message, url), daemon=True
        ).start()

    if open_browser:
        webbrowser.open_new_tab(url)
