# Agent Tools Repository

This repository contains all tools used by the Agent Swarm system for autonomous operations, coordination, and task execution.

## 🎯 Quick Start - Unified Tools

After Phase 1 consolidation (2025-12-25), use these **3 unified tools** for most operations:

```bash
# Monitoring (queue, service, disk, agents, workspace, coverage)
python tools/unified_monitor.py --category all

# Validation (ssot, imports, tracker, session, refactor, consolidation)
python tools/unified_validator.py --all

# Analysis (repository, structure, file, consolidation, overlaps)
python tools/unified_analyzer.py --category all
```

### Via Toolbelt

```bash
python tools/toolbelt.py --monitor --category all     # or -m
python tools/toolbelt.py --validate --all             # or -V
python tools/toolbelt.py --analyze --category all     # or -a
```

## 📊 Consolidation Status

| Metric | Value |
|--------|-------|
| Starting tools | 709 |
| Current tools | 473 |
| Reduction | 33% (236 deleted) |
| Unified tools | 14 |

See [CONSOLIDATION_PLAN.md](./CONSOLIDATION_PLAN.md) for full details.

## Structure

- **`tools/`** - Consolidated tools (~473 files)
  - `unified_monitor.py` - All monitoring operations
  - `unified_validator.py` - All validation operations
  - `unified_analyzer.py` - All analysis operations
  - `unified_*.py` - Other unified tools (14 total)
  - `captain_*.py` - Captain coordination tools
  - `toolbelt.py` - CLI launcher
- **`tools_v2/`** - Modern toolbelt system with categorized tools
- **`mcp_servers/`** - Custom MCP servers for agent operations

## Unified Tools Reference

### unified_monitor.py
```bash
--category {queue,message_queue_file,service,disk,agents,coverage,workspace,resume,all}
--trigger-resume    # Trigger resume prompts for inactive agents
--watch             # Continuous monitoring mode
--json              # JSON output
```

### unified_validator.py
```bash
--category {ssot_config,imports,tracker,session,refactor,consolidation,queue,all}
--file FILE         # Validate specific file
--dir DIR           # Validate directory
--agent AGENT       # For session validation
--all               # Run all validations
```

### unified_analyzer.py
```bash
--category {repository,structure,file,consolidation,overlaps,all}
--file FILE         # Analyze specific file
--repos REPOS       # Comma-separated repo paths
--json              # JSON output
```

## Gold Tools (Recovered)

These valuable tools were recovered during consolidation:

| Tool | Purpose |
|------|---------|
| `check_sensitive_files.py` | 🔒 Security audit |
| `analyze_swarm_coordination_patterns.py` | 🐝 Swarm BI |
| `tech_debt_ci_summary.py` | 🏗️ CI tech debt |
| `audit_imports.py` | 🔍 Import testing |
| `debug_message_queue.py` | 📬 Queue debugging |
| `fix_message_queue.py` | 🔧 Queue fixer |

## MCP Servers

The `mcp_servers/` directory contains custom MCP servers:
- **`swarm_brain_server.py`** - Swarm knowledge and memory management
- **`task_manager_server.py`** - Task management and tracking
- **`v2_compliance_server.py`** - V2 compliance checking
- **`website_manager_server.py`** - Website management operations
- **`git_operations_server.py`** - Git operations and verification
- **`messaging_server.py`** - Agent messaging operations

## Contributing

When adding new tools:
1. Check if functionality exists in a unified tool first
2. If new functionality needed, add to appropriate `unified_*.py`
3. Register in `tools/toolbelt_registry.py`
4. Update this README if adding new categories

## License

Part of the Agent Swarm system.
