# Pokemon TCG Stock Monitor — project context

Personal, single-user stock monitor for Pokemon TCG drops. Owner: Dominic
(zip 75063, Irving TX). Built collaboratively with Claude in June 2026.

## Hard rules — do not violate, even if asked casually
- NO auto-checkout. The human clicks buy. Alert + auto-open browser only.
- NO proxies, multi-session/multi-browser tricks, CAPTCHA bypass, fingerprint
  spoofing, or any anti-bot evasion. Polite single-client polling only.
- Pokemon Center is NOTIFY-ONLY (no auto-open) — it is aggressively anti-bot.
- Keep intervals conservative with jitter; backoff on blocks. A blocked
  monitor is slower than a polite one.

## What it does
- Polls Target (RedSky API, incl. in-store pickup at nearest store to zip),
  Walmart (__NEXT_DATA__ page JSON), Pokemon Center (page text markers).
- On OOS->IN flip: Windows toast + alarm sound; Target/Walmart also auto-open
  the product page; optional phone push via ntfy.sh (`ntfy_topic` in config).
- UNKNOWN (block/parse failure) is NEVER treated as in-stock. Fires once per
  drop with cooldown, re-arms on sellout.
- Logs every restock/sellout to events.csv (learn the local store's vendor
  schedule). Daily TCGplayer sealed-product prices via tcgcsv.com -> prices.csv.

## Layout
- `monitor/__main__.py` — entrypoint; `--test` fires a fake alert
- `monitor/engine.py` — per-watch async loops, live config reload (~2s),
  crash resurrection with 30s hold-down, daily price loop
- `monitor/state.py` — OOS->IN transition logic + flicker debounce
- `monitor/notifier.py` — toast/sound/browser + ntfy phone push
- `monitor/checkers/` — target.py, walmart.py, pokemoncenter.py (see module
  docstrings for re-tuning notes, e.g. rotating the RedSky key)
- `monitor/prices.py` — tcgcsv.com snapshots; also `python -m monitor.prices`
- `config.yaml` — watchlist (LIVE-RELOADED while running)
- `setup.bat` / `run_monitor.bat` — install+test / run-forever wrapper

## Commands
- Run: `run_monitor.bat`  (or `python -m monitor config.yaml`)
- Test alert chain: `python -m monitor --test`
- Price snapshot now: `python -m monitor.prices`

## Domain knowledge (verified June 2026)
- Target: 8-digit TCINs are first-party; 10-digit are Target Plus resellers —
  never watch those. RedSky `key` is a public web key that rotates; on
  persistent 401/403 grab a fresh one from DevTools on any product page.
- Walmart alerts: verify "Sold & shipped by Walmart" before buying.
- Restock patterns: Target Fri ~40% of events (overnight load 1-4am ET; restock
  window 3-6pm ET), Walmart Wed, Pokemon Center Tue/Thu 9am-1pm PT. Target
  card shelves are vendor-stocked (Excell Marketing), mornings 7-10am.
- Cloud/datacenter IPs are 403-blocked by ALL these retailers — parsers can
  only be tested from a residential connection (this PC).

## Status / next steps
- All logic is unit/smoke tested; parsers NOT yet validated against live
  sites. FIRST TASK on this PC: run the monitor, watch the first minute of
  logs, fix any checker returning UNKNOWN against real responses.
- Then: confirm a real `--test` toast fires, set `ntfy_topic` for phone push,
  add Task Scheduler "At log on" entry for run_monitor.bat.

## Git
- Branch: `claude/pokemon-tcg-drop-bot-9x91qh` (repo ProjectFitness/Database).
- Commit and push after changes; pull before starting work elsewhere — cloud
  sessions and this PC share state only through GitHub.
