#!/usr/bin/env bash
# Dry-run a deploy request: validate safety rules and print planned commands only.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRIDGE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${BRIDGE_DIR}/../.." && pwd)"

REQUEST_FILE="${1:-}"
if [[ -z "${REQUEST_FILE}" ]]; then
  echo "Usage: $0 <deploy_request.json>" >&2
  exit 1
fi

export DREAMOS_DEPLOY_MODE="${DREAMOS_DEPLOY_MODE:-dry_run}"

python "${BRIDGE_DIR}/vps_deploy_bridge.py" "${REQUEST_FILE}" --repo-root "${REPO_ROOT}"
