# B2B Sales Discovery Agent

A personal training tool for enterprise discovery calls, built as Claude Code skills. Designed for selling research & advisory (Gartner) to technology leaders — CIO, CISO, CDAO, Head of AI — at sub-$1B-revenue financial services firms, where the buyer rarely has a seat at the table and every deal hinges on anchoring to a quantified corporate objective.

## Usage

Open this repo in Claude Code and use:

| Command | What it does |
|---|---|
| `/roleplay` | Claude plays a guarded CIO/CISO/CDAO/Head-of-AI buyer (easy → realistic → hostile). You run discovery against it. Ends with an honest scored debrief that reveals what you failed to uncover. Mid-scene controls: `pause`, `rewind`, `harder`, `easier`, `end call`. |
| `/coach` | Three modes: paste what a prospect said and get 2nd/3rd-level follow-up ladders; have your planned questions critiqued and rewritten; or run rapid-fire drills against objections and prospect statements. |
| `/prep` | Feed it an upcoming meeting (persona, firm, context) and get a one-page call plan: objective hypotheses, a Challenger opening, question trees with anchor checkpoints, trap doors, power-map blanks, and exit criteria. Can hand off directly into `/roleplay` to pressure-test the plan. |

## Methodology

Gap Selling (current state → root cause → quantified impact → future state → cost of inaction) blended with Challenger (teach, tailor, take control). The standard every skill grades against: did you surface a **quantified, time-bound corporate objective owned above the buyer**, technology's contribution to it, and the cost of inaction?

## Structure

```
.claude/skills/   roleplay, coach, prep
knowledge/        methodology, personas, FS priorities, objection bank, scoring rubric
sessions/         saved roleplay debriefs (trend-tracked across sessions)
plans/            saved call plans
```

The `knowledge/` files are meant to grow — add real objections you hit, new persona quirks, and sub-vertical details over time, and every skill gets sharper.
