# Discovery Dojo (Phase 1)

A personal Claude Code training environment with one purpose: make Dominic measurably better at Gartner GTS discovery calls. It learns his weaknesses and attacks them.

## Quickstart

```
cd Database
claude
```

Then, in order:

1. `/calibrate` (first run only). A structured interview about your last 3 real discovery calls. Produces `profile/dominic.md`, your scouting report and baseline score. Nothing else runs until this exists.
2. `/spar` Fight a resistant CIO for about 20 minutes. The CIO works from a hidden dossier and only reveals what your questions earn. Ends with an extraction score, a verifier audit, and the one thing to fix.
3. `/drill` A 10-minute rep against one of your four kill-shot objections (ChatGPT instead of analysts, free peer calls, R&A is the first budget cut, "just send the Magic Quadrant"). Scored pass or fail on whether you converted it to the defensibility frame.
4. `/progress` Trend of your scores across all sessions, pattern flag frequency, and the single thing to fix before your next real call.

## House rules

- Do not read `personas/`. The dossiers are the answer key. Reading them wastes your reps, and sessions randomize the details anyway.
- The verifier audits every claim against the transcript. "I found the pain" requires a quote.
- A bad session gets called a bad session. That is the point.

## Layout

```
.claude/commands/   slash commands (calibrate, spar, drill, progress)
.claude/agents/     verifier subagent
personas/           hidden CIO dossiers (do not read)
profile/            dominic.md, the compounding scouting report
scoring/            rubric.md, how everything is scored
sessions/           one log per session, parsed by /progress
```
