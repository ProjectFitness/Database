# Decision Log — Owner Input Required

Things Claude cannot or should not decide alone. Each has a recommendation; the project is
structured so everything above the line works before any of these are resolved.

## Blocking (needed before first real API call beyond the demo key)

### 1. GMGN account + API key creation — *only you can do this*
Creating a personal API key at **https://gmgn.ai/ai** requires logging into your GMGN account and
uploading the public key that `scripts/setup.sh` prints. This is an account-bound, identity-bound
action.
**Needed from you:** run the setup script (or just the keygen step), upload the public key, and
place the resulting key in `~/.config/gmgn/.env`.

### 2. Custody & funding model
Trading through GMGN means trading from a GMGN-managed wallet context. How much capital goes in,
from which wallet, on which chain, is a pure risk/ownership call.
**Recommendation:** a dedicated, freshly funded wallet with an amount you can lose entirely
(memecoins routinely go to zero); never a wallet holding anything else.

## Blocking for trading features only

### 3. Enable trading at all? (and when)
The scaffold deliberately leaves `GMGN_PRIVATE_KEY` unset. Options:
- **(a) Read-only indefinitely** — data/analytics product only. Zero fund risk.
- **(b) Confirm-each-trade** — agent proposes, you approve every order. *(Recommended first step)*
- **(c) Autonomous within guardrails** — agent trades inside hard caps. Only after (b) has run
  cleanly for a while and the guardrails wrapper is built and tested in paper mode.

### 4. Risk limits (fill in `config/guardrails.json`)
Defaults proposed in `guardrails.example.json` are deliberately tiny: $25/trade, $100/day, 3 open
positions, Solana only, 2% max slippage, mandatory exit strategy, mandatory security check.
**Needed from you:** confirm or change every number. These are the numbers that bound worst-case
loss from a bug, a hallucination, or an injection.

### 5. Jurisdiction / tax posture
Automated crypto trading has tax reporting consequences (every swap is a taxable event in most
jurisdictions) and possible regulatory constraints depending on where you are.
**Needed from you:** confirm you're comfortable; not something to infer.

## Non-blocking (decide as the project takes shape)

### 6. What is this project, primarily?
The repo is named `Database` — the strongest build direction (see IDEAS.md #1) is a time-series
store of GMGN market/wallet snapshots for longitudinal analysis, which fits the name. Alternatives:
a trading copilot, a KOL-copy research tool, an alerting service. Pick one to lead.

### 7. Runtime & storage stack
gmgn-skills is TypeScript/Node. Recommendation: Node/TS for the API layer to stay native with
their tooling; SQLite to start for snapshots (file-based, zero ops), Postgres/Timescale if volume
demands it.

### 8. Where does this run?
Local machine vs. VPS vs. this remote environment. Note: GMGN is IPv4-only, and scheduled data
collection (IDEAS.md #1/#5) implies an always-on host. Also decide where the signing key may live —
recommendation: only on hardware you control, never in a shared/cloud env until #3(c) is settled.
