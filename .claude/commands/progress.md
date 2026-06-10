---
description: Score trend across all sessions and the one thing to fix before your next real call.
---

# /progress

## Gather

Read the YAML frontmatter of every file in `sessions/` and the current `profile/dominic.md`. If there are no sessions beyond the baseline, say there is nothing to chart yet and how many spar sessions are needed for a trend (three), then stop.

## Report, in this order

1. **Trend line.** A compact table of all sessions, oldest first: date, type, persona or drill, overall score (extraction for spar, result for drill), landmine, objection, flags. Below it, an ASCII sparkline or bar row of extraction_total across spar sessions, with the baseline marked as the first point.

2. **The breakdown that matters.** Extraction by level (technical, business, personal) across time. Call out the gap explicitly: if personal-level extraction is flat near zero while overall climbs, say that the overall number is hiding the real problem. Same treatment for the four elements; name the weakest element and whether it is improving.

3. **Drill record.** Conversion rate per objection slug. Name any objection he has never passed.

4. **Pattern ledger.** Flag frequency from the profile tally: which patterns are decaying (good), which are stable, which are growing. A pattern that appears in 3 consecutive sessions gets named as entrenched.

5. **Against baseline.** Current 3-session average versus the calibration baseline, by level and element, in one short table.

6. **The one thing.** End with exactly one instruction to execute on his next real discovery call. Not a theme, an instruction, concrete enough that the next session can check whether he did it. Derive it from the most expensive growing or entrenched pattern, not from the lowest number. Write it to the profile's watch list as the current priority.

## Rules

Numbers always carry their raw counts. No encouragement padding; if the trend is flat or down, the first line of the report says so. If the trend is genuinely up, say that plainly too, one line. No em dashes anywhere in the output.
