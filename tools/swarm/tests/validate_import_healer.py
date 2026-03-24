#!/usr/bin/env python3
"""Validation script for import_healer confidence-based rewrites."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def run_validation() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    script = repo_root / "tools/swarm/agents/import_healer.py"
    fixtures = repo_root / "tools/swarm/tests/fixtures"

    with TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        target = tmp / "broken_imports.py"
        target.write_text((fixtures / "broken_imports.py").read_text(encoding="utf-8"), encoding="utf-8")

        command = [
            sys.executable,
            str(script),
            str(target),
            "--module-root",
            str(fixtures / "modules"),
            "--rewrite-map",
            str(fixtures / "rewrite_map.json"),
            "--apply",
        ]
        completed = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, check=True)
        data = json.loads(completed.stdout)

        result = data["results"][0]
        rewrite_confidences = {item["original"]: item["confidence"] for item in result["rewrites"]}
        assert rewrite_confidences.get("legacy.helpers") == "high"
        assert rewrite_confidences.get("helpers") == "medium"
        assert result["compile_ok"] is True

        skipped = {item["original"]: item["confidence"] for item in result["skipped"]}
        assert skipped.get("config") == "none"

        rewritten_text = target.read_text(encoding="utf-8")
        assert "import pkg_alpha.helpers as legacy_helpers" in rewritten_text
        assert "import pkg_alpha.helpers" in rewritten_text
        assert "import config" in rewritten_text

    print("import_healer validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_validation())
