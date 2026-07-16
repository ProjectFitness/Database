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

## Quickstart

```bash
./scripts/setup.sh          # generates keys, configures ~/.config/gmgn/.env, verifies with demo key
```

Then create your personal API key at **https://gmgn.ai/ai** by uploading the public key the script
prints, and paste the key when prompted (or add it to `~/.config/gmgn/.env` later).

Verify:

```bash
gmgn-cli market trending --chain sol --interval 1h --limit 3
```

## Ground rules (non-negotiable until revisited in docs/DECISIONS.md)

1. **Read-only first.** No `GMGN_PRIVATE_KEY` in any environment until the guardrails wrapper exists.
2. **Credentials never enter the repo.** `.gitignore` blocks `.env` and `*.pem`; keys live in
   `~/.config/gmgn/` with `chmod 600`.
3. **`GMGN_PRIVATE_KEY` is the API request-signing key, not a wallet key** — but treat it as
   money-moving: anyone holding it can submit trades from your account.
4. **Every trading feature ships behind a human confirmation step** until explicitly waived.

## Known environment constraints

- GMGN OpenAPI is **IPv4 only**.
- The docs site (docs.gmgn.ai) blocks non-browser clients — see the review doc for why that matters.
- Demo key `gmgn_solbscbaseethmonadtron` is public, shared, and read-only; fine for smoke tests, not for anything rate-sensitive.
