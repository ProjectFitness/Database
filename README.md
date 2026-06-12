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

## Phone push (so being away from the PC doesn't cost you a drop)

1. Install the free **ntfy** app (iPhone/Android), no account needed.
2. In the app, subscribe to a topic with a long, unguessable name
   (it works like a password — e.g. `dd-pokemon-x7k2m9qz`).
3. Put the same name in `config.yaml` as `ntfy_topic` and save.

Drops now hit your phone as urgent pushes with a tap-to-open product link, on
top of the PC toast. `python -m monitor --test` verifies the whole chain.

## Keep it alive 24/7 (a dead monitor catches nothing)

- Run `run_monitor.bat` instead of the bare command — it relaunches the
  monitor automatically if it ever crashes.
- To survive reboots: Task Scheduler -> Create Task -> trigger "At log on" ->
  action: start `run_monitor.bat` in this folder.
- Inside the monitor, a watch loop that hits an unexpected error is restarted
  automatically and logged — one flaky product can't silently stop its watch.

## Make sure a drop can actually wake you

- Turn **off** Focus Assist / Do Not Disturb for the Pokemon Monitor app, or
  whitelist it — a suppressed toast is a missed drop.
- Set Windows **power settings** so the PC never sleeps while monitoring
  (display off is fine; sleep stops the monitor).
- Keep volume up. The alert uses a looping alarm sound, not the default ding.

## Event log (learn your store's pattern)

Every restock and sellout is appended to `events.csv` with timestamp, day of
week, and hour. After a few weeks this is your own dataset: open it in Excel
and pivot on day/hour to see exactly when your local Target's vendor scans in
stock and when online drops hit — your store's real schedule, not rumors.

## Market prices (know whether to hold or flip)

Once a day the monitor snapshots TCGplayer market prices (via the free
tcgcsv.com mirror — no API key) for the sealed items listed under `tcg_prices`
in config.yaml, appending to `prices.csv`. You can also run one on demand:

```bat
python -m monitor.prices
```

Pair `prices.csv` with `events.csv` and you have the full picture: what you can
buy at retail, and what the market pays for it — the spread that decides
whether a purchase is worth it before you click buy.

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
