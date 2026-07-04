#!/usr/bin/env python3
"""
Test suite for swarm_mcp/servers/tasks.py
Increases coverage from 19% to >80%
"""

import json
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarm_mcp.servers.tasks import (
    read_task_log,
    write_task_log,
    add_to_inbox,
    mark_task_complete,
    get_tasks,
    select_next_task,
    verify_task_completion,
    recover_system,
    main
)


class TestTasksServer:
    """Test cases for tasks server functions."""

    @patch('swarm_mcp.servers.tasks.TASK_LOG_PATH')
    def test_read_task_log_file_exists(self, mock_path):
        """Test reading task log when file exists."""
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = "# Test content"

        result = read_task_log()

        assert result == "# Test content"
        mock_path.exists.assert_called_once()
        mock_path.read_text.assert_called_once_with(encoding="utf-8")

    @patch('swarm_mcp.servers.tasks.TASK_LOG_PATH')
    def test_read_task_log_file_not_exists(self, mock_path):
        """Test reading task log when file doesn't exist."""
        mock_path.exists.return_value = False

        result = read_task_log()

        assert result == ""
        mock_path.exists.assert_called_once()

    @patch('swarm_mcp.servers.tasks.TASK_LOG_PATH')
    def test_write_task_log_success(self, mock_path):
        """Test successful task log writing."""
        mock_path.write_text.return_value = None

        result = write_task_log("test content")

        assert result is True
        mock_path.write_text.assert_called_once_with("test content", encoding="utf-8")

    @patch('swarm_mcp.servers.tasks.TASK_LOG_PATH')
    def test_write_task_log_failure(self, mock_path):
        """Test task log writing failure."""
        mock_path.write_text.side_effect = Exception("Write failed")

        result = write_task_log("test content")

        assert result is False
        mock_path.write_text.assert_called_once_with("test content", encoding="utf-8")

    @patch('swarm_mcp.servers.tasks.read_task_log')
    def test_add_to_inbox_success(self, mock_read):
        """Test successful addition to inbox."""
        mock_read.return_value = """# MASTER TASK LOG

## INBOX
- [ ] Existing task

## COMPLETED
"""

        result = add_to_inbox("New test task", "Agent-1")

        assert result["success"] is True
        assert "New test task" in result["message"]
        assert result["agent_id"] == "Agent-1"

    @patch('swarm_mcp.servers.tasks.read_task_log')
    @patch('swarm_mcp.servers.tasks.write_task_log')
    def test_add_to_inbox_no_inbox_section(self, mock_write, mock_read):
        """Test adding to inbox when INBOX section doesn't exist."""
        mock_read.return_value = "# MASTER TASK LOG\n\n## OTHER SECTION"
        mock_write.return_value = True

        result = add_to_inbox("New task")

        assert result["success"] is True
        # Verify write was called with content that includes INBOX section
        call_args = mock_write.call_args[0][0]
        assert "## INBOX" in call_args
        assert "- [ ] New task" in call_args

    @patch('swarm_mcp.servers.tasks.read_task_log')
    def test_add_to_inbox_write_failure(self, mock_read):
        """Test inbox addition when write fails."""
        mock_read.return_value = "# MASTER TASK LOG\n\n## INBOX"

        with patch('swarm_mcp.servers.tasks.write_task_log', return_value=False):
            result = add_to_inbox("Test task")

        assert result["success"] is False
        assert "Failed to write" in result["error"]

    @patch('swarm_mcp.servers.tasks.read_task_log')
    def test_get_tasks_success(self, mock_read):
        """Test successful task retrieval."""
        mock_read.return_value = """# MASTER TASK LOG

## 🎯 THIS WEEK
- [ ] Task 1 description
- [x] Completed task
- [ ] Task 2 with agent Agent-1

## 📥 INBOX
- [ ] Inbox task 1
"""

        result = get_tasks()

        assert result["success"] is True
        assert "THIS WEEK" in result["sections"]
        assert "INBOX" in result["sections"]
        assert len(result["sections"]["THIS WEEK"]) == 3
        assert len(result["sections"]["INBOX"]) == 1

    @patch('swarm_mcp.servers.tasks.read_task_log')
    def test_get_tasks_specific_section(self, mock_read):
        """Test task retrieval for specific section."""
        mock_read.return_value = """# MASTER TASK LOG

## 🎯 THIS WEEK
- [ ] Task 1 description
"""

        result = get_tasks("THIS WEEK")

        assert result["success"] is True
        assert "THIS WEEK" in result["sections"]
        assert len(result["sections"]["THIS WEEK"]) == 1

    @patch('swarm_mcp.servers.tasks.read_task_log')
    @patch('swarm_mcp.servers.tasks.write_task_log')
    def test_mark_task_complete_success(self, mock_write, mock_read):
        """Test successful task completion marking."""
        mock_read.return_value = """# MASTER TASK LOG

## 🎯 THIS WEEK
- [ ] Task 1 description
- [ ] Task 2 description

---
"""
        mock_write.return_value = True

        result = mark_task_complete("Task 1 description")

        assert result["success"] is True
        assert result["task"] == "Task 1 description"
        assert result["section"] == "THIS WEEK"

        # Verify the updated content
        call_args = mock_write.call_args[0][0]
        assert "- [x] Task 1 description" in call_args

    @patch('swarm_mcp.servers.tasks.read_task_log')
    def test_mark_task_complete_task_not_found(self, mock_read):
        """Test task completion when task doesn't exist."""
        mock_read.return_value = """# MASTER TASK LOG

## 🎯 THIS WEEK
- [ ] Existing task
---
"""

        result = mark_task_complete("Non-existent task")

        assert result["success"] is False
        assert "not found" in result["error"]

    @patch('swarm_mcp.servers.tasks.HAS_STAGE_4', True)
    @patch('swarm_mcp.servers.tasks.TaskScorer')
    def test_select_next_task_success(self, mock_scorer_class):
        """Test successful next task selection."""
        mock_scorer = Mock()
        mock_scorer_class.return_value = mock_scorer

        mock_task = Mock()
        mock_task.task_id = "task_1"
        mock_task.description = "High priority task"
        mock_task.score = 95

        mock_scorer.select_next_task.return_value = mock_task

        result = select_next_task("urgent")

        assert result["success"] is True
        assert result["task"]["task_id"] == "task_1"
        assert result["task"]["description"] == "High priority task"
        assert result["task"]["score"] == 95
        mock_scorer.select_next_task.assert_called_once_with("urgent")

    @patch('swarm_mcp.servers.tasks.HAS_STAGE_4', False)
    def test_select_next_task_no_stage4(self):
        """Test next task selection when Stage 4 is not available."""
        result = select_next_task()

        assert result["success"] is False
        assert "Stage 4 capabilities not available" in result["error"]

    @patch('swarm_mcp.servers.tasks.HAS_STAGE_4', True)
    @patch('swarm_mcp.servers.tasks.VerificationHarness')
    def test_verify_task_completion_success(self, mock_verification_class):
        """Test successful task completion verification."""
        mock_harness = Mock()
        mock_verification_class.return_value = mock_harness

        mock_result = Mock()
        mock_result.passed = True
        mock_result.details = "Task completed successfully"

        mock_harness.verify_completion.return_value = mock_result

        result = verify_task_completion("Task completed", "manual", "high")

        assert result["success"] is True
        assert result["verification"]["passed"] is True
        assert "Task completed successfully" in result["verification"]["details"]

    @patch('swarm_mcp.servers.tasks.HAS_STAGE_4', False)
    def test_verify_task_completion_no_stage4(self):
        """Test task verification when Stage 4 is not available."""
        result = verify_task_completion("Test task", "manual")

        assert result["success"] is False
        assert "Stage 4 capabilities not available" in result["error"]

    @patch('swarm_mcp.servers.tasks.HAS_STAGE_4', True)
    @patch('swarm_mcp.servers.tasks.RecoveryManager')
    def test_recover_system_success(self, mock_recovery_class):
        """Test successful system recovery."""
        mock_manager = Mock()
        mock_recovery_class.return_value = mock_manager

        mock_event = Mock()
        mock_event.recovery_actions = ["Action 1", "Action 2"]
        mock_event.status = "recovered"

        mock_manager.recover_from_error.return_value = mock_event

        result = recover_system("Database connection failed")

        assert result["success"] is True
        assert result["recovery"]["status"] == "recovered"
        assert len(result["recovery"]["actions"]) == 2

    @patch('swarm_mcp.servers.tasks.HAS_STAGE_4', True)
    @patch('swarm_mcp.servers.tasks.TaskScorer')
    def test_score_tasks_success(self, mock_scorer_class):
        """Test successful task scoring."""
        mock_scorer = Mock()
        mock_scorer_class.return_value = mock_scorer

        mock_task = Mock()
        mock_task.task_id = "task_1"
        mock_task.score = 85
        mock_task.priority = "high"

        mock_scorer.score_tasks.return_value = [mock_task]

        with patch('swarm_mcp.servers.tasks.get_inbox_tasks') as mock_get_inbox:
            mock_get_inbox.return_value = {
                "success": True,
                "tasks": [{"description": "Test task"}]
            }

            result = self._call_score_tasks()

            assert result["success"] is True
            assert len(result["scored_tasks"]) == 1
            assert result["scored_tasks"][0]["task_id"] == "task_1"

    @patch('swarm_mcp.servers.tasks.HAS_STAGE_4', False)
    def test_score_tasks_no_stage4(self):
        """Test task scoring when Stage 4 is not available."""
        result = self._call_score_tasks()

        assert result["success"] is False
        assert "Stage 4 capabilities not available" in result["error"]

    def _call_score_tasks(self):
        """Helper to call score_tasks function."""
        from swarm_mcp.servers.tasks import score_tasks
        return score_tasks()

    @patch('sys.stdout')
    def test_main_initialization(self, mock_stdout):
        """Test main function initialization output."""
        from swarm_mcp.servers.tasks import main
        main()

        # Check that stdout.write was called with initialization message
        mock_stdout.write.assert_called()
        call_args = mock_stdout.write.call_args[0][0]

        # Parse the JSON output
        data = json.loads(call_args.strip())
        assert data["jsonrpc"] == "2.0"
        assert data["method"] == "initialize"
        assert "result" in data
        assert data["result"]["serverInfo"]["name"] == "swarm-tasks"

    @patch('sys.stdin')
    @patch('sys.stdout')
    def test_main_tools_call_add_to_inbox(self, mock_stdout, mock_stdin):
        """Test main function handling tools/call for add_to_inbox."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "add_to_inbox",
                "arguments": {
                    "task": "Test task",
                    "agent_id": "Agent-1"
                }
            }
        }

        mock_stdin.__iter__ = Mock(return_value=iter([json.dumps(request)]))

        with patch('swarm_mcp.servers.tasks.add_to_inbox') as mock_add:
            mock_add.return_value = {"success": True, "message": "Task added"}
            from swarm_mcp.servers.tasks import main
            main()

        call_args = mock_stdout.write.call_args[0][0]
        response = json.loads(call_args.strip())

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        mock_add.assert_called_once_with(task="Test task", agent_id="Agent-1")

    @patch('sys.stdin')
    @patch('sys.stdout')
    def test_main_tools_call_get_inbox_tasks(self, mock_stdout, mock_stdin):
        """Test main function handling tools/call for get_inbox_tasks."""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_inbox_tasks",
                "arguments": {}
            }
        }

        mock_stdin.__iter__ = Mock(return_value=iter([json.dumps(request)]))

        with patch('swarm_mcp.servers.tasks.get_inbox_tasks') as mock_get:
            mock_get.return_value = {"success": True, "tasks": []}
            from swarm_mcp.servers.tasks import main
            main()

        call_args = mock_stdout.write.call_args[0][0]
        response = json.loads(call_args.strip())

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        mock_get.assert_called_once()

    @patch('sys.stdin')
    @patch('sys.stdout')
    def test_main_tools_call_update_task_status(self, mock_stdout, mock_stdin):
        """Test main function handling tools/call for update_task_status."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "update_task_status",
                "arguments": {
                    "description": "Test task",
                    "status": "completed"
                }
            }
        }

        mock_stdin.__iter__ = Mock(return_value=iter([json.dumps(request)]))

        with patch('swarm_mcp.servers.tasks.update_task_status') as mock_update:
            mock_update.return_value = {"success": True, "message": "Status updated"}
            from swarm_mcp.servers.tasks import main
            main()

        call_args = mock_stdout.write.call_args[0][0]
        response = json.loads(call_args.strip())

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 3
        mock_update.assert_called_once_with(description="Test task", status="completed")

    @patch('sys.stdin')
    @patch('sys.stdout')
    def test_main_tools_call_search_tasks(self, mock_stdout, mock_stdin):
        """Test main function handling tools/call for search_tasks."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "search_tasks",
                "arguments": {"query": "test"}
            }
        }

        mock_stdin.__iter__ = Mock(return_value=iter([json.dumps(request)]))

        with patch('swarm_mcp.servers.tasks.search_tasks') as mock_search:
            mock_search.return_value = {"success": True, "matches": []}
            from swarm_mcp.servers.tasks import main
            main()

        call_args = mock_stdout.write.call_args[0][0]
        response = json.loads(call_args.strip())

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 4
        mock_search.assert_called_once_with(query="test")

    @patch('sys.stdin')
    @patch('sys.stdout')
    def test_main_tools_call_unknown_tool(self, mock_stdout, mock_stdin):
        """Test main function handling unknown tool."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {}
            }
        }

        mock_stdin.__iter__ = lambda: iter([json.dumps(request)])
        from swarm_mcp.servers.tasks import main
        main()

        call_args = mock_stdout.write.call_args[0][0]
        response = json.loads(call_args.strip())

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 5
        assert "result" in response
        result_content = json.loads(response["result"]["content"][0]["text"])
        assert result_content["success"] is False
        assert "Unknown tool" in result_content["error"]


if __name__ == "__main__":
    pytest.main([__file__])