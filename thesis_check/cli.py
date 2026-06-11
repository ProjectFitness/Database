"""Command-line entry point.

Usage:
    thesis-check "Short BTC: rates staying higher, dollar strength, ..."
    thesis-check --file my_thesis.txt --out report.md
    thesis-check --data-only          # just print the market snapshot
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from thesis_check.analyst import DEFAULT_MODEL, MissingAPIKeyError, analyze
from thesis_check.render import render_report, render_snapshot
from thesis_check.sources import fetch_btc, fetch_macro


def collect_snapshot() -> list:
    print("Fetching macro data (FRED)...", file=sys.stderr)
    indicators = fetch_macro()
    print("Fetching BTC market data...", file=sys.stderr)
    indicators += fetch_btc()
    ok = sum(1 for i in indicators if i.ok)
    print(f"Collected {ok}/{len(indicators)} indicators.", file=sys.stderr)
    return indicators


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="thesis-check",
        description="Stress-test a trade thesis against live macro and BTC data using Claude.",
    )
    parser.add_argument("thesis", nargs="?", help="The trade thesis, in plain English")
    parser.add_argument("--file", type=Path, help="Read the thesis from a text file instead")
    parser.add_argument("--out", type=Path, help="Write the markdown report to this file")
    parser.add_argument("--json", action="store_true", help="Print the raw structured report as JSON")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Claude model id (default: {DEFAULT_MODEL})")
    parser.add_argument(
        "--data-only",
        action="store_true",
        help="Fetch and print the market snapshot without running the analysis (no API key needed)",
    )
    args = parser.parse_args(argv)

    if args.data_only:
        print(render_snapshot(collect_snapshot()))
        return 0

    if args.file:
        thesis = args.file.read_text()
    elif args.thesis:
        thesis = args.thesis
    else:
        parser.error("provide a thesis as an argument, via --file, or use --data-only")
        return 2

    indicators = collect_snapshot()

    print(f"Running stress test with {args.model}...", file=sys.stderr)
    try:
        report = analyze(thesis, indicators, model=args.model)
    except MissingAPIKeyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        output = report.model_dump_json(indent=2)
    else:
        output = render_report(report, indicators)

    if args.out:
        args.out.write_text(output)
        print(f"Report written to {args.out}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
