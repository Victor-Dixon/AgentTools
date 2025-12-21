#!/usr/bin/env python3
"""
MCP Server for Observability Tools
Exposes metrics and system health monitoring via Model Context Protocol
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root and tools folders to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tools_v2"))

try:
    from tools_v2.categories.observability_tools import (
        MetricsSnapshotTool,
        MetricsTool,
        SystemHealthTool,
        SLOCheckTool
    )
    HAS_TOOLS = True
except ImportError:
    HAS_TOOLS = False


def get_metrics_snapshot() -> Dict[str, Any]:
    """Get current metrics snapshot."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Observability tools not available"}

    try:
        tool = MetricsSnapshotTool()
        # MetricsSnapshotTool doesn't require params, but execute expects a dict
        result = tool.execute({})
        # The execute method returns a dict directly in observability_tools.py (unlike testing_tools.py which returns ToolResult)
        # Wait, looking at observability_tools.py again:
        # It inherits from IToolAdapter.
        # But in the file content I saw earlier:
        # class MetricsSnapshotTool(IToolAdapter):
        #     def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        #         ... returns {"success": True ...}
        # It does NOT return ToolResult object, it returns a dict directly.
        # But IToolAdapter base class says it returns ToolResult.
        # This means observability_tools.py implementation might be slightly inconsistent with base class signature
        # or I misread the base class or the tool implementation.
        # Let's check observability_tools.py again.
        # It imports IToolAdapter but execute returns dict[str, Any].
        # So I should handle it as a dict.
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_metric(key: str) -> Dict[str, Any]:
    """Get specific metric value."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Observability tools not available"}

    try:
        tool = MetricsTool()
        result = tool.execute({"key": key})
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_system_health() -> Dict[str, Any]:
    """Check system health status."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Observability tools not available"}

    try:
        tool = SystemHealthTool()
        result = tool.execute({})
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_slo_compliance() -> Dict[str, Any]:
    """Check SLO compliance."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Observability tools not available"}

    try:
        tool = SLOCheckTool()
        result = tool.execute({})
        return result
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
                            "get_metrics_snapshot": {
                                "description": "Get current metrics snapshot",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                },
                            },
                            "get_metric": {
                                "description": "Get specific metric value",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "key": {
                                            "type": "string",
                                            "description": "Metric key to retrieve",
                                        },
                                    },
                                    "required": ["key"],
                                },
                            },
                            "check_system_health": {
                                "description": "Check system health status",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                },
                            },
                            "check_slo_compliance": {
                                "description": "Check SLO compliance",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "observability-server", "version": "1.0.0"},
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

                if tool_name == "get_metrics_snapshot":
                    result = get_metrics_snapshot()
                elif tool_name == "get_metric":
                    result = get_metric(**arguments)
                elif tool_name == "check_system_health":
                    result = check_system_health()
                elif tool_name == "check_slo_compliance":
                    result = check_slo_compliance()
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
