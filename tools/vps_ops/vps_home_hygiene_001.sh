#!/usr/bin/env bash
# VPS home cleanup — inventory + safe delete of one-time litter.
# Operator-authorized: organize VPS, delete one-time scripts/tarballs.
set -euo pipefail

HOME_DIR="${HOME}"
ARCHIVE_ROOT="${HOME_DIR}/.dreamos/archive/home_cleanup_20260717"
REPORT="${HOME_DIR}/.dreamos/archive/home_cleanup_20260717/cleanup_report.json"
mkdir -p "${ARCHIVE_ROOT}/promoted_staging" "${ARCHIVE_ROOT}/deleted_log"

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "VPS_HOME_CLEANUP start=${ts}"

# --- classify helpers ---
log_action() {
  printf '%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" | tee -a "${ARCHIVE_ROOT}/deleted_log/actions.tsv"
}

# Phase A: remove empty + CR-ghost dirs + stale install tarballs (projects already present)
SAFE_DELETE=(
  "${HOME_DIR}/install_smm.sh"
  "${HOME_DIR}/deploy_candidates_001.txt"
  "${HOME_DIR}/discord_fleet_inv.exit"
  "${HOME_DIR}/discord_fleet_inv.log"
  "${HOME_DIR}/discord_fleet_vps_inventory.status"
  "${HOME_DIR}/dreamtrade_market_nginx_route_install_20260715T231830Z.log"
  "${HOME_DIR}/smm_install.log"
  "${HOME_DIR}/fleet_git_status.txt"
  "${HOME_DIR}/fleet_live_vs_git.diff"
  "${HOME_DIR}/fleet_p1_fix.log"
  "${HOME_DIR}/fleet_p1_verify.log"
  "${HOME_DIR}/lead_intake_public_canary_001.json"
  "${HOME_DIR}/vps_coding_agent_readiness_20260710_023409.md"
  "${HOME_DIR}/weghachi_docker_demo_proof_vps_20260702.txt"
  "${HOME_DIR}/social_media_manager_compose.yml"
  "${HOME_DIR}/social_media_manager_requirements_vps.txt"
  "${HOME_DIR}/signal_to_lead_intake_requirements_vps.txt"
)

# Stale tarballs — canonical trees live under ~/projects
SAFE_DELETE_TGZ=(
  "${HOME_DIR}/socialmediamanager.tgz"
  "${HOME_DIR}/socialmediamanager_git.tgz"
  "${HOME_DIR}/agent-tools-vps.tgz"
  "${HOME_DIR}/dreamvault-discord-fleet.tgz"
  "${HOME_DIR}/signal-to-lead-intake.tgz"
  "${HOME_DIR}/weghachi_demo.tgz"
  "${HOME_DIR}/twitch_bots_vps.tgz"
  "${HOME_DIR}/vps_paper_discord_lane.tgz"
  "${HOME_DIR}/discord_fleet_vps_inventory.tgz"
)

# One-shot probe scripts (already executed; not reusable systems)
ONESHOT_SCRIPTS=(
  "${HOME_DIR}/aws_staging_deploy_probe_001.sh"
  "${HOME_DIR}/find_alamoiq_deploy_surface_001.sh"
  "${HOME_DIR}/inspect_weghachi_deploy_path_001.sh"
  "${HOME_DIR}/weghachi_docker_surface_probe_001.sh"
  "${HOME_DIR}/weghachi_recover_surface_002.sh"
  "${HOME_DIR}/vps_day2_proof.sh"
  "${HOME_DIR}/vps_marketing_operator_smoke.sh"
  "${HOME_DIR}/vps_marketing_preview_smoke.sh"
  "${HOME_DIR}/vps_operator_token_401_probe_001.py"
  "${HOME_DIR}/vps_reentry_audit_003_remote.sh"
)

# Home copies of DreamVault SSOT installers (canonical under ~/projects/DreamVault/runtime/scripts)
DV_COPIES=(
  "${HOME_DIR}/audit_vps_dreamtrade_data_001.sh"
  "${HOME_DIR}/bootstrap_vps_secrets_templates_001.sh"
  "${HOME_DIR}/deploy_dreamos_agent_gateway_nginx_vps_001.sh"
  "${HOME_DIR}/discord_fleet_vps_inventory_001.sh"
  "${HOME_DIR}/fill_signal_intake_empty_secrets_vps_001.py"
  "${HOME_DIR}/install_signal_to_lead_intake_vps_001.sh"
  "${HOME_DIR}/install_social_media_manager_vps_001.sh"
  "${HOME_DIR}/install_swarm_commander_vps_001.sh"
  "${HOME_DIR}/install_vps_discord_bot_fleet_001.sh"
  "${HOME_DIR}/install_vps_paper_discord_services_001.sh"
  "${HOME_DIR}/run_signal_to_lead_canary_vps_001.sh"
)

