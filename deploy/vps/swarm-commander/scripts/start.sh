#!/usr/bin/env bash
# Start Swarm Commander (foreground — systemd uses bot_runner_service directly).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${DEPLOY_DIR}/../../.." && pwd)"
ENV_FILE="${SWARM_COMMANDER_ENV:-/opt/dreamos/secrets/swarm-commander.env}"
VENV="${REPO_ROOT}/.venv"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "FAIL=SECRETS_MISSING env=${ENV_FILE}" >&2
  exit 1
fi

# shellcheck disable=SC1090
set -a
source "${ENV_FILE}"
set +a

export PYTHONPATH="${REPO_ROOT}/src:${PYTHONPATH:-}"
export DREAMVAULT_ROOT="${DREAMVAULT_ROOT:-/opt/dreamos/DreamVault}"

exec "${VENV}/bin/python" -m agent_tools.discord_commander.bot_runner_service
