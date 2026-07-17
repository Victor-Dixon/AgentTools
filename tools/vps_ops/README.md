# VPS Ops (AgentTools)

Reusable DreamOS Hostinger VPS (`dreamos@2.25.64.233`) operator tools promoted out of home-directory one-shots.

## Tools

| Script | Purpose |
|--------|---------|
| `organize_vps_secrets_001.sh` | Archive `*.bak.*` / `*.save` / `*.old` under `~/secrets`, enforce mode 600 |
| `set_vps_envs_001.sh` | Bootstrap/rotate operator auth for signal-to-lead + discord fleet env files |
| `install_aws_cli_v2_user_001.sh` | User-local AWS CLI v2 install |
| `fix_dreamos_ssh_login_001.sh` | Repair dreamos authorized_keys / sshd login path |
| `vps_dreamos_github_key_001.sh` | Bootstrap GitHub deploy key for dreamos user |
| `vps_discord_token_doctor_001.py` | Verify Discord bot tokens in secrets (never prints token values) |
| `vps_discord_logic_audit_001.py` | Read-only Discord fleet logic/source inventory |
| `vps_day3_runner_bootstrap.sh` | Day-3 VPS runner bootstrap |
| `vps_home_hygiene_001.sh` | Classify + clean home litter (tarballs, CR ghosts, oneshot probes) |

## Canonical paths

- DreamVault governance SSOT: `~/projects/DreamVault`
- AgentTools on VPS: `~/projects/agent-tools`
- Secrets: `~/secrets/*.env` (chmod 600)
- Do **not** leave installers or probes in `$HOME` — run from this package or DreamVault `runtime/scripts/`

## Usage (on VPS)

```bash
cd ~/projects/agent-tools/tools/vps_ops
bash organize_vps_secrets_001.sh
python3 vps_discord_token_doctor_001.py
bash vps_home_hygiene_001.sh   # destructive litter cleanup; review script first
```

Trading-specific nginx/alpaca helpers live in DreamVault:

- `runtime/scripts/trading/install_dreamtrade_exact_nginx_routes.sh`
- `runtime/scripts/trading/vps_check_alpaca_ready.sh`
