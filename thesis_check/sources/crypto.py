"""BTC market indicators: spot/derivatives data and sentiment.

All sources are keyless free APIs. Each indicator fails independently.
"""

from __future__ import annotations

import datetime as dt

import httpx

from thesis_check.sources.base import Indicator, short_error

TIMEOUT = 15.0
USER_AGENT = "thesis-check/0.1 (+https://github.com/ProjectFitness/Database)"

COINGECKO_MARKETS = "https://api.coingecko.com/api/v3/coins/markets"
BINANCE_PREMIUM = "https://fapi.binance.com/fapi/v1/premiumIndex"
FEAR_GREED = "https://api.alternative.me/fng/"


def _today() -> str:
    return dt.date.today().isoformat()


def fetch_btc() -> list[Indicator]:
    indicators: list[Indicator] = []
    headers = {"User-Agent": USER_AGENT}

    with httpx.Client(follow_redirects=True, headers=headers) as client:
        # Price, market cap, momentum — CoinGecko
        try:
            resp = client.get(
                COINGECKO_MARKETS,
                params={
                    "vs_currency": "usd",
                    "ids": "bitcoin",
                    "price_change_percentage": "7d,30d",
                },
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            row = resp.json()[0]
            indicators.append(
                Indicator(
                    name="BTC Price",
                    source="CoinGecko",
                    value=float(row["current_price"]),
                    unit=" USD",
                    as_of=_today(),
                    extra={
                        "change_24h_pct": round(row.get("price_change_percentage_24h") or 0.0, 2),
                        "change_7d_pct": round(
                            row.get("price_change_percentage_7d_in_currency") or 0.0, 2
                        ),
                        "change_30d_pct": round(
                            row.get("price_change_percentage_30d_in_currency") or 0.0, 2
                        ),
                        "ath_drawdown_pct": round(row.get("ath_change_percentage") or 0.0, 2),
                    },
                )
            )
            indicators.append(
                Indicator(
                    name="BTC Market Cap",
                    source="CoinGecko",
                    value=round(float(row["market_cap"]) / 1e9, 1),
                    unit="B USD",
                    as_of=_today(),
                )
            )
        except Exception as exc:
            indicators.append(Indicator(name="BTC Price", source="CoinGecko", error=short_error(exc)))

        # Perp funding rate — Binance futures. Positive funding = longs pay
        # shorts (crowded long); negative = shorts pay (crowded short).
        try:
            resp = client.get(BINANCE_PREMIUM, params={"symbol": "BTCUSDT"}, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            rate_pct = float(data["lastFundingRate"]) * 100.0
            indicators.append(
                Indicator(
                    name="BTC Perp Funding Rate (8h)",
                    source="Binance Futures",
                    value=round(rate_pct, 4),
                    unit="%",
                    as_of=_today(),
                    extra={"annualized_pct": round(rate_pct * 3 * 365, 1)},
                )
            )
        except Exception as exc:
            indicators.append(
                Indicator(name="BTC Perp Funding Rate (8h)", source="Binance Futures", error=short_error(exc))
            )

        # Crypto Fear & Greed index — alternative.me (0 = extreme fear, 100 = extreme greed)
        try:
            resp = client.get(FEAR_GREED, params={"limit": 1}, timeout=TIMEOUT)
            resp.raise_for_status()
            entry = resp.json()["data"][0]
            indicators.append(
                Indicator(
                    name="Crypto Fear & Greed Index",
                    source="alternative.me",
                    value=float(entry["value"]),
                    unit="/100",
                    as_of=_today(),
                    extra={"classification": entry.get("value_classification", "")},
                )
            )
        except Exception as exc:
            indicators.append(
                Indicator(name="Crypto Fear & Greed Index", source="alternative.me", error=short_error(exc))
            )

    return indicators
