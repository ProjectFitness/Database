# Pokemon TCG Stock Monitor

A personal, single-user stock monitor for Pokemon TCG drops at **Target**,
**Walmart**, and **Pokemon Center**. When an item you're watching flips from
out-of-stock to in-stock, you get a loud Windows notification — and for Target
and Walmart it also auto-opens the product page in your browser so you land on
the buy button before the public Discord crowd's ping even arrives.

This is **not** an auto-checkout bot. You make the purchase. It does not use
proxies, multiple sessions, CAPTCHA bypass, or anything that defeats a
retailer's anti-bot controls. Its only edge is being *your* monitor instead of
one feed shared by thousands of people.

## Why this helps

Public alert groups are slow for a structural reason: one monitor finds a drop,
then fans the same ping out to thousands of subscribers at once (and gets
rate-limited doing it). Everyone downstream gets it at the same already-delayed
moment. A monitor running just for you skips all of that.

It's also always-on, which is the answer to "Target drops at random times" — it
catches the state change whenever it happens, day or night.

## Setup (Windows)

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configure

Edit `config.yaml`:

- **Target** — `tcin` is the number at the end of the product URL
  (`.../-/A-89542109` -> `tcin: "89542109"`). Set your `zip` so it checks your
  local store too.
- **Walmart** — paste the full product `url`.
- **Pokemon Center** — paste the full product `url` (notify-only by design).

Intervals are in seconds and intentionally polite. Going lower gets you 403s
from Walmart/Pokemon Center, which makes you slower, not faster.

## Run

```bat
python -m monitor config.yaml
```

Leave it running. You'll see one log line per check; on a drop it alerts once
(with a cooldown so it won't spam), then re-arms when the item sells out again.

**Live reload:** `config.yaml` is re-read while the monitor runs. When a SKU
gets posted on X, paste it into the file and save — it's being watched within
~2 seconds, no restart. A broken save (bad YAML) keeps the previous watchlist
running.

**Test your alerts before a real drop:**

```bat
python -m monitor --test
```

fires a fake in-stock alert. If you don't hear a sound, fix Windows
notification settings now (see below), not during a drop.

## Make sure a drop can actually wake you

- Turn **off** Focus Assist / Do Not Disturb for the Pokemon Monitor app, or
  whitelist it — a suppressed toast is a missed drop.
- Set Windows **power settings** so the PC never sleeps while monitoring
  (display off is fine; sleep stops the monitor).
- Keep volume up. The alert uses a looping alarm sound, not the default ding.

## Honest limitations

- Retailer page shapes and API keys change. If a retailer starts logging
  `UNKNOWN`, the parser/selector for it needs a quick re-tune — see the notes at
  the top of each file in `monitor/checkers/`.
- `UNKNOWN` (a block or parse failure) is never treated as a drop, so a bot-block
  can't trigger a false alert.
- Walmart and Pokemon Center are heavily bot-protected; expect intermittent
  blocks. Target's RedSky API is the most reliable of the three.
- This will not out-race a dedicated proxy-rotating bot. It beats manual buyers
  and shared alert feeds — which is most of the field.
