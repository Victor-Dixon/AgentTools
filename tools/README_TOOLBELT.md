# CLI Toolbelt - Unified Tool Access 🛠️

**Version:** 2.0.0 (Consolidated)
**Architecture:** WE ARE SWARM
**Status:** Phase 4 Consolidation Complete
**Date:** 2025-12-26

---

## 🎯 Overview

CLI Toolbelt provides a single, unified command-line interface to access all Swarm tools. It consolidates 160+ specialized tools into a streamlined interface using the "Unified", "Gold", and "Diamond" tier system.

**One Command to Rule Them All:**
```bash
python -m tools.toolbelt [FLAG] [ARGS...]
```

---

## 🚀 Quick Start

### 1. Show Help & List Tools
```bash
python -m tools.toolbelt --help
python -m tools.toolbelt --list
```

### 2. Run Unified Tools (The Big Three)
```bash
# Monitoring (Queue, Service, Disk, Agents)
python -m tools.toolbelt --monitor

# Validation (SSOT, Imports, Config)
python -m tools.toolbelt --validate

# Analysis (Repository, Complexity, Structure)
python -m tools.toolbelt --analyze
```

### 3. Run Specialized Tools
```bash
# Check for sensitive files
python -m tools.toolbelt --check-sensitive

# Diagnose GitHub Auth
python -m tools.toolbelt --diagnose-auth

# Debug Message Queue
python -m tools.toolbelt --debug-queue
```

---

## 📊 Available Tools

### 🟢 Unified Tools (Primary Interfaces)

| Tool | Flags | Description |
|------|-------|-------------|
| **Unified Monitor** | `--monitor`, `-m` | System-wide monitoring (Queue, Service, Disk, Agents) |
| **Unified Validator** | `--validate`, `-V` | System-wide validation (SSOT, Imports, Config) |
| **Unified Analyzer** | `--analyze`, `-a` | System-wide analysis (Repo, Structure, Overlap) |
| **Unified Agent** | `--agent`, `-A` | Agent operations (Status, Tasks, Orientation) |
| **Unified Captain** | `--captain`, `-C` | Captain operations (Inbox, Coordination) |
| **Unified Cleanup** | `--cleanup` | System cleanup (Workspace, Archives) |
| **Unified Discord** | `--discord` | Discord operations (Bot, Webhooks) |
| **Unified GitHub** | `--github` | GitHub operations (PRs, Issues) |
| **Unified Verifier** | `--verify` | Deep verification (CI/CD, Credentials) |
| **Unified WordPress** | `--wordpress` | WordPress operations (Deploy, Theme) |

### 🟡 Gold Tools (Critical/Security/Recovery)

| Tool | Flags | Description |
|------|-------|-------------|
| **Sensitive File Checker** | `--check-sensitive` | Scan for sensitive files/credentials |
| **Import Auditor** | `--audit-imports` | Audit Python imports |
| **GitHub Auth Diagnoser** | `--diagnose-auth` | Fix GitHub CLI auth |
| **Queue Debugger** | `--debug-queue` | Debug message queue contents |
| **Queue Fixer** | `--fix-queue` | Fix message queue issues |
| **Stuck Message Checker** | `--check-stuck` | Identify stuck messages |
| **CI Debt Summary** | `--ci-debt` | Summarize CI technical debt |
| **Swarm Pattern Analyzer** | `--swarm-patterns` | Analyze coordination patterns |
| **Session Creator** | `--create-session` | Create new work sessions |

### 🔵 Diamond Tools (High Value Specialists)

| Tool | Flags | Description |
|------|-------|-------------|
| **Type Fixer** | `--fix-types` | Add/fix type annotations |
| **Refactoring Suggester** | `--suggest-refactor` | Generate refactoring suggestions |
| **Consolidation Analyzer** | `--analyze-consolidation` | Analyze consolidation opportunities |
| **Technical Debt Analyzer** | `--analyze-debt` | Deep scan for technical debt |
| **Source Analyzer** | `--analyze-source` | Source code statistics |
| **Auto Cleaner** | `--auto-cleanup` | Automated workspace maintenance |
| **Session Cleanup** | `--session-cleanup` | Cleanup old sessions |
| **Doc Generator** | `--generate-docs` | Generate documentation |
| **SEO Extractor** | `--seo-extract` | Extract SEO meta tags |
| **Task CLI** | `--task`, `-t` | Task management CLI |

---

## 💡 Usage Examples

### Monitoring & Validation
```bash
# Run full system monitor
python -m tools.toolbelt --monitor --category all

# Validate imports only
python -m tools.toolbelt --validate --category imports
```

### Debugging
```bash
# Debug message queue
python -m tools.toolbelt --debug-queue

# Check for stuck messages
python -m tools.toolbelt --check-stuck
```

### Automation
```bash
# Create a new session
python -m tools.toolbelt --create-session --objective "Fix bug X"

# Clean workspace
python -m tools.toolbelt --auto-cleanup
```

---

## 🔧 Adding New Tools

1.  Create your tool script in `tools/`.
2.  Add an entry to `tools/toolbelt_registry.py`:
    ```python
    "my-tool": {
        "name": "My Tool",
        "module": "tools.my_tool",
        "main_function": "main",
        "description": "My tool description",
        "flags": ["--my-tool"],
        "args_passthrough": True
    }
    ```
3.  Use it: `python -m tools.toolbelt --my-tool`

---

## 🏆 Credits

*   **Architecture**: WE ARE SWARM
*   **Consolidation**: Phase 4 Team
*   **Mission**: Unified Tool Access
