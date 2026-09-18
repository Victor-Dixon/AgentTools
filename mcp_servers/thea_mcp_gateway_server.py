#!/usr/bin/env python3
"""Thin AgentTools packaging entry for THEA-MCP-GATEWAY-002 (DreamVault SSOT).

Does not invent a second A2A transport — imports dreamvault.control_plane.thea_mcp_gateway.
Local stdio only. No public deploy from this module.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

DREAMVAULT_ROOT = Path(os.environ.get("DREAMVAULT_ROOT", r"D:\DreamVault"))
sys.path.insert(0, str(DREAMVAULT_ROOT / "src"))

from dreamvault.control_plane import thea_mcp_gateway as gw  # noqa: E402

handle = gw.handle
invoke_tool = gw.invoke_tool
TOOL_SCHEMAS = gw.TOOL_SCHEMAS
ALLOWED_TOOLS = gw.ALLOWED_TOOLS
SERVER_NAME = gw.SERVER_NAME
SERVER_VERSION = gw.SERVER_VERSION


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            print(json.dumps(gw._jsonrpc_error(None, -32700, "Parse error")), flush=True)
            continue
        resp = gw.handle(
            req,
            api_key=os.environ.get("THEA_MCP_GATEWAY_TOKEN"),
            principal=os.environ.get("THEA_MCP_PRINCIPAL", "stdio"),
        )
        print(json.dumps(resp), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
