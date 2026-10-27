# Hermes model setup — canonical workstation routing

This repository contains Daniel's exported default-profile model routing. It does NOT contain credentials, conversations, memories, bot configuration, or workstation paths.

## Install on another workstation

Install Hermes using the official instructions: https://hermes-agent.nousresearch.com/docs/
Install Git and Python 3.11+ if missing. Then:

```sh
git clone https://github.com/subtiliorars-sys/hermes-config.git
cd hermes-config
hermes auth add nous
python install.py --apply
```

On Linux/macOS use `python3` if `python` is unavailable. Restart Hermes afterward. A signed-in Nous account with access to these models is required; credentials and subscription entitlements do not travel through GitHub. Check pricing/entitlement in your own Portal account. No direct OpenAI or Gemini API key is required for the saved Nous routes.

For a preview run `python install.py`. For an existing clone run `git pull --ff-only` then `python install.py --apply`.

The installer asks `hermes config path` for the active destination; use `--home PATH` to target a specific Hermes home. It writes using `hermes config set`, backs up the config, verifies the values through `hermes config get --json`, and rolls back if a write/read-back fails. It preserves unrelated machine settings and credentials. Close other config editors while applying; the multi-command operation is not a cross-process transaction. Backups remain LOCAL and may contain existing secrets: do not commit them.

Ollama routes are included only if localhost:11434 is reachable and the exact model is installed. `--no-local` excludes them. The source workstation's private-IP proxy preset is intentionally excluded. Existing unrelated presets are retained.

## Current exported setup

- Primary and delegated agents: `openai/gpt-6-astra`, provider `nous`.
- Primary fallback order: `google/gemini-4-argon`, `deepseek/deepseek-v4.1-flash`, then the saved Nous free-model chain, then local `qwen3:4b` when available.
- Auxiliary tasks: `stepfun/step-3.7-flash:free`; vision: `ornith/ornith-1.5-122b:free`; saved free-model fallback chains included.
- Delegation limit: five concurrent children, two levels deep.
- MOA presets are exported, but the main route is direct Nous, NOT MOA. A selected MOA preset alone does not activate MOA.

`routing.json` is the canonical portable policy. `config.yaml` is a readable routing-only reference, NOT a complete config to copy over an existing installation. The exported identifiers are preserved exactly. Catalog reports flag missing IDs; this repo never silently replaces them. The initial live audit flags `upstage/solar-pro4:free` and `tencent/hy3:free` as missing from the Nous catalog. They remain in this exact-source snapshot; do not mistake them for verified working fallbacks.

The source workstation has local Hermes modifications; this repo distributes settings, NOT those patches or its entire runtime. The installer uses the supported config CLI. Verify inference on each destination; successful config read-back does not prove provider access or identical behavior on every Hermes version.

## Where the three-day automation lives

Previously the refresh was a LOCAL Hermes job (`9096b6607189`, `model-catalog-refresh`), not GitHub Actions. Its last recorded local run at export was 2026-10-24. The old public repo still pointed at `meituan/longcat-2.0:free`; there was no automatic sync from the Windows default profile.

Now `.github/workflows/model-catalog.yml` runs on GitHub. It wakes daily at 06:23 UTC, checks whether 72 hours have elapsed since the last successful audit, and only fetches when due. This avoids month-boundary errors in `*/3` day-of-month cron. Actual execution can be delayed by GitHub. Pushes affecting the audit code and manual dispatches run immediately.

Records:

- Actions: https://github.com/subtiliorars-sys/hermes-config/actions/workflows/model-catalog.yml
- `reports/latest.md`: latest attempt, human-readable route findings.
- `reports/latest.json`: last fully successful catalog snapshot.
- `reports/attempt.json`: latest attempt including fetch failures.
- Git history: durable audit records; Actions artifacts retained for 90 days.

This is a deterministic availability/pricing catalog audit, NOT an LLM agent benchmark. It makes no inference calls and uses no model API credentials. Catalog membership is not proof of inference health, vision capability, tool use, or subscription entitlement. Advertised zero text-token prices do not guarantee all modalities/features are free. No config self-healing runs in CI; fetch failures preserve the last successful JSON snapshot and fail the job visibly.

GitHub does not push settings directly onto your other computers. Pull and apply explicitly. Private account credentials stay on each device. The original local cron remains separate and unchanged; its legacy updater has weaker failure handling and is not copied here.

## Verification and rollback

```sh
python -m unittest discover -s tests -v
python catalog.py
hermes config get model --json
hermes config get delegation --json
```

After authentication, start a fresh Hermes chat to verify actual inference. To revert an applied policy, stop concurrent config writers and restore the `config.yaml.before-routing-<timestamp>` backup printed by the installer to that same home's `config.yaml`.

Official references: https://hermes-agent.nousresearch.com/docs/user-guide/configuration and https://hermes-agent.nousresearch.com/docs/integrations/providers
