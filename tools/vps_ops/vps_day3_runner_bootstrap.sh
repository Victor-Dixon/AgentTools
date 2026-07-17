#!/usr/bin/env bash
set -euo pipefail

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT_DIR="$HOME/runtime/reports"
REPORT="$REPORT_DIR/vps_day3_runner_bootstrap_${STAMP}.md"
LATEST="$REPORT_DIR/vps_day3_latest.md"

mkdir -p "$REPORT_DIR" "$HOME/projects" "$HOME/runtime/manifests" "$HOME/bin"

pass(){ echo "VERIFY=PASS_$1"; }
fail(){ echo "VERIFY=FAIL_$1 :: $2"; }
section(){ echo ""; echo "## $1"; echo ""; }

{
echo "# VPS Day 3 Runner Bootstrap"
echo ""
echo "generated_utc=$STAMP"
echo "user=$(whoami)"
echo "home=$HOME"
echo ""

section "Preflight"
hostnamectl 2>/dev/null || true
whoami
id
df -h /
free -h || true
docker --version || true
git --version || true
python3 --version || true

section "Install Missing Tooling"
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  git \
  curl \
  jq \
  gh \
  nodejs \
  npm \
  docker-compose-plugin

section "Toolchain Verify"
for cmd in git gh python3 pip3 node npm docker systemctl ss curl jq; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd=$($cmd --version 2>&1 | head -n 1)"
    pass "CMD_${cmd^^}"
  else
    fail "CMD_${cmd^^}" "missing"
  fi
done

if docker compose version >/dev/null 2>&1; then
  echo "docker_compose=$(docker compose version)"
  pass DOCKER_COMPOSE_PLUGIN
else
  fail DOCKER_COMPOSE_PLUGIN "docker compose plugin unavailable"
fi

section "Clone Canonical Repos"
cd "$HOME/projects"

clone_or_update() {
  local name="$1"
  local repo="$2"

  if [ -d "$name/.git" ]; then
    echo "repo=$name action=fetch"
    git -C "$name" fetch --all --prune
    git -C "$name" status -sb
    pass "REPO_${name^^}_EXISTS"
  else
    echo "repo=$name action=clone"
    git clone "$repo" "$name"
    git -C "$name" status -sb
    pass "REPO_${name^^}_CLONED"
  fi
}

clone_or_update "DreamVault" "git@github.com:Victor-Dixon/DreamVault.git"
clone_or_update "websites" "git@github.com:Victor-Dixon/websites.git"

section "Write VPS Lane Manifest"
cat > "$HOME/runtime/manifests/vps_lane_manifest.yaml" << 'EOF'
id: dreamos_vps_lane_001
title: Dream.OS VPS Runner Lane
status: active_candidate
owner: dreamos
host_role: vps_runner
canonical_projects_dir: /home/dreamos/projects
runtime_dir: /home/dreamos/runtime
reports_dir: /home/dreamos/runtime/reports
repos:
  DreamVault:
    path: /home/dreamos/projects/DreamVault
    remote: git@github.com:Victor-Dixon/DreamVault.git
    role: canonical_runtime_and_tasks
  websites:
    path: /home/dreamos/projects/websites
    remote: git@github.com:Victor-Dixon/websites.git
    role: public_surface_and_deploy
day2_baseline:
  ssh_key_auth: pass
  git_ssh_access: pass
  docker: pass
  systemd: pass
day3_bootstrap:
  gh: required
  node_npm: required_for_website_builds
  docker_compose: required_for_stack_lanes
  proof_loop: required
closeout_rule:
  - every runner action writes a report
  - every report has VERIFY lines
  - no background claim without artifact
EOF

cat "$HOME/runtime/manifests/vps_lane_manifest.yaml"
pass VPS_LANE_MANIFEST_WRITTEN

section "Install Proof Loop"
cat > "$HOME/bin/dreamos_vps_proof_loop.sh" << 'EOF'
#!/usr/bin/env bash
set -u

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT_DIR="$HOME/runtime/reports/vps_proof_loop"
REPORT="$REPORT_DIR/proof_loop_${STAMP}.md"
LATEST="$REPORT_DIR/latest.md"

mkdir -p "$REPORT_DIR"

{
echo "# Dream.OS VPS Proof Loop"
echo ""
echo "generated_utc=$STAMP"
echo "user=$(whoami)"
echo "host=$(hostname)"
echo ""

echo "## Host"
uptime -p 2>/dev/null || uptime
df -h /
free -h || true

echo ""
echo "## Tools"
for cmd in git gh python3 node npm docker jq curl; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "VERIFY=PASS_CMD_${cmd^^}"
    "$cmd" --version 2>&1 | head -n 1
  else
    echo "VERIFY=FAIL_CMD_${cmd^^}"
  fi
done

echo ""
echo "## Docker"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || echo "VERIFY=FAIL_DOCKER_PS"

echo ""
echo "## Repos"
for repo in DreamVault websites; do
  if [ -d "$HOME/projects/$repo/.git" ]; then
    echo "VERIFY=PASS_REPO_${repo^^}"
    git -C "$HOME/projects/$repo" status -sb
    git -C "$HOME/projects/$repo" log -1 --oneline
  else
    echo "VERIFY=FAIL_REPO_${repo^^}"
  fi
done

echo ""
echo "## Manifest"
if [ -f "$HOME/runtime/manifests/vps_lane_manifest.yaml" ]; then
  echo "VERIFY=PASS_VPS_LANE_MANIFEST"
else
  echo "VERIFY=FAIL_VPS_LANE_MANIFEST"
fi

} | tee "$REPORT"

cp "$REPORT" "$LATEST"
echo "PROOF_LOOP_REPORT=$REPORT"
EOF

chmod +x "$HOME/bin/dreamos_vps_proof_loop.sh"

"$HOME/bin/dreamos_vps_proof_loop.sh"
pass PROOF_LOOP_RUN_ONCE

section "Install Systemd Timer"
sudo tee /etc/systemd/system/dreamos-vps-proof-loop.service >/dev/null << EOF
[Unit]
Description=Dream.OS VPS Proof Loop

[Service]
Type=oneshot
User=dreamos
WorkingDirectory=/home/dreamos
ExecStart=/home/dreamos/bin/dreamos_vps_proof_loop.sh
EOF

sudo tee /etc/systemd/system/dreamos-vps-proof-loop.timer >/dev/null << EOF
[Unit]
Description=Run Dream.OS VPS Proof Loop Hourly

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h
Persistent=true

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now dreamos-vps-proof-loop.timer

systemctl list-timers --all | grep dreamos-vps-proof-loop && pass SYSTEMD_TIMER_ENABLED || fail SYSTEMD_TIMER_ENABLED "timer not visible"

section "Final Verify"
test -d "$HOME/projects/DreamVault/.git" && pass DREAMVAULT_CLONED || fail DREAMVAULT_CLONED "missing"
test -d "$HOME/projects/websites/.git" && pass WEBSITES_CLONED || fail WEBSITES_CLONED "missing"
test -f "$HOME/runtime/manifests/vps_lane_manifest.yaml" && pass VPS_MANIFEST_EXISTS || fail VPS_MANIFEST_EXISTS "missing"
test -x "$HOME/bin/dreamos_vps_proof_loop.sh" && pass PROOF_LOOP_EXECUTABLE || fail PROOF_LOOP_EXECUTABLE "missing"
test -f "$HOME/runtime/reports/vps_proof_loop/latest.md" && pass PROOF_LOOP_LATEST_REPORT || fail PROOF_LOOP_LATEST_REPORT "missing"

} | tee "$REPORT"

cp "$REPORT" "$LATEST"

echo ""
echo "VPS_DAY3_REPORT=$REPORT"
echo "VPS_DAY3_LATEST=$LATEST"
echo ""
echo "VERIFY SUMMARY"
grep '^VERIFY=' "$REPORT" || true
