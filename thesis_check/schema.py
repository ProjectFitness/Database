"""Pydantic schema for the structured stress-test report Claude returns."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ClaimAssessment(BaseModel):
    claim: str = Field(description="One factual or directional claim extracted from the thesis")
    status: Literal["supported", "contradicted", "mixed", "unverifiable"] = Field(
        description="Whether the available data currently supports the claim"
    )
    evidence: str = Field(
        description="The specific data points or reasoning behind the status, citing numbers from the snapshot where possible"
    )


class InvalidationTrigger(BaseModel):
    trigger: str = Field(description="A concrete, observable event or data print")
    why_it_matters: str = Field(description="Which leg of the thesis it would invalidate and why")


class HistoricalAnalog(BaseModel):
    period: str = Field(description="When the analogous episode occurred")
    setup: str = Field(description="How that episode resembled the current thesis setup")
    outcome: str = Field(description="What actually happened, and the lesson for this trade")


class Verdict(BaseModel):
    thesis_strength: Literal["strong", "moderate", "weak"] = Field(
        description="Overall assessment of how well the thesis holds up to the evidence"
    )
    summary: str = Field(
        description="Plain-language bottom line: which claims hold, which don't, and the single biggest risk"
    )
    key_risks: list[str] = Field(description="The most important ways this trade loses money")
    suggested_homework: list[str] = Field(
        description="Specific things to check or monitor before/while holding the position"
    )


class ThesisReport(BaseModel):
    thesis_summary: str = Field(description="The trade and its reasoning, restated in one or two sentences")
    claims: list[ClaimAssessment] = Field(description="Each load-bearing claim, checked against the data")
    steelman: list[str] = Field(
        description="The strongest arguments for the OPPOSITE side of the trade"
    )
    invalidation_triggers: list[InvalidationTrigger]
    historical_analogs: list[HistoricalAnalog]
    data_gaps: list[str] = Field(
        description="Relevant data that was unavailable or not collected, and how it limits the analysis"
    )
    verdict: Verdict
