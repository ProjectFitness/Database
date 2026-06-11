"""The LLM analysis step: thesis + market snapshot -> structured stress test.

Uses the Claude API with a Pydantic-validated structured output, so the
report always parses. Requires ANTHROPIC_API_KEY (or ANTHROPIC_AUTH_TOKEN)
in the environment.
"""

from __future__ import annotations

import datetime as dt
import os

import anthropic

from thesis_check.schema import ThesisReport
from thesis_check.sources.base import Indicator

DEFAULT_MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = """\
You are a buy-side risk analyst whose job is to stress-test trade theses, not
to validate them. The user will give you a thesis and a snapshot of current
market data. You must:

1. Extract every load-bearing claim in the thesis (factual claims about the
   world AND directional claims about what follows from them) and check each
   against the data snapshot. Cite specific numbers. If a claim cannot be
   checked with the data provided, mark it unverifiable rather than guessing.
2. Build the steelman: the strongest honest case for the opposite side of the
   trade. Argue it properly; do not strawman.
3. List concrete invalidation triggers: observable events or data prints that
   would kill a leg of the thesis. These should be specific enough that the
   user could set an alert for them.
4. Recall historical analogs: past episodes with a similar setup, what
   happened, and the lesson. Be honest when analogs are weak or conflicting.
5. Give a verdict. Never say "do the trade" or "don't do the trade" — assess
   how well the reasoning holds up, what the biggest risk is, and what the
   user should verify next.

Some data points may be marked UNAVAILABLE. Do not invent values for them;
list them under data_gaps and explain what each gap prevents you from
checking. Be direct and specific. Vague risk language ("markets can be
volatile") is worthless to this user — they are an experienced multi-asset
investor.
"""


class MissingAPIKeyError(RuntimeError):
    pass


def build_user_prompt(thesis: str, indicators: list[Indicator]) -> str:
    lines = [ind.describe() for ind in indicators]
    snapshot = "\n".join(f"- {line}" for line in lines) if lines else "- (no data collected)"
    return (
        f"Today's date: {dt.date.today().isoformat()}\n\n"
        f"## Market data snapshot\n{snapshot}\n\n"
        f"## Trade thesis to stress-test\n{thesis.strip()}\n"
    )


def analyze(
    thesis: str,
    indicators: list[Indicator],
    model: str = DEFAULT_MODEL,
) -> ThesisReport:
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        raise MissingAPIKeyError(
            "No Anthropic API key found. Set ANTHROPIC_API_KEY in your environment "
            "(get one at https://platform.claude.com). The data snapshot still works "
            "without it: run with --data-only."
        )

    client = anthropic.Anthropic()
    response = client.messages.parse(
        model=model,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(thesis, indicators)}],
        output_format=ThesisReport,
    )
    report = response.parsed_output
    if report is None:
        raise RuntimeError(
            f"Model response did not parse into a report (stop_reason={response.stop_reason})"
        )
    return report
