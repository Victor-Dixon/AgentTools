#!/usr/bin/env bash
# Execute an approved deploy request after operator review.
# Requires DREAMOS_DEPLOY_MODE=execute and deploy request with "dry_run": false.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRIDGE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${BRIDGE_DIR}/../.." && pwd)"

REQUEST_FILE="${1:-}"
if [[ -z "${REQUEST_FILE}" ]]; then
  echo "Usage: $0 <deploy_request.json>" >&2
  exit 1
fi

export DREAMOS_DEPLOY_MODE=execute

python "${BRIDGE_DIR}/vps_deploy_bridge.py" "${REQUEST_FILE}" --repo-root "${REPO_ROOT}"
