"""Common shape for every fetched indicator.

Every fetcher returns Indicator objects and never raises: a source that is
down, blocked, or changed its format produces an Indicator with `error` set,
and the analysis step is told the data point was unavailable rather than
crashing the whole run.
"""

from __future__ import annotations

from dataclasses import dataclass, field


def short_error(exc: Exception) -> str:
    """First line of an exception message — httpx appends doc links we don't want."""
    return str(exc).splitlines()[0] if str(exc) else exc.__class__.__name__


@dataclass
class Indicator:
    name: str
    """Human-readable label, e.g. 'Effective Fed Funds Rate'."""

    source: str
    """Where the number came from, e.g. 'FRED (DFF)'."""

    value: float | None = None
    unit: str = ""
    as_of: str = ""
    """Date the observation refers to (not the fetch time)."""

    extra: dict = field(default_factory=dict)
    """Secondary readings, e.g. {'change_30d_pct': -4.2}."""

    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.value is not None

    def describe(self) -> str:
        """One-line plain-text rendering for prompts and reports."""
        if not self.ok:
            return f"{self.name}: UNAVAILABLE ({self.error}) [{self.source}]"
        parts = [f"{self.name}: {self.value:g}{self.unit}"]
        if self.as_of:
            parts.append(f"as of {self.as_of}")
        for key, val in self.extra.items():
            label = key.replace("_", " ")
            parts.append(f"{label}: {val:g}" if isinstance(val, (int, float)) else f"{label}: {val}")
        parts.append(f"[{self.source}]")
        return ", ".join(parts[:1] + parts[1:-1]) + " " + parts[-1]
