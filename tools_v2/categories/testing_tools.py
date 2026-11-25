"""
Testing Tools
=============

Tool adapters for testing and coverage operations.

V2 Compliance: <180 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import subprocess
import sys
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec



class CoverageReportTool(IToolAdapter):
    """Generate test coverage report."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="test.coverage",
            version="1.0.0",
            category="testing",
            summary="Run tests with coverage analysis",
            required_params=[],
            optional_params={"path": "tests/", "html": False, "min_coverage": 85},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        path = params.get("path", "tests/")
        threshold = params.get("min_coverage", 85)
        if not isinstance(path, str) or not path or path.startswith("-"):
            errors.append("path")
        else:
            candidate = Path(path)
            try:
                if candidate.is_absolute() or ".." in candidate.parts or not candidate.resolve().is_relative_to(Path.cwd().resolve()) or not candidate.exists():
                    errors.append("path")
            except (OSError, ValueError):
                errors.append("path")
        if type(threshold) is not int or not 0 <= threshold <= 100:
            errors.append("min_coverage")
        if type(params.get("html", False)) is not bool:
            errors.append("html")
        return not errors, errors

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        valid, errors = self.validate(params)
        if not valid:
            return ToolResult(success=False, output=None, exit_code=2, error_message="Invalid parameters: " + ", ".join(errors))
        cmd = [sys.executable, "-m", "pytest", "--cov=.", "--cov-report=term", f"--cov-fail-under={params.get('min_coverage', 85)}"]
        if params.get("html"):
            cmd.append("--cov-report=html")
        cmd.extend(["--", params.get("path", "tests/")])
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return ToolResult(success=result.returncode == 0, output=result.stdout,
                              exit_code=result.returncode,
                              error_message=(result.stderr or result.stdout) if result.returncode else None)
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, output=None, exit_code=124, error_message="Coverage execution timed out")
        except OSError as exc:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(exc))


class MutationGateTool(IToolAdapter):
    """Run mutation testing gate."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="test.mutation",
            version="1.0.0",
            category="testing",
            summary="Mutation testing gate (backend unavailable)",
            required_params=[],
            optional_params={"threshold": 80},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        threshold = params.get("threshold", 80)
        valid = type(threshold) is int and 0 <= threshold <= 100
        return valid, [] if valid else ["threshold"]

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        valid, errors = self.validate(params)
        if not valid:
            return ToolResult(success=False, output=None, exit_code=2,
                              error_message="Invalid parameters: " + ", ".join(errors))
        return ToolResult(success=False, output=None, exit_code=69,
                          error_message="Mutation backend unavailable: no verified engine configured")
