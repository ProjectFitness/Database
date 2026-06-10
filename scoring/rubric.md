# Scoring Rubric

All scores in this project are computed from the dossier's truth inventory and the session transcript. Nothing is scored on vibes. The verifier has final say.

## 1. Extraction score (spar sessions)

Every dossier contains a truth inventory: a numbered table of facts, each tagged with a Level and a deal Element.

Levels:
- **T (technical):** systems, projects, architecture, compliance specifics
- **B (business):** money, timelines, politics, organizational consequence
- **P (personal):** what this means for the CIO's own career, credibility, and fears

Elements:
- **Pain:** the problem and its consequences
- **Metrics:** numbers that size the pain or the decision
- **Power:** who decides, who blocks, who the CIO answers to
- **Urgency:** why now, the compelling event, the cost of delay

A fact counts as **surfaced** only if all three hold:

1. The CIO actually stated it in the transcript (verbatim quote required).
2. A question or move from Dominic earned it per the fact's "earned by" condition. Facts the CIO let slip through roleplay error do not count.
3. Dominic acknowledged or used it. A fact stated by the CIO and then talked past counts at half weight.

**Extraction score = surfaced facts / total facts**, reported overall, then broken out by Level and by Element. Report raw counts next to every percentage, for example: business 36% (4/11).

### Bands

| Overall | Read |
|---|---|
| Under 30% | Poor. The dossier beat you. |
| 30 to 50% | Developing. Typical for a resistant CIO. |
| 50 to 70% | Solid. Deal-ready discovery. |
| Over 70% | Strong. Rare against a persistent deflector. |

A high overall score with personal-level at zero is not a win and must be called out as such. Deals at Gartner contract values are justified at the personal-stakes level.

## 2. Modifiers

- **Landmine:** `avoided` or `triggered`. Triggering it ends or craters the call realistically. The session is still logged and scored on what was extracted before the blast. Note what was said that triggered it, verbatim.
- **Objection conversion:** every dossier carries a "why not just AI / peers / free content" objection. Scored `converted` (reframed to defensibility: cost of a bad decision, board credibility, regulator-proof validation, and landed a question that makes the CIO weigh that cost), `partial` (reframed but never landed the question), or `failed` (defended the product, listed features, discounted, or capitulated).
- **Question stacking:** count of turns where Dominic asked two or more questions at once. Each instance is a flag.

## 3. No-deal sessions

Some dossiers are not deals. For those, extraction scoring inverts into qualification scoring:

- **Disqualifiers found:** how many of the dossier's disqualifying facts Dominic surfaced (same evidence rules).
- **The call:** did he correctly qualify out (or route to a low-cost nurture path), and how many minutes in?
- **Pass:** 3 or more disqualifiers surfaced and a clean exit inside 20 minutes.
- **Fail:** booked a follow-up, pitched value, or mistook warmth for progress. Flag `happy-ears` and `rapport-overrun`.

## 4. Drill scoring

Drills are pass/fail on a single behavior: did he convert the objection to the defensibility frame, or did he defend the product?

- **Pass:** named the real risk (cost of a bad decision, board credibility, regulator-proof validation), priced it or got the CIO to price it, and turned it back with one question.
- **Partial:** right frame, but lectured instead of asking, or buckled on the second push-back.
- **Fail:** defended product features, compared Gartner to the alternative on quality, offered discount or free content, or agreed to "send some info."

The CIO in a drill pushes back at least twice. Surviving the first exchange is not a pass.

## 5. Pattern flags

Canonical flag vocabulary (extend it in `profile/dominic.md` as calibration and sessions reveal more):

| Flag | Meaning |
|---|---|
| `bail-on-deflection` | Accepted the first deflection and changed topic |
| `no-quantification` | Heard pain, never asked what it costs |
| `stays-technical` | Never moved the conversation to business or personal stakes |
| `rapport-overrun` | Confused a friendly conversation with progress |
| `question-stacking` | Multiple questions in one turn |
| `feature-defense` | Answered an objection by defending the product |
| `happy-ears` | Heard buying signals that were not there; failed to qualify out |
| `monologue` | Talked more than the CIO for a stretch of 3+ turns |
| `premature-pitch` | Started selling before pain, power, and urgency were established |

## 6. Session log format

Every session writes `sessions/YYYY-MM-DD-<type>-<slug>.md` beginning with this YAML frontmatter, which `/progress` parses:

```yaml
---
date: 2026-06-12
type: spar            # spar | drill | baseline
persona: regional-bank-cio   # or drill objection slug
extraction_total: 42  # percent; omit for drills
extraction_technical: 60
extraction_business: 36
extraction_personal: 0
pain: 50
metrics: 33
power: 25
urgency: 50
landmine: avoided     # avoided | triggered | n/a
objection: failed     # converted | partial | failed | n/a
drill_result: n/a     # pass | partial | fail | n/a
no_deal_call: n/a     # correct | missed | n/a
patterns: [bail-on-deflection, no-quantification]
one_fix: "Ask what the slip costs per month before offering anything."
---
```

Body sections, in order: Scores (with counts), Pattern flags (each with the transcript quote that evidences it), Verifier findings (verbatim from the verifier), One thing to fix, Transcript, and for spar sessions a final section listing the varied dossier values that were in play.
