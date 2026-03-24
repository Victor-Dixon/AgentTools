#!/usr/bin/env python3
"""Coverage non-regression gate for import healer tooling files (stdlib trace)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from trace import Trace, _find_executable_linenos
from typing import Dict

import pytest
import sys

TARGETS = [
    "tools/swarm/agents/import_healer.py",
    "tools/swarm/tests/validate_import_healer.py",
    "tools/swarm/tests/test_import_healer.py",
]


def to_relpath(path: Path, repo_root: Path) -> str:
    return str(path.resolve().relative_to(repo_root.resolve()))


def calculate_coverage(repo_root: Path) -> Dict[str, float]:
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    tracer = Trace(count=True, trace=False)
    exit_code = tracer.runfunc(pytest.main, ["-q", "tools/swarm/tests/test_import_healer.py"])
    if exit_code != 0:
        raise RuntimeError(f"pytest failed with exit code {exit_code}")

    counts = tracer.results().counts
    current: Dict[str, float] = {}
    for target in TARGETS:
        abs_target = (repo_root / target).resolve()
        executable = set(_find_executable_linenos(str(abs_target)).keys())
        executed = {
            line_no
            for (filename, line_no), hit_count in counts.items()
            if Path(filename).resolve() == abs_target and hit_count > 0
        }
        percent = (len(executed & executable) / len(executable) * 100.0) if executable else 100.0
        current[target] = round(percent, 2)
    return current


def load_baseline(path: Path) -> Dict[str, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    baseline = data.get("baseline_percent", {})
    if not isinstance(baseline, dict):
        raise ValueError("baseline_percent must be a JSON object")
    return {str(key): float(value) for key, value in baseline.items()}


def write_baseline(path: Path, current: Dict[str, float]) -> None:
    payload = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "method": "python trace module",
        "baseline_percent": current,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import healer coverage non-regression gate")
    parser.add_argument(
        "--baseline-file",
        type=Path,
        default=Path("tools/swarm/tests/import_healer_coverage_baseline.json"),
        help="Baseline coverage JSON file",
    )
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Write the current coverage values to the baseline file and exit",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    baseline_path = repo_root / args.baseline_file
    current = calculate_coverage(repo_root)

    if args.write_baseline:
        write_baseline(baseline_path, current)
        print(f"Baseline written to {to_relpath(baseline_path, repo_root)}")
        for target in TARGETS:
            print(f"- {target}: {current[target]:.2f}%")
        return 0

    baseline = load_baseline(baseline_path)
    regressions: list[str] = []

    print("Import healer coverage report")
    for target in TARGETS:
        observed = current.get(target, 0.0)
        expected = baseline.get(target)
        if expected is None:
            regressions.append(f"missing baseline for {target}")
            print(f"- {target}: current={observed:.2f}% baseline=missing")
            continue
        print(f"- {target}: current={observed:.2f}% baseline={expected:.2f}%")
        if observed + 1e-9 < expected:
            regressions.append(f"{target}: current={observed:.2f}% baseline={expected:.2f}%")

    if regressions:
        print("Coverage regression detected:")
        for item in regressions:
            print(f"  - {item}")
        return 1

    print("Coverage gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
