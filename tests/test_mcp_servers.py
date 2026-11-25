import sys
import json
import subprocess
from pathlib import Path
import pytest

from swarm_mcp.servers.messaging import broadcast_message, send_agent_message

# Add workspace root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestMCPServers:
    def _run_server(self, server_module, input_data):
        """Run an MCP server module with input data."""
        cmd = [sys.executable, "-m", server_module]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=json.dumps(input_data) + "\n")
        return stdout, stderr

    def test_tools_server_initialize(self):
        """Test swarm-tools-server initialization."""
        init_req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1
        }
        
        stdout, _ = self._run_server("swarm_mcp.servers.tools", init_req)
        response = json.loads(stdout)
        
        assert response["jsonrpc"] == "2.0"
        
        assert "result" in response
        assert "capabilities" in response["result"]
        assert "tools" in response["result"]["capabilities"]
        
        tools = response["result"]["capabilities"]["tools"]
        assert "run_monitor" in tools
        assert "run_security_scan" in tools

    def test_messaging_server_initialize(self):
        """Test swarm-messaging-server initialization."""
        init_req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1
        }
        
        stdout, _ = self._run_server("swarm_mcp.servers.messaging", init_req)
        response = json.loads(stdout)
        
        assert response["result"]["serverInfo"]["name"] == "swarm-messaging"
        tools = response["result"]["capabilities"]["tools"]
        assert "send_agent_message" in tools

    def test_memory_server_initialize(self):
        """Test swarm-memory-server initialization."""
        init_req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1
        }
        
        stdout, _ = self._run_server("swarm_mcp.servers.memory", init_req)
        response = json.loads(stdout)
        
        assert response["result"]["serverInfo"]["name"] == "swarm-memory"

    def test_tasks_server_initialize(self):
        """Test swarm-tasks-server initialization and Stage 4 tools."""
        init_req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1
        }
        
        stdout, _ = self._run_server("swarm_mcp.servers.tasks", init_req)
        response = json.loads(stdout)
        
        assert response["result"]["serverInfo"]["name"] == "swarm-tasks"
        tools = response["result"]["capabilities"]["tools"]
        
        # Core tasks
        assert "add_task_to_inbox" in tools
        assert "mark_task_complete" in tools
        
        # Stage 4 additions
        assert "select_next_task" in tools
        assert "verify_task_completion" in tools
        assert "recover_system" in tools

    def test_send_agent_message_applies_template(self):
        """send_agent_message should render the selected template category."""
        result = send_agent_message(
            agent_id="Agent-Template-1",
            message="Execute validation",
            category="A2A",
            sender="Agent-2",
        )

        assert result["success"] is True
        assert "[HEADER] A2A" in result["message_sent"]
        assert "#A2A" in result["message_sent"]

    def test_broadcast_message_applies_template(self):
        """broadcast_message should render the selected template category."""
        result = broadcast_message(
            message="Kick off sync",
            category="C2A",
            sender="CAPTAIN",
        )

        assert result["success"] is True
        assert result["category"] == "C2A"


@pytest.mark.parametrize("exit_code", [0, 1, 2])
def test_linter_success_tracks_exit_code(monkeypatch, tmp_path, exit_code):
    from mcp_servers.code_quality_server import run_linter

    monkeypatch.setattr(subprocess, "run", lambda *a, **kw:
                        subprocess.CompletedProcess(a[0], exit_code, "[]", "failure" if exit_code else ""))
    result = run_linter(str(tmp_path), linter="ruff")
    assert result["success"] is (exit_code == 0)
    assert result["exit_code"] == exit_code


@pytest.mark.parametrize("exit_code, expected", [(0, True), (1, False), (2, False), (3, True)])
def test_python_dead_code_result_contract(monkeypatch, tmp_path, exit_code, expected):
    from mcp_servers.code_quality_server import find_dead_code

    output = "sample.py:1: unused function 'f' (80% confidence)" if exit_code == 3 else ""
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw:
                        subprocess.CompletedProcess(a[0], exit_code, output, ""))
    result = find_dead_code(str(tmp_path), language="python")
    assert result["success"] is expected
    assert result["exit_code"] == exit_code
    if exit_code == 3:
        assert result["total"] == 1
