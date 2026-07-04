#!/usr/bin/env python3
"""
MCP Server Template - Standardized Boilerplate
==============================================

This template provides the foundation for all MCP server conversions.
Follow this pattern for consistency across all 12 MCP servers.

V2 Compliant: Modular design, error handling, logging
Author: Agent-2 (Architecture Lead) - Template created by Agent-4
Date: 2026-01-13
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

# MCP imports
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types

# Add project root to path for imports
import sys
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("server-name")


@server.tool()
async def example_tool(args: Dict[str, Any]) -> List[types.TextContent]:
    """
    Example MCP tool demonstrating proper structure.

    Args:
        args: Dictionary containing tool arguments

    Returns:
        List of TextContent with results or error messages
    """
    try:
        # Extract and validate arguments
        param1 = args.get("param1", "default_value")
        param2 = args.get("param2", 0)

        # Validate input
        if not isinstance(param1, str):
            raise ValueError("param1 must be a string")
        if not isinstance(param2, int) or param2 < 0:
            raise ValueError("param2 must be a non-negative integer")

        # Execute tool logic
        result = f"Processed {param1} with value {param2}"

        # Log success
        logger.info(f"Tool executed successfully: {result}")

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        # Comprehensive error handling
        error_msg = f"Tool execution failed: {str(e)}"
        logger.error(error_msg, exc_info=True)

        return [types.TextContent(type="text", text=error_msg)]


@server.tool()
async def health_check(args: Dict[str, Any]) -> List[types.TextContent]:
    """
    Health check tool - verify server functionality.

    Returns server status and basic diagnostics.
    """
    try:
        health_status = {
            "status": "healthy",
            "server": "server-name",
            "timestamp": "2026-01-13T13:00:00Z",
            "tools_available": len(server.list_tools()),
            "version": "1.0.0"
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(health_status, indent=2)
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Health check failed: {str(e)}"
        )]


async def main():
    """Main server execution function."""
    try:
        # Log server startup
        logger.info("Starting MCP server: server-name")

        # Run the MCP server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server startup failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Execute server
    asyncio.run(main())