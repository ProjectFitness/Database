# GMGN Agent API — Review & Critique

*Reviewed 2026-07-16 against https://docs.gmgn.ai/index/gmgn-agent-api, the official
[GMGNAI/gmgn-skills](https://github.com/GMGNAI/gmgn-skills) repo (MIT, TypeScript, ~380 stars,
actively maintained), and third-party coverage.*

## What it is

GMGN's Agent API is not a classic REST surface — it is a **skills toolkit** (`gmgn-skills`) plus a
CLI (`gmgn-cli`) designed to be driven by AI agents (Claude, Cursor, Codex, OpenCode plugins ship
in-repo). A separate, traditional **GMGN OpenAPI** exists for raw endpoint access. The Agent API
wraps six skill domains:

| Skill | Capability |
|-------|-----------|
| `gmgn-token` | Token info, security/rug analysis, pools, holders, traders |
| `gmgn-market` | K-lines, trending rankings (1-minute granularity, 500+ data dimensions) |
| `gmgn-portfolio` | Wallet holdings, activity, P&L stats |
| `gmgn-track` | Follow-wallet trades, KOL activity, Smart Money moves |
| `gmgn-swap` | Market/limit orders, TP/SL, trailing strategies, order tracking |
| `gmgn-cooking` | One-command buy + attached exit strategy |

Chains: Solana, BSC, Base, Ethereum (+ "Robinhood" for data-only; trading is sol/bsc/base/eth).
Claimed sub-0.3s order submission latency. Auth: locally generated Ed25519 keypair; public half
uploaded at https://gmgn.ai/ai to mint an API key; the private half signs requests.

## What they got right

1. **Asymmetric auth is the correct choice.** No bearer secret ever transits to GMGN; a leaked API
   key alone can't sign trades. This is better than most crypto data APIs (typically static bearer
   tokens).
2. **A public read-only demo key** removes the biggest onboarding friction — you can evaluate the
   data quality before creating an account.
3. **Skills-first packaging is genuinely agent-native.** Shipping Claude/Cursor/Codex plugin
   manifests and workflow guides in-repo beats "here's a swagger file, good luck."
4. **Honest risk disclosure.** The docs explicitly name model hallucination and prompt injection as
   execution risks. Most vendors don't.
5. **Exit-strategy-attached orders** (`condition-orders` on swap, the `cooking` skill) mean an agent
   can never open a naked position if you require it — a good primitive for automation safety.

## Critique — where it falls short

### Critical

- **C1. The docs site blocks agents.** `docs.gmgn.ai` returns 403 to non-browser clients
  (Cloudflare). An *Agent API* whose documentation is unreadable by agents is self-defeating: any
  AI integrator must scrape mirrors or the GitHub repo. They should publish `llms.txt` /
  raw-markdown docs endpoints.
- **C2. Dangerous credential naming.** The env var is `GMGN_PRIVATE_KEY`, in an ecosystem where
  "private key" universally means *wallet* key. The docs themselves have to disclaim the confusion.
  Predictable failure mode: a user pastes their actual wallet private key into a config file that
  tooling, logs, and LLM context windows all touch. Should be `GMGN_SIGNING_KEY`.
- **C3. No server-side spend limits.** There is no documented way to scope an API key (read-only
  vs. trading, per-key spend caps, chain restrictions, IP allowlists). A compromised signing key =
  unlimited trading authority until manually revoked. All damage control is pushed client-side —
  hence our `config/guardrails.example.json`.
- **C4. No sandbox or paper-trading mode.** The official guidance is "test with small amounts" —
  i.e., test in production with real money. For an API explicitly marketed to autonomous agents,
  the absence of a dry-run flag on `swap` is the single biggest product gap.

### Significant

- **C5. Undocumented rate limits, fees, and error semantics** in the public docs. You discover
  limits by hitting them; fee structure (GMGN takes a trading fee) must be inferred from the
  product, not the API docs. No published SLA or status page reference.
- **C6. Prompt-injection surface is the data itself.** Token names, ticker symbols, and social
  links returned by the query skills are attacker-controlled strings that flow straight into the
  agent's context — and the same agent holds trading authority. GMGN names the risk but ships no
  mitigation (no sanitized/structured-only response mode). See IDEAS.md #2 for our containment
  design.
- **C7. Key lifecycle is undocumented.** No visible docs on key rotation, revocation, multiple
  keys per account, or audit logs of API-initiated trades. For a money-moving credential this is
  table stakes.
- **C8. Plaintext key at rest.** The blessed setup stores the signing PEM inline in
  `~/.config/gmgn/.env`. `chmod 600` is the only protection; no OS-keychain integration, no
  encrypted-at-rest option, and inlining the PEM into an env var makes it visible to `ps`/`env`
  dumps and crash logs.
- **C9. IPv4 only.** Breaks on IPv6-only cloud runners (increasingly common) with no documented
  workaround.

### Minor

- **C10. Chain support matrix is inconsistent** across docs: "Robinhood" appears in the demo key
  and chain lists but is excluded from trading and Smart Money tracking; Monad/Tron appear in the
  demo key string but not the docs. The support matrix needs one authoritative table.
- **C11. "MCP architecture" is marketing-loose.** Coverage describes it as MCP-based, but the repo
  ships a CLI with per-editor plugin folders, not an MCP server. Works fine, but integrators
  expecting `mcp.json`-style wiring will be confused.
- **C12. Docs live in a tutorial site, not an API reference.** Endpoint-level request/response
  schemas exist only as CLI help text and workflow guides; there's no OpenAPI spec published for
  the Agent API surface itself.

## Verdict

**Adopt for market data now; gate trading behind our own guardrails layer.** The data surface
(token security, Smart Money/KOL tracking, 1-minute trending) is differentiated and the agent
packaging is ahead of competitors. The trading surface is powerful but structurally trusting —
no sandbox, no server-side caps, injection-exposed — so it must never be wired directly to an
autonomous loop. Read-only integration is low-risk today; live trading only after decisions #2–#4
in `DECISIONS.md` are made and the guardrails wrapper exists.
