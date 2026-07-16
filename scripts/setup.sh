#!/usr/bin/env bash
# GMGN Agent API — local setup.
# Idempotent: safe to re-run. Never overwrites existing keys or credentials.
set -euo pipefail

CONFIG_DIR="${HOME}/.config/gmgn"
ENV_FILE="${CONFIG_DIR}/.env"
PRIV_PEM="${CONFIG_DIR}/gmgn_signing_private.pem"
PUB_PEM="${CONFIG_DIR}/gmgn_signing_public.pem"
DEMO_KEY="gmgn_solbscbaseethmonadtron"

say()  { printf '\n\033[1m%s\033[0m\n' "$*"; }
warn() { printf '\033[33m%s\033[0m\n' "$*"; }
die()  { printf '\033[31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

say "1/5 Checking prerequisites"
command -v openssl >/dev/null || die "openssl is required (used for Ed25519 keygen)"
command -v node    >/dev/null || die "node is required (gmgn-cli is an npm package)"
command -v npx     >/dev/null || die "npx is required"
# GMGN OpenAPI is IPv4-only; fail early if this host resolves to IPv6 without fallback.
if command -v curl >/dev/null && ! curl -4 -s --max-time 10 -o /dev/null https://gmgn.ai; then
  warn "Could not reach gmgn.ai over IPv4. The API is IPv4-only — check your network before continuing."
fi
echo "ok"

say "2/5 Installing GMGN skills + CLI"
npx skills add GMGNAI/gmgn-skills
command -v gmgn-cli >/dev/null || npm install -g gmgn-cli
echo "gmgn-cli: $(gmgn-cli --version 2>/dev/null || echo 'installed via npx')"

say "3/5 Generating Ed25519 request-signing keypair"
mkdir -p "${CONFIG_DIR}"
chmod 700 "${CONFIG_DIR}"
if [[ -f "${PRIV_PEM}" ]]; then
  warn "Signing key already exists at ${PRIV_PEM} — keeping it."
else
  ( umask 077 && openssl genpkey -algorithm ed25519 -out "${PRIV_PEM}" )
  openssl pkey -in "${PRIV_PEM}" -pubout -out "${PUB_PEM}"
  chmod 600 "${PRIV_PEM}"
fi
echo
echo "Public key (upload this at https://gmgn.ai/ai to create your API key):"
echo "----------------------------------------------------------------------"
cat "${PUB_PEM}"
echo "----------------------------------------------------------------------"

say "4/5 Writing credential file"
if [[ -f "${ENV_FILE}" ]]; then
  warn "${ENV_FILE} already exists — keeping it. Edit it manually if needed."
else
  read -r -p "Paste your GMGN API key (or press Enter to use the read-only demo key for now): " USER_KEY
  API_KEY="${USER_KEY:-${DEMO_KEY}}"
  ( umask 077 && printf 'GMGN_API_KEY=%s\n' "${API_KEY}" > "${ENV_FILE}" )
  chmod 600 "${ENV_FILE}"
  if [[ "${API_KEY}" == "${DEMO_KEY}" ]]; then
    warn "Using the shared demo key: read-only, shared rate limits. Replace it once you have a personal key."
  fi
  # Deliberately NOT writing GMGN_PRIVATE_KEY: trading stays disabled until
  # guardrails exist (docs/DECISIONS.md, decision #3). Enable it consciously:
  #   echo 'GMGN_PRIVATE_KEY="<pem contents>"' >> ~/.config/gmgn/.env
fi
echo "ok: ${ENV_FILE}"

say "5/5 Verifying read-only access"
set -a; source "${ENV_FILE}"; set +a
if gmgn-cli market trending --chain sol --interval 1h --limit 3; then
  say "Setup complete. Trading is intentionally NOT enabled — see docs/DECISIONS.md."
else
  die "Verification call failed. Check the API key, IPv4 connectivity, and gmgn-cli installation."
fi
