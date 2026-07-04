#!/usr/bin/env bash
set -euo pipefail

if systemctl is-active --quiet swarm-commander.service 2>/dev/null; then
  sudo systemctl stop swarm-commander.service
  echo "STOP=systemd swarm-commander.service"
else
  echo "STOP=not_running"
fi
