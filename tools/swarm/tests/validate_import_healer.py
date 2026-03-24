#!/usr/bin/env python3
"""Validation script for import_healer confidence-based rewrites."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.swarm.agents.import_healer import main as import_healer_main


def run_validation() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    fixtures = repo_root / "tools/swarm/tests/fixtures"

    with TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        target = tmp / "broken_imports.py"
        target.write_text((fixtures / "broken_imports.py").read_text(encoding="utf-8"), encoding="utf-8")

        capture = StringIO()
        with redirect_stdout(capture):
            exit_code = import_healer_main(
                [
                    str(target),
                    "--module-root",
                    str(fixtures / "modules"),
                    "--rewrite-map",
                    str(fixtures / "rewrite_map.json"),
                    "--apply",
                ]
            )

        assert exit_code == 0
        data = json.loads(capture.getvalue())

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
