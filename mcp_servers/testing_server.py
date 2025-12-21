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
    """MCP server main loop."""
    print(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "initialize",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "run_coverage_analysis": {
                                "description": "Run tests with coverage analysis",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "path": {
                                            "type": "string",
                                            "default": "tests/",
                                            "description": "Path to run tests on",
                                        },
                                        "html": {
                                            "type": "boolean",
                                            "default": False,
                                            "description": "Generate HTML report",
                                        },
                                        "min_coverage": {
                                            "type": "integer",
                                            "default": 85,
                                            "description": "Minimum coverage percentage",
                                        },
                                    },
                                },
                            },
                            "run_mutation_tests": {
                                "description": "Run mutation testing quality gate",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "threshold": {
                                            "type": "integer",
                                            "default": 80,
                                            "description": "Minimum mutation score threshold",
                                        },
                                    },
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "testing-server", "version": "1.0.0"},
                },
            }
        )
    )

    # Handle tool calls
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "run_coverage_analysis":
                    result = run_coverage_analysis(**arguments)
                elif tool_name == "run_mutation_tests":
                    result = run_mutation_tests(**arguments)
                else:
                    result = {"success": False,
                              "error": f"Unknown tool: {tool_name}"}

                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
                        }
                    )
                )
        except Exception as e:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32603, "message": str(e)},
                    }
                )
            )


if __name__ == "__main__":
    main()
