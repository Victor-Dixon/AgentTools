#!/usr/bin/env python3
"""Simple MCP server test"""

import sys
import json
import subprocess
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_mcp_server_simple():
    """Test MCP server with simple approach"""

    print("Testing MCP server...")

    # Test messaging server
    try:
        cmd = [sys.executable, "-m", "swarm_mcp.servers.messaging"]

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(__file__)
        )

        # Send initialize request
        init_req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1,
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }

        process.stdin.write(json.dumps(init_req) + "\n")
        process.stdin.flush()

        # Try to read response
        try:
            response = process.stdout.readline().strip()
            if response:
                data = json.loads(response)
                print(f"✅ Got response: {data.get('result', {}).get('serverInfo', {}).get('name', 'unknown')}")
                return True
            else:
                print("❌ No response")
                return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    finally:
        if 'process' in locals():
            process.terminate()
            process.wait()

if __name__ == "__main__":
    test_mcp_server_simple()