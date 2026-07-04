# ⚡ Quick Start - Phase 0A Tools

**Quick reference for using tools to help with Phase 0A: Organization & Planning**

---

## 🚀 Installation (One-Time Setup)

```bash
cd /home/dream/Development/projects/personal/AgentTools

# Optional: Install in development mode
pip install -e .
```

**That's it!** No additional installation needed. Tools run directly from the project.

---

## 📋 Essential Commands for Phase 0A

### 1. Tool Inventory & Discovery

```bash
# Analyze all tools in repository
python3 tools/analysis/unified_analyzer.py --category all --json > phase0a_reports/tool_analysis.json

# Analyze repository structure
python3 tools/analysis/unified_analyzer.py --category repository --json > phase0a_reports/repo_structure.json

# Analyze project structure
python3 tools/analysis/unified_analyzer.py --category structure --json > phase0a_reports/project_structure.json

# Find consolidation opportunities
python3 tools/analysis/unified_analyzer.py --category consolidation --json > phase0a_reports/consolidation_ops.json

# Detect overlaps
python3 tools/analysis/unified_analyzer.py --category overlaps --json > phase0a_reports/overlaps.json
```

### 2. Dependency Analysis

```bash
# Validate all imports
python3 tools/validation/unified_validator.py --category imports --json > phase0a_reports/imports.json

# Validate all categories
python3 tools/validation/unified_validator.py --all --json > phase0a_reports/validation.json
```

### 3. System Health Check

```bash
# Monitor all systems
python3 tools/monitoring/unified_monitor.py --category all --json > phase0a_reports/system_health.json
```

---

## 🎯 Phase 0A Task → Command Cheat Sheet

| Task | Command |
|------|---------|
| **Inventory all tools** | `python3 tools/analysis/unified_analyzer.py --category all --json` |
| **Map dependencies** | `python3 tools/validation/unified_validator.py --category imports --json` |
| **Analyze usage** | `python3 tools/analysis/unified_analyzer.py --category structure --json` |
| **Find duplicates** | `python3 tools/analysis/unified_analyzer.py --category overlaps --json` |
| **Check V2 compliance** | `python3 tools/validation/unified_validator.py --category all --json` |
| **🤖 AI coordination analysis** | `mcp --server ai-orchestration analyze_task --task-description "your task"` |
| **🤖 Generate coordination message** | `mcp --server ai-orchestration generate_coordination_message --task "task" --agent-ids "[\"agent-1\",\"agent-2\"]"` |

---

## 📊 Generate All Phase 0A Reports

```bash
# Create reports directory
mkdir -p phase0a_reports

# Generate all reports at once
python3 tools/analysis/unified_analyzer.py --category all --json > phase0a_reports/analysis.json && \
python3 tools/validation/unified_validator.py --all --json > phase0a_reports/validation.json && \
python3 tools/monitoring/unified_monitor.py --category all --json > phase0a_reports/monitoring.json && \
echo "✅ All Phase 0A reports generated!"
```

---

## 🔍 Tool Help Commands

```bash
# Get help for any tool
python3 tools/analysis/unified_analyzer.py --help
python3 tools/validation/unified_validator.py --help
python3 tools/monitoring/unified_monitor.py --help
```

---

## 📝 Next Steps

1. Run the analysis commands above
2. Review the generated JSON reports
3. Use the data to populate `tools_inventory.json`
4. Follow `PHASE_0A_ORGANIZATION_PLAN.md` for detailed tasks

---

**See `TOOLS_USAGE_GUIDE.md` for complete documentation.**


