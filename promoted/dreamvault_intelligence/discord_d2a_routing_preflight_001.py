#!/usr/bin/env python3
"""Preflight gate for Discord D2A → PyAutoGUI routing (all quad agents).

Validates env, layout coords, processor lock, bus queue health, and stale
in-flight rows that block single_active_inject dispatch.

Usage:
  python runtime/scripts/discord_d2a_routing_preflight_001.py
  python runtime/scripts/discord_d2a_routing_preflight_001.py --auto-unblock-stale
  python runtime/scripts/discord_d2a_routing_preflight_001.py --json-out data/reports/coordination/discord_d2a_routing_preflight_latest.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dreamvault.agent_cellphone.coord_validation import (  # noqa: E402
    CoordValidationError,
    default_layout_mode,
    validate_before_send,
)
from dreamvault.agent_cellphone.delivery import ALLOW_LIVE_INJECTION_ENV  # noqa: E402
from dreamvault.message_bus.dispatcher import default_bus_paths  # noqa: E402
from dreamvault.runtime_bus import list_messages  # noqa: E402
from dreamvault.thea_agent_gas.transport import LEGACY_ROOT, resolve_agent_cellphone_root  # noqa: E402

FLEET = ("Agent-1", "Agent-2", "Agent-3", "Agent-4")
_UNBLOCK_SCRIPT = REPO_ROOT / "runtime" / "scripts" / "bus_stale_delivery_unblock_001.py"


def _load_unblock_helpers():
    import importlib.util

    spec = importlib.util.spec_from_file_location("bus_stale_delivery_unblock_001", _UNBLOCK_SCRIPT)
    if not spec or not spec.loader:
        raise RuntimeError(f"missing {_UNBLOCK_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.find_stale, mod.unblock


def _processor_running(ledger_dir: Path) -> tuple[bool, int | None]:
    lock = ledger_dir / "processor.lock"
    if not lock.is_file():
        return False, None
    try:
        pid = int(lock.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return False, None
    if pid <= 0:
        return False, pid
    if sys.platform == "win32":
        import ctypes

        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True, pid
        return False, pid
    try:
        os.kill(pid, 0)
        return True, pid
    except OSError:
        return False, pid


def run_preflight(*, repo_root: Path | None = None, auto_unblock_stale: bool = False, max_age_minutes: int = 30) -> dict:
    root = repo_root or REPO_ROOT
    os.environ.setdefault("AGENT_CELLPHONE_ROOT", str(LEGACY_ROOT))
    layout = default_layout_mode()
    acp_root = resolve_agent_cellphone_root()
    paths = default_bus_paths(root)

    find_stale, unblock = _load_unblock_helpers()
    stale_before = find_stale(paths.state_path, max_age_minutes=max_age_minutes)
    unblock_proof: dict | None = None
    if auto_unblock_stale and stale_before:
        unblock_proof = unblock(paths=paths, execute=True, max_age_minutes=max_age_minutes)
    stale_after = find_stale(paths.state_path, max_age_minutes=max_age_minutes)

    env_live = os.environ.get(ALLOW_LIVE_INJECTION_ENV, "").strip() == "1"
    env_layout = os.environ.get("AGENT_GAS_LAYOUT_MODE", "").strip() or layout

    agent_checks: list[dict] = []
    failures: list[str] = []
    for agent_id in FLEET:
        try:
            validate_before_send(acp_root, agent_id, layout_mode=layout)
            agent_checks.append({"agent_id": agent_id, "coords": "PASS"})
        except CoordValidationError as exc:
            agent_checks.append({"agent_id": agent_id, "coords": "FAIL", "detail": str(exc)})
            failures.append(f"{agent_id}: {exc}")

    processor_up, processor_pid = _processor_running(paths.ledger_dir)
    if not processor_up:
        failures.append("message bus processor not running (processor.lock missing or stale PID)")

    in_flight = sum(
        len(list_messages(state_path=paths.state_path, status=status))
        for status in ("claimed", "running", "delivered")
    )
    queued = len(list_messages(state_path=paths.state_path, status="queued"))

    if not env_live:
        failures.append(f"{ALLOW_LIVE_INJECTION_ENV} not set to 1")

    if stale_after:
        failures.append(
            f"stale in-flight bus rows={len(stale_after)} block dispatch "
            f"(run: python runtime/scripts/bus_stale_delivery_unblock_001.py --execute "
            f"or preflight --auto-unblock-stale)"
        )

    payload = {
        "schema": "dreamvault.discord_d2a_routing_preflight.v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "pass": not failures,
        "layout": layout,
        "env": {
            ALLOW_LIVE_INJECTION_ENV: env_live,
            "AGENT_GAS_LAYOUT_MODE": env_layout,
        },
        "agent_checks": agent_checks,
        "processor": {"running": processor_up, "pid": processor_pid},
        "bus": {
            "queued": queued,
            "in_flight": in_flight,
            "stale_in_flight": len(stale_after),
            "stale_cleared": len(stale_before) - len(stale_after) if auto_unblock_stale else 0,
        },
        "unblock": unblock_proof,
        "failures": failures,
        "verify_cmd": "python runtime/scripts/discord_d2a_routing_preflight_001.py",
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=REPO_ROOT / "data/reports/coordination/discord_d2a_routing_preflight_latest.json",
    )
    parser.add_argument(
        "--auto-unblock-stale",
        action="store_true",
        help="Clear stale claimed/running/delivered rows before checks",
    )
    parser.add_argument("--max-age-minutes", type=int, default=30, help="Stale in-flight threshold")
    args = parser.parse_args()

    proof = run_preflight(auto_unblock_stale=args.auto_unblock_stale, max_age_minutes=args.max_age_minutes)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")

    status = "PASS" if proof["pass"] else "FAIL"
    print(f"DISCORD_D2A_ROUTING_PREFLIGHT={status}")
    print(f"LAYOUT={proof['layout']} PROCESSOR={proof['processor']['running']} QUEUED={proof['bus']['queued']} STALE_IN_FLIGHT={proof['bus']['stale_in_flight']}")
    for row in proof["agent_checks"]:
        print(f"  {row['agent_id']}: {row['coords']}")
    if proof["failures"]:
        for item in proof["failures"]:
            print(f"  FAIL: {item}", file=sys.stderr)
    print(f"PROOF={args.json_out}")
    return 0 if proof["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
