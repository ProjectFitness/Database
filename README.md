# GMGN Agent API — Project Setup

Integration workspace for the [GMGN Agent API](https://docs.gmgn.ai/index/gmgn-agent-api): AI-agent-driven
memecoin market data and on-chain trading across Solana, BSC, Base, and Ethereum.

## What's here

| Path | Purpose |
|------|---------|
| `scripts/setup.sh` | One-shot local setup: prereq checks, Ed25519 keygen, credential config, read-only verification |
| `.env.example` | Template for GMGN credentials (never commit the real one) |
| `config/guardrails.example.json` | Proposed hard trading limits, enforced in code — not in prompts |
| `docs/gmgn-agent-api-review.md` | Full review and critique of the API, docs, and security model |
| `docs/DECISIONS.md` | Decisions only the project owner can make — read this first |
| `docs/IDEAS.md` | Product/architecture ideas for building on top of the API |

> [!IMPORTANT]
> **Convention:** anything in this project that requires the owner's hands or a decision is
> flagged with an `ACTION REQUIRED` callout like the one below. If it isn't flagged, it's
> automated or already handled.

## Quickstart

> [!WARNING]
> **ACTION REQUIRED — do these 3 steps in order (~5 minutes):**
> 1. Run `./scripts/setup.sh` — it checks prerequisites, generates your Ed25519 keypair, and
>    prints your **public key**.
> 2. Log in at **https://gmgn.ai/ai**, upload that public key, and copy the API key it issues.
> 3. Paste the key when the script prompts (or add `GMGN_API_KEY=...` to `~/.config/gmgn/.env`),
>    then verify with:
>    ```bash
>    gmgn-cli market trending --chain sol --interval 1h --limit 3
>    ```
>
> Until step 2, the script falls back to the shared read-only demo key — fine for smoke tests only.

## Ground rules (non-negotiable until revisited in docs/DECISIONS.md)

1. **Read-only first.** No `GMGN_PRIVATE_KEY` in any environment until the guardrails wrapper exists.
2. **Credentials never enter the repo.** `.gitignore` blocks `.env` and `*.pem`; keys live in
   `~/.config/gmgn/` with `chmod 600`.
3. **`GMGN_PRIVATE_KEY` is the API request-signing key, not a wallet key** — but treat it as
   money-moving: anyone holding it can submit trades from your account.
4. **Every trading feature ships behind a human confirmation step** until explicitly waived.

## Known environment constraints

- GMGN OpenAPI is **IPv4 only**.
- **Restricted-egress runners need an allowlist entry:** the API lives at `openapi.gmgn.ai`
  (key creation at `gmgn.ai`). Claude Code web sessions with a limited network policy will get
  proxy 403s on every call until both domains are added to the environment's allowed domains.
- **API keys are cryptographically bound to one key pair.** `gmgn-cli config --apply` fails with
  "does not match your local key pair" if the key was minted against a public key generated on a
  different machine. Key pair and API key must be created as a pair, on the machine that will use them.
- The docs site (docs.gmgn.ai) blocks non-browser clients — see the review doc for why that matters.
- Demo key `gmgn_solbscbaseethmonadtron` is public, shared, and read-only; fine for smoke tests, not for anything rate-sensitive.
