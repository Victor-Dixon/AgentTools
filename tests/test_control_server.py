#!/usr/bin/env python3
"""
Test suite for swarm_mcp/servers/control.py
Increases coverage from 24% to >80%
"""

import json
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarm_mcp.servers.control import (
    get_coordinator,
    check_pack_status,
    assign_hunt,
    scout_territory,
    main
)


class TestControlServer:
    """Test cases for control server functions."""

    @patch('swarm_mcp.servers.control.HAS_CORE', True)
    @patch('swarm_mcp.servers.control.PackCoordinator')
    def test_get_coordinator_success(self, mock_coordinator_class):
        """Test successful coordinator creation."""
        mock_coordinator = Mock()
        mock_coordinator_class.return_value = mock_coordinator

        result = get_coordinator()

        assert result == mock_coordinator
        mock_coordinator_class.assert_called_once_with(
            wolves=["Agent-1", "Agent-2", "Agent-8", "Captain"],
            den="./agent_workspaces"
        )

    @patch('swarm_mcp.servers.control.HAS_CORE', False)
    def test_check_pack_status_no_core(self):
        """Test pack status check when core is not available."""
        result = check_pack_status()

        assert result == {"success": False, "error": "Swarm Core not available"}

    @patch('swarm_mcp.servers.control.HAS_CORE', True)
    @patch('swarm_mcp.servers.control.get_coordinator')
    def test_check_pack_status_success(self, mock_get_coordinator):
        """Test successful pack status check."""
        # Mock coordinator
        mock_coord = Mock()
        mock_get_coordinator.return_value = mock_coord

        # Mock roll_call result
        mock_status = Mock()
        mock_status.role = "wolf"
        mock_status.status = "active"
        mock_status.current_hunt = "hunt_123"
        mock_status.kills = 5
        mock_status.last_howl = Mock()
        mock_status.last_howl.isoformat.return_value = "2024-01-12T10:00:00"

        mock_coord.roll_call.return_value = {
            "Agent-1": mock_status,
            "Agent-2": mock_status
        }

        result = check_pack_status()

        assert result["success"] is True
        assert "pack_status" in result
        assert "Agent-1" in result["pack_status"]
        assert "Agent-2" in result["pack_status"]
        assert result["pack_status"]["Agent-1"]["role"] == "wolf"
        assert result["pack_status"]["Agent-1"]["status"] == "active"

    @patch('swarm_mcp.servers.control.HAS_CORE', True)
    @patch('swarm_mcp.servers.control.get_coordinator')
    def test_check_pack_status_exception(self, mock_get_coordinator):
        """Test pack status check with exception."""
        mock_coord = Mock()
        mock_coord.roll_call.side_effect = Exception("Database error")
        mock_get_coordinator.return_value = mock_coord

        result = check_pack_status()

        assert result["success"] is False
        assert "Database error" in result["error"]

    @patch('swarm_mcp.servers.control.HAS_CORE', False)
    def test_assign_hunt_no_core(self):
        """Test hunt assignment when core is not available."""
        result = assign_hunt("Agent-1", "test task")

        assert result == {"success": False, "error": "Swarm Core not available"}

    @patch('swarm_mcp.servers.control.HAS_CORE', True)
    @patch('swarm_mcp.servers.control.get_coordinator')
    def test_assign_hunt_success(self, mock_get_coordinator):
        """Test successful hunt assignment."""
        mock_coord = Mock()
        mock_coord.assign_hunt.return_value = True
        mock_get_coordinator.return_value = mock_coord

        result = assign_hunt("Agent-1", "test task", 5)

        assert result["success"] is True
        assert result["agent_id"] == "Agent-1"
        assert result["task"] == "test task"
        assert result["status"] == "assigned"
        mock_coord.assign_hunt.assert_called_once_with(
            wolf_id="Agent-1",
            prey="test task",
            difficulty=5
        )

    @patch('swarm_mcp.servers.control.HAS_CORE', True)
    @patch('swarm_mcp.servers.control.get_coordinator')
    def test_assign_hunt_exception(self, mock_get_coordinator):
        """Test hunt assignment with exception."""
        mock_coord = Mock()
        mock_coord.assign_hunt.side_effect = Exception("Assignment failed")
        mock_get_coordinator.return_value = mock_coord

        result = assign_hunt("Agent-1", "test task")

        assert result["success"] is False
        assert "Assignment failed" in result["error"]

    @patch('swarm_mcp.servers.control.HAS_CORE', False)
    def test_scout_territory_no_core(self):
        """Test territory scouting when core is not available."""
        result = scout_territory(".")

        assert result == {"success": False, "error": "Swarm Core not available"}

    @patch('swarm_mcp.servers.control.HAS_CORE', True)
    @patch('swarm_mcp.servers.control.get_coordinator')
    def test_scout_territory_success(self, mock_get_coordinator):
        """Test successful territory scouting."""
        mock_coord = Mock()
        mock_get_coordinator.return_value = mock_coord

        # Mock prey objects
        mock_prey1 = Mock()
        mock_prey1.prey_id = "task_1"
        mock_prey1.description = "Test task 1"
        mock_prey1.location = "file.py:10"
        mock_prey1.difficulty = 3

        mock_prey2 = Mock()
        mock_prey2.prey_id = "task_2"
        mock_prey2.description = "Test task 2"
        mock_prey2.location = "file.py:20"
        mock_prey2.difficulty = 5

        mock_coord.scout_territory.return_value = [mock_prey1, mock_prey2]

        result = scout_territory("/test/path")

        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["prey"]) == 2
        assert result["prey"][0]["id"] == "task_1"
        assert result["prey"][0]["description"] == "Test task 1"
        assert result["prey"][1]["difficulty"] == 5
        mock_coord.scout_territory.assert_called_once_with("/test/path")

    @patch('swarm_mcp.servers.control.HAS_CORE', True)
    @patch('swarm_mcp.servers.control.get_coordinator')
    def test_scout_territory_exception(self, mock_get_coordinator):
        """Test territory scouting with exception."""
        mock_coord = Mock()
        mock_coord.scout_territory.side_effect = Exception("Scouting failed")
        mock_get_coordinator.return_value = mock_coord

        result = scout_territory()

        assert result["success"] is False
        assert "Scouting failed" in result["error"]

    @patch('sys.stdout')
    def test_main_initialization(self, mock_stdout):
        """Test main function initialization output."""
        main()

        # Check that stdout.write was called with initialization message
        mock_stdout.write.assert_called()
        call_args = mock_stdout.write.call_args[0][0]

        # Parse the JSON output
        data = json.loads(call_args.strip())
        assert data["jsonrpc"] == "2.0"
        assert data["method"] == "initialize"
        assert "result" in data
        assert data["result"]["serverInfo"]["name"] == "swarm-control"

    @patch('sys.stdin')
    @patch('sys.stdout')
    def test_main_tools_call_check_pack_status(self, mock_stdout, mock_stdin):
        """Test main function handling tools/call for check_pack_status."""
        # Mock stdin to provide a JSON request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "check_pack_status",
                "arguments": {}
            }
        }

        mock_stdin.__iter__ = Mock(return_value=iter([json.dumps(request)]))

        with patch('swarm_mcp.servers.control.check_pack_status') as mock_check:
            mock_check.return_value = {"success": True, "status": "test"}
            main()

        # Verify the response
        call_args = mock_stdout.write.call_args[0][0]
        response = json.loads(call_args.strip())

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response

    @patch('sys.stdin')
    @patch('sys.stdout')
    def test_main_tools_call_assign_hunt(self, mock_stdout, mock_stdin):
        """Test main function handling tools/call for assign_hunt."""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "assign_hunt",
                "arguments": {
                    "agent_id": "Agent-1",
                    "task": "test task",
                    "difficulty": 4
                }
            }
        }

        mock_stdin.__iter__ = Mock(return_value=iter([json.dumps(request)]))

        with patch('swarm_mcp.servers.control.assign_hunt') as mock_assign:
            mock_assign.return_value = {"success": True, "agent_id": "Agent-1"}
            main()

        call_args = mock_stdout.write.call_args[0][0]
        response = json.loads(call_args.strip())

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        mock_assign.assert_called_once_with(agent_id="Agent-1", task="test task", difficulty=4)

    @patch('sys.stdin')
    @patch('sys.stdout')
    def test_main_tools_call_scout_territory(self, mock_stdout, mock_stdin):
        """Test main function handling tools/call for scout_territory."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "scout_territory",
                "arguments": {"path": "/test/path"}
            }
        }

        mock_stdin.__iter__ = Mock(return_value=iter([json.dumps(request)]))

        with patch('swarm_mcp.servers.control.scout_territory') as mock_scout:
            mock_scout.return_value = {"success": True, "count": 5}
            main()

        call_args = mock_stdout.write.call_args[0][0]
        response = json.loads(call_args.strip())

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 3
        mock_scout.assert_called_once_with(path="/test/path")

    @patch('sys.stdin')
    @patch('sys.stdout')
    def test_main_tools_call_unknown_tool(self, mock_stdout, mock_stdin):
        """Test main function handling unknown tool."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {}
            }
        }

        mock_stdin.__iter__ = Mock(return_value=iter([json.dumps(request)]))
        main()

        call_args = mock_stdout.write.call_args[0][0]
        response = json.loads(call_args.strip())

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 4
        assert "result" in response
        result_content = json.loads(response["result"]["content"][0]["text"])
        assert result_content["success"] is False
        assert "Unknown tool" in result_content["error"]

    @patch('sys.stdin')
    @patch('sys.stdout')
    def test_main_exception_handling(self, mock_stdout, mock_stdin):
        """Test main function exception handling."""
        # Invalid JSON
        mock_stdin.__iter__ = Mock(return_value=iter(["invalid json"]))

        main()

        call_args = mock_stdout.write.call_args[0][0]
        response = json.loads(call_args.strip())

        assert response["jsonrpc"] == "2.0"
        assert "error" in response
        assert response["error"]["code"] == -32603


if __name__ == "__main__":
    pytest.main([__file__])