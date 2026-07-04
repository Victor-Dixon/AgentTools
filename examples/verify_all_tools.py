#!/usr/bin/env python3
"""Verify every toolbelt registry entry responds to --help with exit code 0."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.toolbelt_registry import TOOLS_REGISTRY  # noqa: E402


def verify_all_tools() -> int:
    print("Verifying All Tools in Registry")
    print("================================")
    env = dict(**__import__("os").environ)
    env["PYTHONPATH"] = str(ROOT) + __import__("os").pathsep + env.get("PYTHONPATH", "")

    passed = 0
    failed: list[str] = []

    for tool_id, config in TOOLS_REGISTRY.items():
        flag = config["flags"][0]
        args = ["--warn-only"] if tool_id == "security-scan" else ["--help"]
        cmd = [sys.executable, "-m", "tools.toolbelt", flag, *args]
        result = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  OK  {tool_id}")
            passed += 1
        else:
            print(f"  FAIL {tool_id} (exit {result.returncode})")
            err = (result.stderr or result.stdout or "").strip().splitlines()
            failed.append(f"{tool_id}: {err[0] if err else 'unknown'}")
            print(f"       {failed[-1]}")

    total = len(TOOLS_REGISTRY)
    print("\nSummary")
    print(f"  Total:  {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {len(failed)}")
    if failed:
        for line in failed:
            print(f"    - {line}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(verify_all_tools())
