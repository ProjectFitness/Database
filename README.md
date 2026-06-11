# thesis-check

Stress-test a trade thesis against live market data, using Claude as the
analyst. You describe the trade in plain English ("short BTC because rates
are staying higher and risk appetite is rolling over"); the tool pulls a
live macro + BTC snapshot, then produces a structured report that:

- **checks each claim** in your thesis against real numbers,
- **argues the other side** properly (the steelman),
- **lists what would prove you wrong** — concrete invalidation triggers you
  can set alerts on,
- **recalls historical analogs** and what happened,
- gives a **verdict on the reasoning** — strong / moderate / weak — never a
  buy/sell signal.

It is a sparring partner, not an oracle: it audits your reasoning against
evidence, it does not predict prices.

## Setup

```bash
pip install -e .            # or: uv pip install -e .
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
# Full stress test
thesis-check "Short BTC: rates staying higher for longer, dollar strength, \
risk appetite rolling over into year end."

# From a file, written to a report
thesis-check --file thesis.txt --out report.md

# Raw structured JSON instead of markdown
thesis-check "..." --json

# Just the market snapshot — no API key needed
thesis-check --data-only
```

## Data sources (all free, no keys)

| Indicator | Source |
|---|---|
| Fed funds, 2Y/10Y Treasury yields, broad dollar index, CPI YoY, 10Y breakevens | FRED (St. Louis Fed) |
| BTC price, market cap, 7d/30d momentum, ATH drawdown | CoinGecko |
| BTC perpetual funding rate | Binance Futures |
| Crypto Fear & Greed index | alternative.me |

Every source fails independently — if one is down, the report notes the gap
instead of crashing, and the analysis flags what it couldn't verify.

The framework is asset-agnostic by design: adding equity, FX, or commodity
indicators means adding a fetcher module under `thesis_check/sources/` —
the analysis layer doesn't change.

## Development

```bash
pip install -e ".[dev]"
pytest            # offline test suite, all HTTP mocked
```

## Repo notes

`docs/quant-mind-evaluation.md` contains an earlier hands-on evaluation of
the LLMQuant/quant-mind framework, which preceded and informed this tool.
