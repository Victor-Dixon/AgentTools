#!/usr/bin/env python3
"""
Test MCP integration by simulating Claude Desktop/Cursor MCP protocol
"""

import sys
import json
import subprocess
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_mcp_server(server_module, server_name):
    """Test a single MCP server with basic protocol messages"""

    print(f"\n🔍 Testing {server_name} MCP server...")

    try:
        # Start the MCP server process
        cmd = [sys.executable, "-m", server_module]
        env = {"PYTHONPATH": str(Path(__file__).parent)}

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**env, **dict(os.environ)},
            cwd=str(Path(__file__).parent)
        )

        # Test 1: Initialize request
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1,
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        # Send initialize request
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Read response
        response_line = process.stdout.readline().strip()
        if not response_line:
            print(f"❌ {server_name}: No response to initialize")
            process.terminate()
            return False

        try:
            response = json.loads(response_line)
            if "error" in response:
                print(f"❌ {server_name}: Initialize error: {response['error']}")
                process.terminate()
                return False

            if "result" not in response:
                print(f"❌ {server_name}: No result in initialize response")
                process.terminate()
                return False

            # Check server info
            server_info = response["result"].get("serverInfo", {})
            if server_info.get("name") != server_name:
                print(f"❌ {server_name}: Wrong server name: {server_info.get('name')}")
                process.terminate()
                return False

            print(f"✅ {server_name}: Initialize successful")

        except json.JSONDecodeError:
            print(f"❌ {server_name}: Invalid JSON response")
            process.terminate()
            return False

        # Test 2: Tools list request
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 2
        }

        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()

        # Read tools response
        tools_response_line = process.stdout.readline().strip()
        if not tools_response_line:
            print(f"❌ {server_name}: No response to tools/list")
            process.terminate()
            return False

        try:
            tools_response = json.loads(tools_response_line)
            if "error" in tools_response:
                print(f"❌ {server_name}: Tools/list error: {tools_response['error']}")
                process.terminate()
                return False

            tools = tools_response.get("result", {}).get("tools", [])
            print(f"✅ {server_name}: Tools/list successful - {len(tools)} tools available")

            # Print tool names for verification
            tool_names = [tool.get("name", "unnamed") for tool in tools]
            print(f"   Tools: {', '.join(tool_names[:5])}{'...' if len(tool_names) > 5 else ''}")

        except json.JSONDecodeError:
            print(f"❌ {server_name}: Invalid JSON in tools response")
            process.terminate()
            return False

        # Clean shutdown
        process.terminate()
        process.wait(timeout=5)

        print(f"✅ {server_name}: All tests passed")
        return True

    except subprocess.TimeoutExpired:
        print(f"❌ {server_name}: Process timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ {server_name}: Exception - {e}")
        if 'process' in locals():
            process.kill()
        return False

def test_all_mcp_servers():
    """Test all MCP servers"""

    servers = [
        ("swarm_mcp.servers.messaging", "swarm-messaging"),
        ("swarm_mcp.servers.memory", "swarm-memory"),
        ("swarm_mcp.servers.tasks", "swarm-tasks"),
        ("swarm_mcp.servers.control", "swarm-control"),
        ("swarm_mcp.servers.tools", "swarm-tools")
    ]

    passed = 0
    total = len(servers)

    for module, name in servers:
        if test_mcp_server(module, name):
            passed += 1

    print(f"\n📊 MCP Integration Results: {passed}/{total} servers working")

    return passed == total

if __name__ == "__main__":
    print("🔌 Testing MCP Server Integration")
    print("=" * 50)

    success = test_all_mcp_servers()

    print("\n" + "=" * 50)
    if success:
        print("✅ ALL MCP SERVERS INTEGRATION TEST PASSED!")
        print("🎉 Ready for Claude Desktop and Cursor integration!")
        sys.exit(0)
    else:
        print("❌ SOME MCP SERVERS FAILED INTEGRATION TEST!")
        sys.exit(1)