# Hermes Config

Portable Hermes Agent setup. Duplicate your Linux config on any machine.

## Setup

1. Install Hermes: `pip install hermes-agent` (or via mise/pipx)
2. Copy `config.yaml` to `~/.hermes/config.yaml`
3. Copy `.env.example` to `~/.hermes/.env` and fill in your keys
4. Run `hermes auth add nous` to link your Nous Portal account
5. Run `hermes doctor` to verify

## Fallback Chain

Primary: `meituan/longcat-2.0:free` via Nous Portal
Fallbacks: 19 free models across Nous + OpenRouter

## Files

- `config.yaml` — full Hermes config (safe to share)
- `.env.example` — template for secrets (NEVER commit your real .env)
