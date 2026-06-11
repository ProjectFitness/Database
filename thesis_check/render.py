"""Render a ThesisReport (and the data snapshot) as readable markdown."""

from __future__ import annotations

import datetime as dt

from thesis_check.schema import ThesisReport
from thesis_check.sources.base import Indicator

_STATUS_MARK = {
    "supported": "✅ supported",
    "contradicted": "❌ contradicted",
    "mixed": "⚖️ mixed",
    "unverifiable": "❓ unverifiable",
}

_STRENGTH_MARK = {
    "strong": "🟢 STRONG",
    "moderate": "🟡 MODERATE",
    "weak": "🔴 WEAK",
}


def render_snapshot(indicators: list[Indicator]) -> str:
    lines = ["## Market data snapshot", ""]
    ok = [i for i in indicators if i.ok]
    failed = [i for i in indicators if not i.ok]
    for ind in ok:
        lines.append(f"- {ind.describe()}")
    if failed:
        lines.append("")
        lines.append("Unavailable sources:")
        for ind in failed:
            lines.append(f"- {ind.name} — {ind.error} [{ind.source}]")
    lines.append("")
    return "\n".join(lines)


def render_report(report: ThesisReport, indicators: list[Indicator]) -> str:
    out: list[str] = []
    out.append(f"# Thesis Stress Test — {dt.date.today().isoformat()}")
    out.append("")
    out.append(f"**Thesis:** {report.thesis_summary}")
    out.append("")
    out.append(f"**Verdict: {_STRENGTH_MARK.get(report.verdict.thesis_strength, report.verdict.thesis_strength)}** — {report.verdict.summary}")
    out.append("")
    out.append(render_snapshot(indicators))

    out.append("## Claim-by-claim check")
    out.append("")
    for claim in report.claims:
        out.append(f"### {_STATUS_MARK.get(claim.status, claim.status)} — {claim.claim}")
        out.append("")
        out.append(claim.evidence)
        out.append("")

    out.append("## The other side of the trade (steelman)")
    out.append("")
    for point in report.steelman:
        out.append(f"- {point}")
    out.append("")

    out.append("## What would prove you wrong")
    out.append("")
    for trig in report.invalidation_triggers:
        out.append(f"- **{trig.trigger}** — {trig.why_it_matters}")
    out.append("")

    if report.historical_analogs:
        out.append("## Historical rhymes")
        out.append("")
        for analog in report.historical_analogs:
            out.append(f"- **{analog.period}** — {analog.setup} Outcome: {analog.outcome}")
        out.append("")

    out.append("## Key risks")
    out.append("")
    for risk in report.verdict.key_risks:
        out.append(f"- {risk}")
    out.append("")

    if report.data_gaps:
        out.append("## Data gaps in this analysis")
        out.append("")
        for gap in report.data_gaps:
            out.append(f"- {gap}")
        out.append("")

    out.append("## Suggested homework")
    out.append("")
    for item in report.verdict.suggested_homework:
        out.append(f"- {item}")
    out.append("")
    out.append("---")
    out.append(
        "*This is an automated stress test of your reasoning, not investment advice. "
        "It checks your claims against data and argues the other side; it does not predict prices.*"
    )
    return "\n".join(out)
