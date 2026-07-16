# Ideas — What to Build on the GMGN Agent API

Ranked by leverage-per-effort. #1 and #2 are the ones I'd start this week.

## 1. The Memecoin Flight Recorder *(fits the repo name — recommended lead)*
GMGN gives you 1-minute trending granularity and Smart Money flows — **as of now**. Nobody can
query "what did the market look like 4 hours before X rugged?" because nobody kept the tape.
Build a scheduled collector (`gmgn-cli market trending`, `gmgn-track` on a watchlist of Smart
Money wallets, `gmgn-token security` for every new trender) that snapshots into SQLite every few
minutes. Value compounds daily and is unavailable at any price later:
- **Rug post-mortems:** replay holder concentration and Smart Money exits leading up to failures;
  distill the signatures into pre-trade checks that feed guardrails (`token_min_safety`).
- **KOL truth scores:** measure whether tracked wallets are actually early or just loud, using
  entry timestamps vs. price history — before copying anyone.
- **Signal backtesting:** any future "should I buy" heuristic gets tested against the recorded
  tape in paper mode instead of with live funds.

## 2. Injection-Firewalled Two-Agent Trading Desk
The core security problem (review C6): token metadata is attacker-controlled text, and the same
agent that reads it can sign trades. Split the roles:
- **Analyst agent** — has GMGN query access, reads all the dirty data, and may output *only* a
  strictly-typed JSON trade ticket (chain, address, size, thesis score, security findings). Free
  text from token metadata is stripped/escaped before it enters its context.
- **Executor** — a dumb, non-LLM wrapper that validates the ticket against
  `config/guardrails.json`, checks the kill-switch file, requests human confirmation, and only
  then invokes `gmgn-cli swap`. No LLM in the signing path ⇒ no prompt injection in the signing
  path.
This is also the natural home for the paper-trading mode GMGN doesn't offer: executor in
`mode: "paper"` logs the ticket + market snapshot instead of trading, and #1's recorder scores it
later.

## 3. Claude Code as the Trading Cockpit
Wire gmgn-skills into this repo's Claude setup (they ship a `.claude-plugin/`) plus:
- a **PreToolUse hook** that hard-blocks any `gmgn-cli swap|cooking` invocation unless a valid,
  recent, human-approved ticket file exists — human-in-the-loop enforced by the harness, not by
  prompt discipline;
- a `/morning-brief` skill: overnight trending diffs, watchlist wallet moves, open-order status,
  P&L — one command replaces the first 30 minutes of tab-checking.

## 4. Counterparty X-Ray (pre-trade due diligence in one command)
Compose `gmgn-token` holders/traders + `gmgn-portfolio` on the top holders: before touching a
token, profile *who you'd be trading against* — what % of supply sits with wallets that have a
history of coordinated exits, sniping, or fresh-wallet farming. GMGN exposes all the pieces; no
one has composed them into a single adversary report. Output feeds the ticket's thesis score in #2.

## 5. Regime-Aware Alerting, not price alerts
Everyone has price alerts. Using the recorder (#1), alert on *distribution changes*: "Smart Money
net flow on your held token flipped negative over 3 windows", "holder concentration in top-10
wallets rose 8% in an hour", "security score degraded (LP unlock)". These are the alerts that
precede the price move. Delivery via Routine → push/email digest.

## 6. Give GMGN the feedback (cheap goodwill)
File issues on GMGNAI/gmgn-skills for the review's C1 (agent-readable docs / llms.txt), C2
(`GMGN_SIGNING_KEY` naming), and C4 (dry-run flag on swap). Active repo, early ecosystem —
becoming a known early integrator has outsized returns if this project grows.