# Promote candidates — stage copies before deleting home copies of unique tools
PROMOTE=(
  "${HOME_DIR}/organize_vps_secrets_001.sh"
  "${HOME_DIR}/set_vps_envs_001.sh"
  "${HOME_DIR}/install_aws_cli_v2_user_001.sh"
  "${HOME_DIR}/install_ollama_cpu_model_001.sh"
  "${HOME_DIR}/install_dreamtrade_exact_nginx_routes.sh"
  "${HOME_DIR}/fix_dreamos_ssh_login_001.sh"
  "${HOME_DIR}/vps_dreamos_github_key_001.sh"
  "${HOME_DIR}/vps_check_alpaca_ready.sh"
  "${HOME_DIR}/vps_day3_runner_bootstrap.sh"
  "${HOME_DIR}/vps_discord_token_doctor_001.py"
  "${HOME_DIR}/vps_discord_logic_audit_001.py"
)

deleted=0
bytes_freed=0
promoted=0

size_of() {
  if [ -e "$1" ]; then
    du -sb "$1" 2>/dev/null | awk '{print $1}'
  else
    echo 0
  fi
}

safe_rm() {
  local path="$1"
  local reason="$2"
  if [ ! -e "$path" ] && [ ! -L "$path" ]; then
    return 0
  fi
  # Never touch secrets, projects, .ssh, .dreamos itself, bin, runtime
  case "$path" in
    */secrets*|*/projects/*|*/.ssh*|*/.dreamos/*|*/bin/*|*/runtime/*) 
      log_action "SKIP_PROTECTED" "$path"
      return 0
      ;;
  esac
  local sz
  sz=$(size_of "$path")
  rm -rf -- "$path"
  log_action "DELETE:${reason}" "$path (${sz} bytes)"
  deleted=$((deleted + 1))
  bytes_freed=$((bytes_freed + sz))
}

echo "=== Phase 0: stage promote candidates ==="
for f in "${PROMOTE[@]}"; do
  if [ -f "$f" ]; then
    cp -a "$f" "${ARCHIVE_ROOT}/promoted_staging/"
    promoted=$((promoted + 1))
    log_action "STAGE_PROMOTE" "$f"
  fi
done

echo "=== Phase 1: empty/logs/status litter ==="
for f in "${SAFE_DELETE[@]}"; do
  safe_rm "$f" "litter"
done

echo "=== Phase 2: stale install tarballs ==="
# Guard: only delete tarball if matching project dir exists
if [ -d "${HOME_DIR}/projects/socialmediamanager" ]; then
  safe_rm "${HOME_DIR}/socialmediamanager.tgz" "stale_tarball"
  safe_rm "${HOME_DIR}/socialmediamanager_git.tgz" "stale_tarball"
fi
if [ -d "${HOME_DIR}/projects/agent-tools" ]; then
  safe_rm "${HOME_DIR}/agent-tools-vps.tgz" "stale_tarball"
fi
if [ -d "${HOME_DIR}/projects/DreamVault" ]; then
  safe_rm "${HOME_DIR}/dreamvault-discord-fleet.tgz" "stale_tarball"
  safe_rm "${HOME_DIR}/vps_paper_discord_lane.tgz" "stale_tarball"
fi
safe_rm "${HOME_DIR}/signal-to-lead-intake.tgz" "stale_tarball"
safe_rm "${HOME_DIR}/weghachi_demo.tgz" "stale_tarball"
safe_rm "${HOME_DIR}/twitch_bots_tgz" "stale_tarball" 2>/dev/null || true
safe_rm "${HOME_DIR}/twitch_bots_vps.tgz" "stale_tarball"
safe_rm "${HOME_DIR}/discord_fleet_vps_inventory.tgz" "stale_tarball"

echo "=== Phase 3: CR-ghost directories ==="
# projects\r and discord_fleet_vps_inventory\r created by Windows line endings
python3 - <<'PY'
import os, shutil
from pathlib import Path
home = Path.home()
archive = home / ".dreamos/archive/home_cleanup_20260717/deleted_log/actions.tsv"
for name in os.listdir(home):
    if name.endswith("\r") or "\r" in name:
        p = home / name
        # only remove known ghosts
        base = name.replace("\r", "")
        if base in ("projects", "discord_fleet_vps_inventory"):
            # if real counterpart exists, remove ghost
            if (home / base).exists() or base == "discord_fleet_vps_inventory":
                sz = sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) if p.is_dir() else p.stat().st_size
                shutil.rmtree(p) if p.is_dir() else p.unlink()
                with archive.open("a", encoding="utf-8") as fh:
                    fh.write(f"DELETE:cr_ghost\t{p!s} ({sz} bytes)\n")
                print(f"REMOVED_CR_GHOST {p!s} bytes={sz}")
PY

echo "=== Phase 4: one-shot probes ==="
for f in "${ONESHOT_SCRIPTS[@]}"; do
  safe_rm "$f" "oneshot_probe"
done

echo "=== Phase 5: DreamVault SSOT home copies (keep projects tree) ==="
for f in "${DV_COPIES[@]}"; do
  base=$(basename "$f")
  if find "${HOME_DIR}/projects/DreamVault/runtime/scripts" -name "$base" 2>/dev/null | grep -q .; then
    safe_rm "$f" "dv_ssot_copy"
  else
    # stage then keep? stage to promote if missing from DV
    if [ -f "$f" ]; then
      cp -a "$f" "${ARCHIVE_ROOT}/promoted_staging/"
      log_action "STAGE_MISSING_FROM_DV" "$f"
      safe_rm "$f" "staged_then_remove_home"
    fi
  fi
done

echo "=== Phase 6: promote-staged unique tools — remove from home after staging ==="
for f in "${PROMOTE[@]}"; do
  if [ -f "$f" ]; then
    safe_rm "$f" "promoted_staged"
  fi
done

echo "=== Phase 7: large one-time inventory dumps ==="
# Keep a tiny summary; remove 600MB inventory + 122MB audit dump
if [ -d "${HOME_DIR}/discord_fleet_vps_inventory" ]; then
  # Keep meta.txt + systemd_inventory.txt as tiny evidence; nuke the rest
  mkdir -p "${ARCHIVE_ROOT}/discord_fleet_inventory_keep"
  for keep in meta.txt systemd_inventory.txt cron_inventory.txt secret_surface.txt; do
    if [ -f "${HOME_DIR}/discord_fleet_vps_inventory/${keep}" ]; then
      cp -a "${HOME_DIR}/discord_fleet_vps_inventory/${keep}" "${ARCHIVE_ROOT}/discord_fleet_inventory_keep/"
    fi
  done
  safe_rm "${HOME_DIR}/discord_fleet_vps_inventory" "oneshot_inventory_dump"
fi
if [ -d "${HOME_DIR}/audits" ]; then
  safe_rm "${HOME_DIR}/audits" "oneshot_audit_dump"
fi

# leftover deploy scratch dirs that are not services
safe_rm "${HOME_DIR}/coding-agent-lab" "oneshot_lab"
safe_rm "${HOME_DIR}/dream_twitch_council_deploy" "deploy_scratch"
# dreamos_discord_fleet_setup — check if still referenced
if [ -d "${HOME_DIR}/dreamos_discord_fleet_setup" ]; then
  # keep if systemd unit ExecStart references it
  if systemctl --user cat dreamos-discord-commander.service 2>/dev/null | grep -q dreamos_discord_fleet_setup; then
    log_action "KEEP_SERVICE_REF" "${HOME_DIR}/dreamos_discord_fleet_setup"
  else
    safe_rm "${HOME_DIR}/dreamos_discord_fleet_setup" "setup_scratch"
  fi
fi

echo "=== Post-clean home top ==="
ls -lah "${HOME_DIR}" | head -60
echo
du -sh "${HOME_DIR}"/* 2>/dev/null | sort -hr | head -25 || true
echo
echo "DELETED_COUNT=${deleted}"
echo "BYTES_FREED=${bytes_freed}"
echo "PROMOTED_STAGED=${promoted}"
echo "ARCHIVE=${ARCHIVE_ROOT}"
printf '{"ts":"%s","deleted":%s,"bytes_freed":%s,"promoted_staged":%s,"archive":"%s"}\n' \
  "$ts" "$deleted" "$bytes_freed" "$promoted" "$ARCHIVE_ROOT" > "$REPORT"
echo "REPORT=${REPORT}"
echo "VPS_HOME_CLEANUP=PASS"
