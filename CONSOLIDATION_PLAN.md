# 🗺️ Master Plan: Tools Consolidation Phase 1

**Goal**: Consolidate 399 specialized tools into 3 unified systems (`unified_monitor`, `unified_validator`, `unified_analyzer`), reducing tool count by ~56%.

**Strategy**: "Consolidate, Verify, Archive".
We will move functionality into the unified tools, verify they work, and then archive the old tools.

---

## 🏗️ Preparation Phase

- [x] **Create `unified_validator.py`**: ✅ Created with SSOT, imports, tracker, session, refactor, consolidation, and queue validation categories.
- [x] **Verify `unified_monitor.py`**: ✅ Confirmed working - handles queue, service, disk, agent, workspace, and coverage monitoring.
- [x] **Verify `unified_analyzer.py`**: ✅ Confirmed working - handles repository, structure, file, consolidation, and overlap analysis.
- [x] **Create Archival Directory**: ✅ `tools/deprecated/consolidated_phase1` exists.

---

## 🚀 Phase 1: Monitoring Consolidation (108 candidates)

**Target Tool**: `unified_monitor.py`

- [x] **Batch 1: Status & Health Checks** ✅ COMPLETE
    - `captain_check_agent_status.py` - Already archived in `deprecated/consolidated_2025-12-05/`
    - `workspace_health_monitor.py` - Archived to `deprecated/consolidated_phase1/`
    - Service health monitoring consolidated in `unified_monitor.py`
- [x] **Batch 2: Queue & Infrastructure** ✅ COMPLETE
    - `check_queue_status.py`, `check_queue_issue.py` - Archived to `deprecated/consolidated_phase1/`
    - `check_service_status.py` - Archived to `deprecated/consolidated_phase1/`
    - Queue/service logic consolidated in `unified_monitor.py`
- [x] **Batch 3: Recovery Triggers** ✅ COMPLETE
    - `status_monitor_recovery_trigger.py` - Archived to `deprecated/consolidated_phase1/`
    - Resume trigger functionality in `unified_monitor.py --trigger-resume`

**Status**: ✅ PHASE 1 COMPLETE - Use `python3 unified_monitor.py --category all` for all monitoring.

---

## 🛡️ Phase 2: Validation Consolidation (73 candidates)

**Target Tool**: `unified_validator.py`

- [ ] **Batch 1: SSOT & Config**
    - Consolidate `ssot_config_validator.py`
    - Consolidate `validate_trackers.py`
- [ ] **Batch 2: Code & Imports**
    - Consolidate `validate_imports.py`
    - Consolidate `check_active_theme_and_deploy_css.py` (validation parts)
- [ ] **Batch 3: System Verification**
    - Consolidate `verify_file_usage_enhanced.py`
    - Consolidate `check_system_readiness.py`

**Action**: Implement checks in `unified_validator.py`, verify, archive.

---

## 🧠 Phase 3: Analysis Consolidation (218 candidates)

**Target Tool**: `unified_analyzer.py`

- [ ] **Batch 1: Reporting & Metrics**
    - Consolidate `tech_debt_ci_summary.py`
    - Consolidate `generate_weekly_progression_report.py`
- [ ] **Batch 2: Codebase Scanning**
    - Consolidate `projectscanner_modular_reports.py`
    - Consolidate `analyze_project_structure.py` logic
- [ ] **Batch 3: Specialized Audits**
    - Consolidate `audit_wordpress_blogs.py`
    - Consolidate `analyze_documentation_sprawl.py`

**Action**: Implement analyzers in `unified_analyzer.py`, verify, archive.

---

## 🧹 Phase 4: Cleanup & Finalization

- [ ] **Update Toolbelt**: Ensure `toolbelt.py` points to the unified tools.
- [ ] **Documentation**: Update `README.md` to reference the unified tools.
- [ ] **Final Archive**: Move all 399 tools to `tools/deprecated/consolidated_phase1`.
- [ ] **Verify Tool Count**: Run `count_tools.py` (or `ls | wc -l`) to confirm reduction.

---

## 📝 Execution Log

*   [x] Plan Created - 2025-12-25
*   [x] `unified_validator.py` Created - 2025-12-25
*   [x] Phase 1 Started - 2025-12-25
*   [x] Phase 1 Complete - 2025-12-25
    - Batch 1: Archived `workspace_health_monitor.py` (functionality in `unified_monitor.py`)
    - Batch 2: Archived `check_queue_status.py`, `check_queue_issue.py`, `check_service_status.py`
    - Batch 3: Archived `status_monitor_recovery_trigger.py`
*   [ ] Phase 2 Started
*   [ ] Phase 2 Complete
*   [ ] Phase 3 Started
*   [ ] Phase 3 Complete
*   [ ] Cleanup Complete
