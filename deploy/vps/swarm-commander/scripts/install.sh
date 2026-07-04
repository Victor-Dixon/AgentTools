#!/usr/bin/env bash
# Install Swarm Commander on Ubuntu VPS (headless). Does not start bot if secrets missing.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${DEPLOY_DIR}/../../.." && pwd)"
ENV_FILE="${SWARM_COMMANDER_ENV:-/opt/dreamos/secrets/swarm-commander.env}"
ENV_EXAMPLE="${DEPLOY_DIR}/.env.example"
VENV="${REPO_ROOT}/.venv"
SERVICE_NAME="swarm-commander.service"
RUN_USER="${SWARM_COMMANDER_USER:-dreamos}"

echo "INSTALL=swarm-commander repo=${REPO_ROOT}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "FAIL=python3_missing" >&2
  exit 1
fi

python3 -m venv "${VENV}"
"${VENV}/bin/pip" install --upgrade pip wheel
"${VENV}/bin/pip" install -r "${DEPLOY_DIR}/requirements-headless.txt"
"${VENV}/bin/pip" install -e "${REPO_ROOT}" 2>/dev/null || true

# Optional dev/test deps for healthcheck pytest on VPS
if [[ "${INSTALL_DEV:-0}" == "1" ]]; then
  "${VENV}/bin/pip" install pytest
fi

echo "ENV_DOC=${ENV_FILE}"
echo "ENV_TEMPLATE=${ENV_EXAMPLE}"
sudo mkdir -p "$(dirname "${ENV_FILE}")"
if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Copy secrets template: sudo cp ${ENV_EXAMPLE} ${ENV_FILE} && sudo chmod 600 ${ENV_FILE}"
  echo "Fill from Bitwarden — install will not start the bot."
else
  echo "External env exists: ${ENV_FILE}"
fi

if id "${RUN_USER}" >/dev/null 2>&1; then
  sudo cp "${DEPLOY_DIR}/systemd/${SERVICE_NAME}" "/etc/systemd/system/${SERVICE_NAME}"
  sudo sed -i "s|/opt/dreamos/repos/agent-tools|${REPO_ROOT}|g" "/etc/systemd/system/${SERVICE_NAME}"
  sudo sed -i "s|User=dreamos|User=${RUN_USER}|g" "/etc/systemd/system/${SERVICE_NAME}"
  sudo sed -i "s|Group=dreamos|Group=${RUN_USER}|g" "/etc/systemd/system/${SERVICE_NAME}"
  sudo systemctl daemon-reload
  sudo systemctl enable "${SERVICE_NAME}"
  echo "SYSTEMD=installed unit=${SERVICE_NAME}"
else
  echo "SKIP=systemd user ${RUN_USER} not found — install unit manually from ${DEPLOY_DIR}/systemd/"
fi

bash "${SCRIPT_DIR}/healthcheck.sh"

if [[ -f "${ENV_FILE}" ]] && grep -q '^DISCORD_BOT_TOKEN=[^[:space:]]' "${ENV_FILE}"; then
  echo "SECRETS=present — start with: sudo systemctl start ${SERVICE_NAME}"
else
  echo "SECRETS=missing — bot not started (expected on first install)"
  exit 0
fi

if systemctl is-enabled "${SERVICE_NAME}" >/dev/null 2>&1; then
  sudo systemctl start "${SERVICE_NAME}" || true
fi
echo "INSTALL=PASS"
