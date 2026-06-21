#!/usr/bin/env bash
# VPS healthcheck — no live Discord connection; no secret values printed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${DEPLOY_DIR}/../../.." && pwd)"
ENV_FILE="${SWARM_COMMANDER_ENV:-/opt/dreamos/secrets/swarm-commander.env}"
VENV="${REPO_ROOT}/.venv"
FAIL=0

log_ok() { echo "CHECK=PASS $*"; }
log_fail() { echo "CHECK=FAIL $*" >&2; FAIL=1; }

echo "HEALTHCHECK=swarm-commander repo=${REPO_ROOT}"

# Python version
PY_VER="$("${VENV}/bin/python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)"
if [[ -z "${PY_VER}" ]]; then
  log_fail python_venv
else
  MAJOR="${PY_VER%%.*}"
  MINOR="${PY_VER#*.}"
  if (( MAJOR >= 3 && MINOR >= 10 )); then
    log_ok "python_version=${PY_VER}"
  else
    log_fail "python_version=${PY_VER} (need >=3.10)"
  fi
fi

# venv
if [[ -x "${VENV}/bin/python" ]]; then
  log_ok venv_exists
else
  log_fail venv_missing path="${VENV}"
fi

# Required deploy + runtime files
REQUIRED=(
  "${DEPLOY_DIR}/.env.example"
  "${DEPLOY_DIR}/requirements-headless.txt"
  "${DEPLOY_DIR}/systemd/swarm-commander.service"
  "${REPO_ROOT}/src/agent_tools/discord_commander/bot_runner_service.py"
  "${REPO_ROOT}/src/agent_tools/discord_commander/unified_discord_bot.py"
  "${REPO_ROOT}/src/agent_tools/discord_commander/outbound_router.py"
  "${REPO_ROOT}/src/agent_tools/discord_commander/agent_message_sender.py"
  "${REPO_ROOT}/tests/test_discord_commander_toolbelt.py"
)
for f in "${REQUIRED[@]}"; do
  if [[ -f "${f}" ]]; then
    log_ok "file=$(basename "${f}")"
  else
    log_fail "missing=${f}"
  fi
done

# .env.example placeholders only (values empty after =)
if grep -E '^[A-Z0-9_]+=[^[:space:]]+' "${DEPLOY_DIR}/.env.example" 2>/dev/null | grep -q .; then
  log_fail env_example_has_non_empty_values
else
  log_ok env_example_placeholders
fi

# No committed live secrets in tracked files (heuristic)
if command -v git >/dev/null 2>&1 && git -C "${REPO_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git -C "${REPO_ROOT}" grep -E 'gh[pousr]_[A-Za-z0-9_]{20,}|discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]{20,}' \
    -- ':!deploy/vps/swarm-commander/.env.example' ':!tests/*' 2>/dev/null | grep -q .; then
    log_fail committed_secret_pattern_detected
  else
    log_ok no_committed_secrets_heuristic
  fi
fi

# External env: token present only outside repo (boolean only)
if [[ -f "${ENV_FILE}" ]]; then
  if grep -q '^DISCORD_BOT_TOKEN=[^[:space:]]' "${ENV_FILE}" 2>/dev/null; then
    log_ok external_env_token_present
  else
    log_fail external_env_token_missing
  fi
else
  echo "CHECK=SKIP external_env_not_installed path=${ENV_FILE}"
fi

# Import smoke (no Discord connection)
export PYTHONPATH="${REPO_ROOT}/src"
if "${VENV}/bin/python" - <<'PY'
import importlib
mods = [
    "agent_tools.discord_commander",
    "agent_tools.discord_commander.outbound_router",
    "agent_tools.discord_commander.agent_message_sender",
    "agent_tools.discord_commander.commands.messaging_commands",
    "agent_tools.discord_commander.lifecycle.bot_lifecycle",
]
for m in mods:
    importlib.import_module(m)
print("IMPORT_SMOKE=PASS")
PY
then
  log_ok import_smoke
else
  log_fail import_smoke
fi

# CLI dry-runs without live connection
if "${VENV}/bin/python" -m agent_tools.discord_commander outbound-dry-run >/dev/null 2>&1; then
  log_ok outbound_dry_run_cli
else
  # Expected WEBHOOK_MISSING when unset is exit 1 — still proves CLI loads
  OUT="$("${VENV}/bin/python" -m agent_tools.discord_commander outbound-dry-run 2>&1 || true)"
  if echo "${OUT}" | grep -q 'WEBHOOK_MISSING\|webhook\|No webhook'; then
    log_ok outbound_dry_run_webhook_missing_expected
  else
    log_fail outbound_dry_run_cli
  fi
fi

if (( FAIL == 0 )); then
  echo "HEALTHCHECK=PASS"
  exit 0
fi
echo "HEALTHCHECK=FAIL"
exit 1
