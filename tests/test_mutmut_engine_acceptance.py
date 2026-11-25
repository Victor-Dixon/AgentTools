"""Opt-in real engine acceptance; no production activation."""
import os
import subprocess
import sys

import pytest


@pytest.mark.skipif(os.environ.get("AGENTTOOLS_MUTMUT_ACCEPTANCE") != "1",
                    reason="requires isolated mutmut 2.4.5 environment")
def test_real_mutmut_engine(tmp_path):
    from importlib.metadata import version
    from tools_v2.categories.testing_tools import evaluate_mutation_counts
    import xml.etree.ElementTree as ET

    assert version("mutmut") == "2.4.5"
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "__init__.py").touch()
    (tmp_path / "src" / "sample.py").write_text(
        "def add(a, b):\n    return a + b\n\ndef unused():\n    return 42\n")
    (tmp_path / "tests" / "test_sample.py").write_text(
        "from src.sample import add\n\ndef test_add():\n    assert add(2, 3) == 5\n")
    def run(*args):
        return subprocess.run(args, cwd=tmp_path, capture_output=True,
                              text=True, timeout=120, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    # Avoid stale bytecode when mutmut rewrites source within the same second.
    baseline = run(sys.executable, "-B", "-m", "pytest", "-q")
    assert baseline.returncode == 0, baseline.stdout + baseline.stderr
    result = run("mutmut", "run", "--paths-to-mutate", "src",
                 "--tests-dir", "tests", "--runner", sys.executable + " -B -m pytest -q")
    assert result.returncode in (0, 2), result.stdout + result.stderr
    report = run("mutmut", "junitxml")
    assert report.returncode == 0, report.stderr
    root = ET.fromstring(report.stdout)
    cases = list(root.iter("testcase"))
    assert cases
    assert any(case.find("failure") is not None for case in cases), report.stdout
    assert any(case.find("failure") is None and case.find("error") is None and case.find("skipped") is None for case in cases), report.stdout
    counts = {"killed": 0, "survived": 0, "timeout": 0}
    for case in cases:
        failure = case.find("failure")
        assert case.find("error") is None and case.find("skipped") is None
        if failure is None:
            counts["killed"] += 1
        else:
            assert failure.get("message") == "bad_survived"
            counts["survived"] += 1
    assert counts == {"killed": 1, "survived": 1, "timeout": 0}
    assert evaluate_mutation_counts(counts, 50).success
    assert not evaluate_mutation_counts(counts, 51).success
    print("MUTMUT_REAL_REPORT=" + report.stdout)
    print("MUTMUT_THRESHOLD_ACCEPTANCE=PASS")
