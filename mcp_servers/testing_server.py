#!/usr/bin/env python3
"""
MCP Server for Testing Tools
Exposes testing and coverage capabilities via Model Context Protocol
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root and tools folders to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tools_v2"))

try:
    from tools_v2.categories.testing_tools import CoverageReportTool, MutationGateTool
    HAS_TOOLS = True
except ImportError:
    HAS_TOOLS = False


def run_coverage_analysis(
    path: str = "tests/", html: bool = False, min_coverage: int = 85
) -> Dict[str, Any]:
    """Run test coverage analysis."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Testing tools not available"}

    try:
        tool = CoverageReportTool()
        result = tool.execute({
            "path": path,
            "html": html,
            "min_coverage": min_coverage
        })
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_mutation_tests(threshold: int = 80) -> Dict[str, Any]:
    """Run mutation testing quality gate."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Testing tools not available"}

    try:
        tool = MutationGateTool()
        result = tool.execute({"threshold": threshold})
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


# MCP Server Protocol
def main():
    """Serve local stdio MCP requests; no remote execution authority."""
    tools = [{
        "name": "run_coverage_analysis",
        "description": "Run tests with coverage analysis",
        "inputSchema": {"type": "object", "additionalProperties": False,
                        "properties": {"path": {"type": "string", "default": "tests/"},
                                       "html": {"type": "boolean", "default": False},
                                       "min_coverage": {"type": "integer", "minimum": 0, "maximum": 100, "default": 85}}}
    }] if HAS_TOOLS else []
    for line in sys.stdin:
        request_id = None
        try:
            request = json.loads(line)
            if not isinstance(request, dict):
                raise ValueError("Invalid request")
            request_id = request.get("id")
            method = request.get("method")
            if "id" not in request:
                continue
            params = request.get("params", {})
            if method == "initialize":
                result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                          "serverInfo": {"name": "testing-server", "version": "1.0.0"}}
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": tools}
            elif method == "tools/call":
                if params.get("name") != "run_coverage_analysis" or not HAS_TOOLS:
                    raise ValueError("Unknown or unavailable tool")
                arguments = params.get("arguments", {})
                if not isinstance(arguments, dict) or set(arguments) - {"path", "html", "min_coverage"}:
                    raise ValueError("Invalid arguments")
                outcome = run_coverage_analysis(**arguments)
                result = {"content": [{"type": "text", "text": json.dumps(outcome)}],
                          "isError": not outcome.get("success", False)}
            else:
                print(json.dumps({"jsonrpc": "2.0", "id": request_id,
                                  "error": {"code": -32601, "message": "Method not found"}}), flush=True)
                continue
            print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)
        except (ValueError, TypeError, AttributeError) as exc:
            print(json.dumps({"jsonrpc": "2.0", "id": request_id,
                              "error": {"code": -32602, "message": str(exc)}}), flush=True)


if __name__ == "__main__":
    main()
