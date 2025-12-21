# MCP Servers for Agent Swarm

This directory contains Model Context Protocol (MCP) servers that expose Agent Swarm capabilities.

## 🗂️ Server Organization

The MCP servers are organized into three main categories:

### 1. Core Operations
Essential servers for agent coordination and task management.
- **Swarm Messaging**: Inter-agent communication
- **Task Manager**: Master task log operations
- **Swarm Brain**: Knowledge base and memory

### 2. Development & Quality
Tools for maintaining code quality and standards.
- **Git Operations**: Work verification and commit checking
- **V2 Compliance**: Code standard enforcement
- **Testing Server**: Test execution and coverage analysis
- **Memory Safety**: Resource leak detection and verification

### 3. Infrastructure & Monitoring
Tools for system health and external services.
- **Website Manager**: WordPress and content management
- **Observability Server**: System metrics and health monitoring

---

## 🚀 Server Details

### 1. Swarm Messaging Server
Exposes the swarm messaging system via MCP, allowing agents and external tools to send messages to agents via PyAutoGUI coordinates.
- **Tools**: `send_agent_message`, `broadcast_message`, `get_agent_coordinates`

### 2. Task Manager Server
Exposes the MASTER_TASK_LOG.md system via MCP.
- **Tools**: `add_task_to_inbox`, `mark_task_complete`, `move_task_to_waiting`, `get_tasks`

### 3. Website Manager Server
Exposes WordPress and website management capabilities.
- **Tools**: `create_wordpress_page`, `deploy_file_to_wordpress`, `create_blog_post`, `generate_image_prompts`

### 4. Swarm Brain Server
Exposes Swarm Brain knowledge base operations.
- **Tools**: `share_learning`, `record_decision`, `search_swarm_knowledge`, `take_note`

### 5. Git Operations Server
Exposes git verification and commit checking capabilities.
- **Tools**: `verify_git_work`, `get_recent_commits`, `check_file_history`, `validate_commit`

### 6. V2 Compliance Checker Server
Exposes V2 compliance validation capabilities.
- **Tools**: `check_v2_compliance`, `validate_file_size`, `check_function_size`, `get_v2_exceptions`

### 7. Testing Server (NEW)
Exposes testing and coverage capabilities.
- **Tools**: 
  - `run_coverage_analysis`: Run tests with coverage reporting
  - `run_mutation_tests`: Run mutation quality gate

### 8. Observability Server (NEW)
Exposes metrics and system health monitoring.
- **Tools**: 
  - `get_metrics_snapshot`: Get current system metrics
  - `check_system_health`: Verify component health status
  - `check_slo_compliance`: Check Service Level Objectives

### 9. Memory Safety Server (NEW)
Exposes memory leak detection and resource verification.
- **Tools**: 
  - `detect_memory_leaks`: Scan for unbounded data structures
  - `verify_files_exist`: Prevent phantom task references
  - `check_file_handles`: Detect unclosed file resources

---

## ⚙️ Configuration

To use these servers, add them to your MCP settings (e.g., `claude_desktop_config.json`).
A complete configuration example is available in `all_mcp_servers.json`.

```json
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["/path/to/mcp_servers/server_script.py"]
    }
  }
}
```
