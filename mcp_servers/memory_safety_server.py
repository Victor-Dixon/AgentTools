#!/usr/bin/env python3
"""
MCP Server for Memory Safety Tools
Exposes memory leak detection and resource verification via Model Context Protocol
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root and tools folders to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tools_v2"))

try:
    from tools_v2.categories.memory_safety_tools import (
        detect_memory_leaks,
        verify_files_exist,
        scan_unbounded_structures,
        validate_imports,
        check_file_handles
    )
    HAS_TOOLS = True
except ImportError:
    HAS_TOOLS = False


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
                            "detect_memory_leaks": {
                                "description": "Detect potential memory leaks (unbounded structures, missing size checks)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "target_path": {
                                            "type": "string",
                                            "default": "src",
                                            "description": "Directory to scan (default: src)",
                                        },
                                    },
                                },
                            },
                            "verify_files_exist": {
                                "description": "Verify files exist before task assignment",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "file_list": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "List of file paths to verify",
                                        },
                                    },
                                    "required": ["file_list"],
                                },
                            },
                            "scan_unbounded_structures": {
                                "description": "Scan for unbounded data structures that could grow indefinitely",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "target_path": {
                                            "type": "string",
                                            "default": "src",
                                            "description": "Directory to scan",
                                        },
                                    },
                                },
                            },
                            "validate_imports": {
                                "description": "Validate Python file imports work correctly",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "file_path": {
                                            "type": "string",
                                            "description": "Path to Python file to validate",
                                        },
                                    },
                                    "required": ["file_path"],
                                },
                            },
                            "check_file_handles": {
                                "description": "Check for unclosed file handles (resource leak detection)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "target_path": {
                                            "type": "string",
                                            "default": "src",
                                            "description": "Directory to scan",
                                        },
                                    },
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "memory-safety-server", "version": "1.0.0"},
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
                result = {"success": False, "error": "Unknown tool"}

                if not HAS_TOOLS:
                    result = {"success": False, "error": "Memory safety tools not available"}
                else:
                    try:
                        if tool_name == "detect_memory_leaks":
                            result = detect_memory_leaks(**arguments)
                        elif tool_name == "verify_files_exist":
                            result = verify_files_exist(**arguments)
                        elif tool_name == "scan_unbounded_structures":
                            result = scan_unbounded_structures(**arguments)
                        elif tool_name == "validate_imports":
                            result = validate_imports(**arguments)
                        elif tool_name == "check_file_handles":
                            result = check_file_handles(**arguments)
                    except Exception as e:
                        result = {"success": False, "error": str(e)}

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
