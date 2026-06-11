"""Macro indicators from FRED (St. Louis Fed).

Uses the keyless ``fredgraph.csv`` endpoint, which serves any public series
as a two-column CSV (date, value). Missing observations appear as ".".
"""

from __future__ import annotations

import datetime as dt

import httpx

from thesis_check.sources.base import Indicator, short_error

FREDGRAPH_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
TIMEOUT = 15.0
USER_AGENT = "thesis-check/0.1 (+https://github.com/ProjectFitness/Database)"

# (series_id, display name, unit)
SERIES = [
    ("DFF", "Effective Fed Funds Rate", "%"),
    ("DGS2", "2-Year Treasury Yield", "%"),
    ("DGS10", "10-Year Treasury Yield", "%"),
    ("DTWEXBGS", "Broad US Dollar Index", ""),
    ("T10YIE", "10-Year Breakeven Inflation", "%"),
]

CPI_SERIES = ("CPIAUCSL", "CPI Inflation (YoY)", "%")


def _fetch_series(client: httpx.Client, series_id: str) -> list[tuple[str, float]]:
    """Return [(date, value), ...] for the last ~14 months, oldest first."""
    start = (dt.date.today() - dt.timedelta(days=430)).isoformat()
    resp = client.get(
        FREDGRAPH_URL,
        params={"id": series_id, "cosd": start},
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    rows: list[tuple[str, float]] = []
    for line in resp.text.strip().splitlines()[1:]:  # skip header
        date, _, raw = line.partition(",")
        raw = raw.strip()
        if raw and raw != ".":
            try:
                rows.append((date.strip(), float(raw)))
            except ValueError:
                continue
    return rows


def fetch_macro() -> list[Indicator]:
    """Fetch the macro snapshot. Each series fails independently."""
    indicators: list[Indicator] = []
    with httpx.Client(follow_redirects=True) as client:
        for series_id, name, unit in SERIES:
            source = f"FRED ({series_id})"
            try:
                rows = _fetch_series(client, series_id)
                if not rows:
                    raise ValueError("no observations returned")
                date, value = rows[-1]
                indicators.append(
                    Indicator(name=name, source=source, value=value, unit=unit, as_of=date)
                )
            except Exception as exc:
                indicators.append(Indicator(name=name, source=source, error=short_error(exc)))

        # CPI YoY is computed from the monthly index level 12 months apart.
        series_id, name, unit = CPI_SERIES
        source = f"FRED ({series_id})"
        try:
            rows = _fetch_series(client, series_id)
            if len(rows) < 13:
                raise ValueError(f"need 13 monthly observations, got {len(rows)}")
            date, latest = rows[-1]
            _, year_ago = rows[-13]
            yoy = (latest / year_ago - 1.0) * 100.0
            indicators.append(
                Indicator(name=name, source=source, value=round(yoy, 2), unit=unit, as_of=date)
            )
        except Exception as exc:
            indicators.append(Indicator(name=name, source=source, error=short_error(exc)))

    return indicators
