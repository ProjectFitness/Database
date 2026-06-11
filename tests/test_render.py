from thesis_check.analyst import build_user_prompt
from thesis_check.render import render_report, render_snapshot
from thesis_check.schema import (
    ClaimAssessment,
    HistoricalAnalog,
    InvalidationTrigger,
    ThesisReport,
    Verdict,
)
from thesis_check.sources.base import Indicator

INDICATORS = [
    Indicator(name="BTC Price", source="CoinGecko", value=67000.0, unit=" USD", as_of="2026-06-11"),
    Indicator(name="2-Year Treasury Yield", source="FRED (DGS2)", error="HTTP 403"),
]

REPORT = ThesisReport(
    thesis_summary="Short BTC on the view that rates stay high and risk appetite rolls over.",
    claims=[
        ClaimAssessment(
            claim="Rates are staying higher for longer",
            status="supported",
            evidence="Fed funds at 4.33% with no cuts priced in.",
        ),
        ClaimAssessment(
            claim="Risk appetite is rolling over",
            status="unverifiable",
            evidence="Equity flow data was not collected in this snapshot.",
        ),
    ],
    steelman=["ETF inflows remain structurally positive.", "Halving supply dynamics favor longs."],
    invalidation_triggers=[
        InvalidationTrigger(
            trigger="A dovish FOMC surprise (50bp cut)",
            why_it_matters="Kills the rates leg of the thesis outright.",
        )
    ],
    historical_analogs=[
        HistoricalAnalog(
            period="2022 hiking cycle",
            setup="Rising real yields alongside crypto drawdown.",
            outcome="BTC fell ~65% peak to trough; the macro short worked.",
        )
    ],
    data_gaps=["No ETF flow data", "No options skew data"],
    verdict=Verdict(
        thesis_strength="moderate",
        summary="The rates leg holds; the positioning leg is unproven.",
        key_risks=["Short squeeze on crowded positioning"],
        suggested_homework=["Check ETF net flows for the past two weeks"],
    ),
)


def test_render_snapshot_separates_ok_and_failed():
    text = render_snapshot(INDICATORS)
    assert "BTC Price: 67000 USD" in text
    assert "Unavailable sources:" in text
    assert "2-Year Treasury Yield — HTTP 403" in text


def test_render_report_contains_all_sections():
    text = render_report(REPORT, INDICATORS)
    for heading in (
        "# Thesis Stress Test",
        "## Claim-by-claim check",
        "## The other side of the trade (steelman)",
        "## What would prove you wrong",
        "## Historical rhymes",
        "## Key risks",
        "## Data gaps in this analysis",
        "## Suggested homework",
    ):
        assert heading in text, f"missing section: {heading}"
    assert "MODERATE" in text
    assert "✅ supported" in text
    assert "❓ unverifiable" in text
    assert "not investment advice" in text


def test_build_user_prompt_includes_data_and_thesis():
    prompt = build_user_prompt("Short BTC because rates.", INDICATORS)
    assert "BTC Price: 67000 USD" in prompt
    assert "UNAVAILABLE (HTTP 403)" in prompt
    assert "Short BTC because rates." in prompt


def test_report_round_trips_through_json():
    raw = REPORT.model_dump_json()
    assert ThesisReport.model_validate_json(raw) == REPORT
