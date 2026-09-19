# Tool Surfaces & Overlap Map

_Generated: 2025-12-21 12:24 UTC_

**Freshness notice (reviewed 2026-07-03):** This map is useful for locating overlapping tool surfaces, but some counts and failing-entry notes predate SWARM-016 and later registry cleanup. Use `docs/architecture/DOMAIN_MODEL.md`, `docs/root/MASTER_TASK_LOG.md`, `mcp_servers/all_mcp_servers.json`, and `docs/TOOLS_V2_DISABLED_REGISTRY_ENTRIES.md` for current canonical status.

This document maps **where “tool capabilities” live** in this repository, and where the **same capability is exposed through multiple surfaces** (MCP vs Toolbelt V2 vs legacy CLI vs app/runtime code).

**Canonical source-of-truth files (start here):**

- **MCP server inventory**: `mcp_servers/all_mcp_servers.json`
- **Toolbelt V2 registry (internal adapters)**: `tools_v2/tool_registry.lock.json`
- **Legacy CLI registry (flags → modules)**: `tools/toolbelt_registry.py`

## Tool surfaces in this repo

- **MCP servers** (`mcp_servers/*_server.py`): JSON-RPC tools exposed externally.
- **Toolbelt V2** (`tools_v2/tool_registry.lock.json`): in-process adapter tools keyed like `msg.send`.
- **Legacy CLI toolbelt** (`tools/toolbelt_registry.py`): CLI flags map to many scripts/unified tools.
- **Standalone scripts** (`tools/*.py`): many utilities exist outside the registries (some are referenced by the registries; many are “direct-run only”).
- **Family Focus Board runtime** (`apps/*`, `packages/*`): product code (API/Web/shared) with its own command surface via `package.json` scripts.

## MCP servers (external tool surface)

### `git-operations`
- **Source**: `mcp_servers/git_operations_server.py`
- **`check_file_history`**: Check git history for a specific file
- **`get_recent_commits`**: Get recent git commits
- **`validate_commit`**: Validate a commit exists and get details
- **`verify_git_work`**: Verify claimed work against git commits
- **`verify_work_exists`**: Verify that work exists in today's git commits

### `swarm-brain`
- **Source**: `mcp_servers/swarm_brain_server.py`
- **`get_agent_notes`**: Get agent personal notes
- **`record_decision`**: Record a decision to Swarm Brain
- **`search_swarm_knowledge`**: Search Swarm Brain knowledge base
- **`share_learning`**: Share a learning to Swarm Brain knowledge base
- **`take_note`**: Take a personal note (agent-specific)

### `swarm-messaging`
- **Source**: `mcp_servers/messaging_server.py`
- **`broadcast_message`**: Broadcast a message to all agents
- **`get_agent_coordinates`**: Get coordinates and status information for all agents
- **`send_agent_message`**: Send message to a specific agent via PyAutoGUI coordinates

### `task-manager`
- **Source**: `mcp_servers/task_manager_server.py`
- **`add_task_to_inbox`**: Add a task to the INBOX section of `docs/root/MASTER_TASK_LOG.md`
- **`get_tasks`**: Get tasks from `docs/root/MASTER_TASK_LOG.md`
- **`mark_task_complete`**: Mark a task as complete in `docs/root/MASTER_TASK_LOG.md`
- **`move_task_to_waiting`**: Move a task to WAITING ON section

### `v2-compliance`
- **Source**: `mcp_servers/v2_compliance_server.py`
- **`check_function_size`**: Check function size against V2 limit
- **`check_v2_compliance`**: Check a file for V2 compliance
- **`get_v2_exceptions`**: Get approved V2 compliance exceptions
- **`validate_file_size`**: Validate file size against V2 limit

### `website-manager`
- **Source**: `mcp_servers/website_manager_server.py`
- **`add_page_to_menu`**: Add a page to WordPress menu
- **`create_blog_post`**: Create a blog post for a site
- **`create_report_page`**: Create a report page for a site
- **`create_wordpress_page`**: Create a new WordPress page
- **`deploy_file_to_wordpress`**: Deploy a file to a WordPress site
- **`generate_image_prompts`**: Generate image prompts for website design
- **`list_wordpress_pages`**: List all pages on WordPress site
- **`purge_wordpress_cache`**: Purge WordPress cache

## Family Focus Board (runtime surface)

This repo also contains a TypeScript monorepo for the Family Focus Board product. This is **not an agent tool surface**, but it is an important “capability surface” in the repository (API routes, realtime events, and shared timer state machine).

- **API service**: `apps/api`
  - entrypoint: `apps/api/src/server.ts`
  - scripts: `dev`, `start`, `db:migrate`, `db:seed` (see `apps/api/package.json`)
- **Web app**: `apps/web` (Next.js)
  - scripts: `dev`, `build`, `start` (see `apps/web/package.json`)
- **Shared library**: `packages/shared`
  - timer state machine + types shared across API/web (see `packages/shared/src/`)

## Toolbelt V2 registry (internal adapter tool surface)

- **Registry**: `tools_v2/tool_registry.lock.json`
- **Lockfile entries**: 91 (`tools` keys)
- **Registry `count`**: 87 (typically “loadable/healthy” tools at generation time; a mismatch indicates stale/broken entries or partial generation)

### Registry health (known failing entries)
- **`agent.points`** — _IMPORT ERROR_ (AttributeError: module 'tools_v2.categories.session_tools' has no attribute 'PointsCalculatorTool') — `tools_v2.categories.session_tools:PointsCalculatorTool`
- **`brain.get`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class GetAgentNotesTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.swarm_brain_tools:GetAgentNotesTool`
- **`brain.note`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class TakeNoteTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.swarm_brain_tools:TakeNoteTool`
- **`brain.search`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class SearchKnowledgeTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.swarm_brain_tools:SearchKnowledgeTool`
- **`brain.session`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class LogSessionTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.swarm_brain_tools:LogSessionTool`
- **`brain.share`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class ShareLearningTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.swarm_brain_tools:ShareLearningTool`
- **`discord.health`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class DiscordBotHealthTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.discord_tools:DiscordBotHealthTool`
- **`discord.start`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class DiscordBotStartTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.discord_tools:DiscordBotStartTool`
- **`discord.test`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class DiscordTestMessageTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.discord_tools:DiscordTestMessageTool`
- **`infra.roi_calc`** — _IMPORT ERROR_ (AttributeError: module 'tools_v2.categories.infrastructure_tools' has no attribute 'ROICalculatorTool') — `tools_v2.categories.infrastructure_tools:ROICalculatorTool`
- **`mem.imports`** — _IMPORT ERROR_ (AttributeError: module 'tools_v2.categories.memory_safety_adapters' has no attribute 'ImportValidatorTool') — `tools_v2.categories.memory_safety_adapters:ImportValidatorTool`
- **`msgtask.fingerprint`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class TaskFingerprintTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.message_task_tools:TaskFingerprintTool`
- **`msgtask.ingest`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class MessageIngestTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.message_task_tools:MessageIngestTool`
- **`msgtask.parse`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class TaskParserTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.message_task_tools:TaskParserTool`
- **`obs.get`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class MetricsTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.observability_tools:MetricsTool`
- **`obs.health`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class SystemHealthTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.observability_tools:SystemHealthTool`
- **`obs.metrics`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class MetricsSnapshotTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.observability_tools:MetricsSnapshotTool`
- **`obs.slo`** — _IMPORT ERROR_ (TypeError: Can't instantiate abstract class SLOCheckTool without an implementation for abstract methods 'get_spec', 'validate') — `tools_v2.categories.observability_tools:SLOCheckTool`

### `agent_ops`
- **`agent.claim`**: Claim next available task from task queue — `tools_v2.categories.agent_ops_tools:ClaimTaskTool`
  - required: `agent_id`
  - optional: `priority, task_type`
- **`agent.status`**: Get comprehensive agent status and metrics — `tools_v2.categories.agent_ops_tools:AgentStatusTool`
  - required: `agent_id`
  - optional: `include_vector`

### `analysis`
- **`analysis.complexity`**: Analyze code complexity and cyclomatic metrics — `tools_v2.categories.analysis_tools:ComplexityTool`
  - required: `path`
  - optional: `format, threshold`
- **`analysis.duplicates`**: Detect duplicate code and consolidation opportunities — `tools_v2.categories.analysis_tools:DuplicationTool`
  - required: `path`
  - optional: `min_lines, report`
- **`analysis.scan`**: Run comprehensive project analysis scan — `tools_v2.categories.analysis_tools:ProjectScanTool`
  - optional: `enhanced`

### `business_intelligence`
- **`bi.metrics`**: Quick analysis of Python file metrics (lines, classes, functions, V2 compliance) — `tools_v2.categories.bi_tools:QuickMetricsTool`
  - required: `files`
  - optional: `json, pattern, summary, violations_only`
- **`bi.roi.optimize`**: Optimize task assignment using Markov chain and ROI analysis for all agents — `tools_v2.categories.bi_tools:MarkovROIOptimizerTool`
  - optional: `max_tasks, output_format`
- **`bi.roi.repo`**: Calculate ROI for GitHub repositories (keep vs archive decision) — `tools_v2.categories.bi_tools:RepoROICalculatorTool`
  - required: `repo_path`
  - optional: `detailed, output_format`
- **`bi.roi.task`**: Calculate task ROI (points, complexity, V2 impact, autonomy impact) — `tools_v2.categories.bi_tools:TaskROICalculatorTool`
  - required: `points, complexity`
  - optional: `autonomy_impact, v2_impact`

### `captain`
- **`captain.assign_mission`**: Create structured mission file in agent inbox — `tools_v2.categories.captain_tools:MissionAssignTool`
  - required: `agent_id, mission_title, mission_description`
  - optional: `complexity, dependencies, points, priority, roi`
- **`captain.calc_points`**: Calculate task points based on ROI metrics — `tools_v2.categories.captain_tools:PointsCalculatorTool`
  - required: `task_type`
  - optional: `complexity, custom_multiplier, impact, time_saved`
- **`captain.cycle_report`**: Generate Captain's cycle activity report — `tools_v2.categories.captain_tools:CycleReportTool`
  - required: `cycle_number`
  - optional: `agents_activated, messages_sent, missions_assigned, notes, points_awarded`
- **`captain.deliver_gas`**: Send PyAutoGUI activation message to agent — `tools_v2.categories.captain_tools:GasDeliveryTool`
  - required: `agent_id, message`
  - optional: `priority`
- **`captain.git_verify`**: Verify git commits for work attribution — `tools_v2.categories.captain_tools:GitVerifyTool`
  - required: `commit_hash`
  - optional: `show_diff, show_stat`
- **`captain.integrity_check`**: Verify work claims with git history (Entry #025) — `tools_v2.categories.captain_tools:IntegrityCheckTool`
  - required: `agent_id, claimed_work`
  - optional: `search_terms`
- **`captain.markov_optimize`**: Use Markov optimizer for ROI-based task selection — `tools_v2.categories.captain_tools:MarkovOptimizerTool`
  - required: `tasks`
  - optional: `agent_count, time_budget`
- **`captain.status_check`**: Check all agent status files to detect idle agents — `tools_v2.categories.captain_tools:StatusCheckTool`
  - optional: `agents, threshold_hours`
- **`captain.update_leaderboard`**: Update agent leaderboard with points, achievements, and session tracking — `tools_v2.categories.captain_tools:LeaderboardUpdateTool`
  - optional: `achievement, agent_id, points, session_date, updates`
- **`captain.verify_work`**: Verify completed work with git commits and file checks — `tools_v2.categories.captain_tools:WorkVerifyTool`
  - required: `agent_id, work_description`
  - optional: `commit_hash, files_changed`

### `compliance`
- **`comp.check`**: Check code against project policies and standards — `tools_v2.categories.compliance_tools:PolicyCheckTool`
  - required: `path`
  - optional: `policy, strict`
- **`comp.history`**: View compliance history and trend analysis — `tools_v2.categories.compliance_tools:ComplianceHistoryTool`
  - optional: `agent_id, days, format`

### `config`
- **`config.check-imports`**: Check files importing configuration — `tools_v2.categories.config_tools:CheckConfigImportsAdapter`
  - required: `config_file`
- **`config.list-sources`**: List all configuration sources — `tools_v2.categories.config_tools:ListConfigSourcesAdapter`
  - optional: `detail`
- **`config.validate-ssot`**: Validate config SSOT compliance — `tools_v2.categories.config_tools:ValidateConfigSSOTAdapter`

### `consciousness`
- **`swarm.pulse`**: Real-time view of entire swarm activity (MASTERPIECE TOOL) — `tools_v2.categories.swarm_consciousness:SwarmPulseTool`
  - optional: `agent_id, mode, refresh`

### `coordination`
- **`coord.check-patterns`**: Check swarm brain for coordination patterns — `tools_v2.categories.coordination_tools:CheckCoordinationPatternsAdapter`
- **`coord.find-expert`**: Find domain expert agent for Pattern #5 coordination — `tools_v2.categories.coordination_tools:FindDomainExpertAdapter`
  - required: `domain`
- **`coord.request-review`**: Request expert review (Pattern #5) — `tools_v2.categories.coordination_tools:RequestExpertReviewAdapter`
  - required: `domain, topic, agent`

### `docs`
- **`docs.export`**: Export agent knowledge base to JSON — `tools_v2.categories.docs_tools:DocsExportTool`
  - required: `agent_id`
  - optional: `output_file`
- **`docs.search`**: Semantic search across project documentation — `tools_v2.categories.docs_tools:DocsSearchTool`
  - required: `query`
  - optional: `agent_id, results`

### `health`
- **`health.ping`**: Quick health check of project status — `tools_v2.categories.health_tools:HealthPingTool`
  - optional: `check_agents, check_snapshots`
- **`health.snapshot`**: Create or update project snapshot for captain tracking — `tools_v2.categories.health_tools:SnapshotTool`
  - optional: `update, validate`

### `infrastructure`
- **`infra.extract_planner`**: Analyze file and suggest modular extraction plan — `tools_v2.categories.infrastructure_tools:ModuleExtractorPlannerTool`
  - required: `file`
- **`infra.file_lines`**: Count lines in file(s) for V2 compliance verification — `tools_v2.categories.infrastructure_tools:FileLineCounterTool`
  - required: `files`
- **`infra.orchestrator_scan`**: Scan all orchestrator files for V2 violations and performance bottlenecks — `tools_v2.categories.infrastructure_tools:OrchestratorScanTool`

### `integration`
- **`integration.check-imports`**: Check import dependencies for issues — `tools_v2.categories.integration_tools:CheckImportDependenciesAdapter`
  - required: `file`
- **`integration.find-duplicates`**: Find duplicate functionality across codebase — `tools_v2.categories.integration_tools:FindDuplicateFunctionalityAdapter`
  - required: `pattern`
  - optional: `path`
- **`integration.find-opportunities`**: Analyze codebase for integration opportunities — `tools_v2.categories.integration_tools:FindIntegrationOpportunitiesAdapter`
  - optional: `focus`
- **`integration.find-ssot-violations`**: Find potential SSOT violations in codebase — `tools_v2.categories.integration_tools:FindSSOTViolationsAdapter`
  - optional: `path`

### `intelligent_advisor`
- **`advisor.guide`**: 💡 Get real-time execution guidance during task — `tools_v2.categories.intelligent_mission_advisor_adapter:RealtimeGuidanceTool`
  - required: `agent_id, current_step`
  - optional: `task_context`
- **`advisor.recommend`**: 🧠 MASTERPIECE: AI-powered mission advisor - your personal senior engineer copilot — `tools_v2.categories.intelligent_mission_advisor_adapter:MissionAdvisorTool`
  - required: `agent_id`
  - optional: `avoid_duplication, context, prefer_high_roi`
- **`advisor.swarm`**: 📊 Analyze swarm state and identify opportunities — `tools_v2.categories.intelligent_mission_advisor_adapter:SwarmAnalyzerTool`
  - required: `agent_id`
- **`advisor.validate`**: 🛡️ Validate Captain's orders (prevent phantom tasks - Pattern #1!) — `tools_v2.categories.intelligent_mission_advisor_adapter:OrderValidatorTool`
  - required: `agent_id, order_file`

### `memory_safety`
- **`mem.handles`**: Check for unclosed file handles (resource leak detection) — `tools_v2.categories.memory_safety_adapters:FileHandleCheckTool`
  - optional: `target_path`
- **`mem.leaks`**: Detect potential memory leaks (unbounded structures, missing size checks) — `tools_v2.categories.memory_safety_adapters:MemoryLeakDetectorTool`
  - optional: `target_path`
- **`mem.scan`**: Scan for unbounded data structures that could grow indefinitely — `tools_v2.categories.memory_safety_adapters:UnboundedScanTool`
  - optional: `target_path`
- **`mem.verify`**: Verify files exist (prevent phantom tasks) — `tools_v2.categories.memory_safety_adapters:FileVerificationTool`
  - required: `file_list`

### `messaging`
- **`msg.broadcast`**: Broadcast message to all agents — `tools_v2.categories.messaging_tools:BroadcastTool`
  - required: `message`
  - optional: `priority`
- **`msg.inbox`**: Check agent inbox, optionally with semantic search — `tools_v2.categories.messaging_tools:InboxCheckTool`
  - required: `agent_id`
  - optional: `search_query`
- **`msg.send`**: Send message to a specific agent via PyAutoGUI — `tools_v2.categories.messaging_tools:SendMessageTool`
  - required: `agent_id, message`
  - optional: `priority, tags`

### `onboarding`
- **`onboard.hard`**: Hard onboarding with complete reset (DESTRUCTIVE - requires --yes) — `tools_v2.categories.onboarding_tools:HardOnboardTool`
  - required: `agent_id, message`
  - optional: `confirm`
- **`onboard.soft`**: Soft onboarding with 3-step session cleanup protocol — `tools_v2.categories.onboarding_tools:SoftOnboardTool`
  - required: `agent_id, message`
  - optional: `priority`

### `oss`
- **`oss.clone`**: Clone external OSS project — `tools_v2.categories.oss_tools:OSSCloneTool`
  - required: `github_url`
  - optional: `project_name`
- **`oss.import`**: Import GitHub issues as tasks — `tools_v2.categories.oss_tools:OSSImportIssuesTool`
  - required: `project_id`
  - optional: `labels, max_tasks`
- **`oss.issues`**: Fetch GitHub issues from OSS project — `tools_v2.categories.oss_tools:OSSFetchIssuesTool`
  - required: `project_id`
  - optional: `labels`
- **`oss.portfolio`**: Generate OSS contribution portfolio — `tools_v2.categories.oss_tools:OSSPortfolioTool`
  - optional: `format`
- **`oss.status`**: Get OSS contribution status — `tools_v2.categories.oss_tools:OSSStatusTool`

### `session`
- **`session.cleanup`**: Automate complete session cleanup (passdown, devlog, swarm brain, status) — `tools_v2.categories.session_tools:SessionCleanupTool`
  - required: `agent_id`
  - optional: `auto_devlog, update_status`
- **`session.passdown`**: Create or read session passdown.json — `tools_v2.categories.session_tools:PassdownTool`
  - required: `agent_id`
  - optional: `action, data`

### `testing`
- **`test.coverage`**: Run tests with coverage analysis — `tools_v2.categories.testing_tools:CoverageReportTool`
  - optional: `html, min_coverage, path`
- **`test.mutation`**: Run mutation testing quality gate — `tools_v2.categories.testing_tools:MutationGateTool`
  - optional: `threshold`

### `v2`
- **`v2.check`**: Check files for V2 compliance violations (≤400 lines) — `tools_v2.categories.v2_tools:V2CheckTool`
  - required: `path`
  - optional: `fix, recursive`
- **`v2.report`**: Generate comprehensive V2 compliance report — `tools_v2.categories.v2_tools:V2ReportTool`
  - optional: `format, path`

### `validation`
- **`val.flags`**: Check or set feature flags — `tools_v2.categories.validation_tools:FeatureFlagTool`
  - optional: `action, feature`
- **`val.report`**: Generate validation report for all systems — `tools_v2.categories.validation_tools:ValidationReportTool`
- **`val.rollback`**: Emergency rollback features — `tools_v2.categories.validation_tools:RollbackTool`
  - optional: `feature`
- **`val.smoke`**: Run smoke tests for system validation — `tools_v2.categories.validation_tools:SmokeTestTool`
  - optional: `system`

### `vector`
- **`vector.context`**: Get intelligent context for a task from vector database — `tools_v2.categories.vector_tools:TaskContextTool`
  - required: `agent_id, task`
  - optional: `limit`
- **`vector.index`**: Index agent work to vector database for future retrieval — `tools_v2.categories.vector_tools:IndexWorkTool`
  - required: `agent_id`
  - optional: `file, inbox, work_type`
- **`vector.search`**: Semantic search across all indexed content — `tools_v2.categories.vector_tools:VectorSearchTool`
  - required: `query`
  - optional: `agent_id, collection, limit`

### `workflow`
- **`mission.claim`**: Claim next high-value mission from task queue — `tools_v2.categories.workflow_tools:MissionClaimTool`
  - required: `agent_id`
  - optional: `min_points, sort_by`
- **`msg.cleanup`**: Clean old messages from inbox (archive or delete) — `tools_v2.categories.workflow_tools:InboxCleanupTool`
  - required: `agent_id`
  - optional: `action, days_old, dry_run`
- **`workflow.roi`**: Calculate ROI (return on investment) for task prioritization — `tools_v2.categories.workflow_tools:ROICalculatorTool`
  - required: `task_description`
  - optional: `estimated_hours, points_estimate`

## Legacy CLI toolbelt registry

- **Registry**: `tools/toolbelt_registry.py`
- **Registered tools**: 87
  - Note: this is the “flags → module” mapping used by the legacy CLI entrypoints; it overlaps heavily with `tools/*.py` scripts.

### `analysis`
- **`analyze-dreamvault`**: DreamVault-specific duplicate detection (consolidated into unified_analyzer) — `tools.unified_analyzer:main`
  - flags: `--analyze-dreamvault --dreamvault-dup`
- **`analyze-duplicates`**: General-purpose duplicate file analyzer for any repository (consolidated into unified_analyzer) — `tools.unified_analyzer:main`
  - flags: `--analyze-duplicates --dup-analyze`
- **`complexity`**: Analyze code complexity metrics — `tools.unified_analyzer:main`
  - flags: `--complexity -c`
- **`duplication`**: Find duplicate code across project — `tools.duplication_analyzer:main`
  - flags: `--duplication --dup`
- **`memory-scan`**: Detect unbounded caches, lists, and memory leaks — `tools.memory_leak_scanner:main`
  - flags: `--memory-scan --memleak`
- **`merge-duplicates`**: Compare duplicate files and generate merge suggestions (Agent-3's tool) — `tools.merge_duplicate_file_functionality:main`
  - flags: `--merge-duplicates --dup-merge`
- **`pattern-suggest`**: Suggest consolidation patterns for refactoring — `tools.refactoring_suggestion_engine:main`
  - flags: `--pattern-suggest --suggest-pattern`
- **`real-violations`**: Verify actual V2 violations (intelligent verification) — `tools.real_violation_scanner:main`
  - flags: `--real-violations --real-v2`
- **`refactor`**: Get intelligent refactoring suggestions — `tools.refactoring_suggestion_engine:main`
  - flags: `--refactor -r`
- **`refactor-analyze`**: Smart refactoring suggestions based on file analysis — `tools.unified_validator:main`
  - flags: `--refactor-analyze --analyze-refactor`
- **`repo-batch`**: Unified repository and project analysis (consolidates repo_batch_analyzer and 7 other tools) — `tools.repository_analyzer:main`
  - flags: `--repo-batch --batch-analyze --repository-analyzer`
- **`repo-overlap`**: Analyze repository overlaps for consolidation (consolidated into repository_analyzer) — `tools.repository_analyzer:main`
  - flags: `--repo-overlap --overlap`
- **`resolve-duplicates`**: Detailed duplicate resolution analysis and planning (Agent-2's tool) — `tools.resolve_dreamvault_duplicates:main`
  - flags: `--resolve-duplicates --dup-resolve`
- **`scan`**: Scan project structure and generate analysis — `tools.project_scan:main`
  - flags: `--scan -s`
- **`technical-debt`**: Analyze technical debt markers and consolidation opportunities — `tools.technical_debt_analyzer:main`
  - flags: `--technical-debt --debt`
- **`unified-analyzer`**: Consolidated analysis tool - repository, project structure, file analysis, consolidation detection, overlaps (consolidates multiple analysis tools) — `tools.unified_analyzer:main`
  - flags: `--unified-analyzer --analyze --analyzer`

### `compliance`
- **`dashboard`**: Open compliance tracking dashboard — `tools.compliance_dashboard:main`
  - flags: `--dashboard -d`
- **`history`**: Track compliance history over time — `tools.compliance_history_tracker:main`
  - flags: `--history`
- **`ssot-validate`**: Check documentation-code alignment (prevent SSOT violations) — `tools.ssot_validator:main`
  - flags: `--ssot-validate --ssot-check`
- **`v2-batch`**: Quick V2 compliance check for multiple files (uses modular v2_checker_cli) — `tools.v2_compliance_checker:main`
  - flags: `--v2-batch --batch`
- **`v2-check`**: Check V2 compliance violations — `tools.v2_compliance_checker:main`
  - flags: `--v2-check --v2 -v`

### `coordination`
- **`agent-orient`**: Agent orientation and onboarding — `tools.agent_orient:main`
  - flags: `--agent-orient --orient`
- **`agent-status`**: Unified agent status monitoring (consolidates 15+ tools including quick check, snapshot, staleness) — `tools.communication.agent_status_validator:main`
  - flags: `--agent-status --status-check`
- **`agent-task-finder`**: Find tasks assigned to agents — `tools.agent_task_finder:main`
  - flags: `--agent-task-finder --find-tasks`
- **`captain-find-idle`**: Find agents that are idle — `tools.captain_find_idle_agents:main`
  - flags: `--find-idle --idle-agents`
- **`captain-next-task`**: Pick next task for agents — `tools.captain_next_task_picker:main`
  - flags: `--next-task --pick-task`
- **`markov-optimize`**: Get optimal task assignments using Markov Chain analysis (integrated with swarm) — `tools.markov_swarm_integration:main`
  - flags: `--markov-optimize --markov --optimize-task`
- **`mission-control`**: THE masterpiece - Runs all 5 workflow steps, generates conflict-free mission brief — `tools.mission_control:main`
  - flags: `--mission-control --mission --mc`
- **`orchestrate`**: The Gas Station - Autonomous swarm coordination and gas delivery — `tools.swarm_orchestrator:run_orchestrator`
  - flags: `--orchestrate --gas-station --swarm`
- **`swarm-brain`**: Easy Swarm Brain contributions (10min → 1min!) — `tools.swarm_brain_cli:main`
  - flags: `--swarm-brain --brain`
- **`system-inventory`**: Complete catalog of all systems, tools, integrations, and connections — `tools.swarm_system_inventory:main`
  - flags: `--system-inventory --inventory --what-do-we-have`
- **`unified-agent`**: Consolidated agent operations - orient, tasks, status, lifecycle, onboard (consolidates 12+ agent tools) — `tools.unified_agent:main`
  - flags: `--unified-agent --agent`
- **`unified-captain`**: Consolidated captain operations - inbox, coordination, monitoring, tasks, cleanup (consolidates 23+ captain tools) — `tools.unified_captain:main`
  - flags: `--unified-captain --captain`

### `git/github`
- **`fix-github-prs`**: One-command fix for GitHub PR issues — `tools.fix_github_prs:main`
  - flags: `--fix-github-prs --fix-prs`
- **`git-verify`**: Verify claimed work exists in git history — `tools.git_commit_verifier:main`
  - flags: `--git-verify --verify-commits`
- **`git-work-verify`**: Verify work in git history — `tools.git_work_verifier:main`
  - flags: `--git-work-verify --verify-work`
- **`github-pr-debug`**: Diagnose and fix GitHub PR creation issues — `tools.github_pr_debugger:main`
  - flags: `--github-pr-debug --pr-debug --debug-pr`
- **`spreadsheet-github`**: Spreadsheet-driven GitHub automation (create_issue, update_file, open_pr) using unified GitHub tools — `tools.spreadsheet_github_adapter:main`
  - flags: `--spreadsheet-github --sheet-github --spreadsheet`
- **`unified-github`**: Consolidated GitHub operations - pr, repo, merge, audit (consolidates 28+ GitHub tools) — `tools.unified_github:main`
  - flags: `--unified-github --github --gh`

### `infrastructure`
- **`infra-health`**: Monitor infrastructure health for automation reliability — `src.infrastructure.infrastructure_health_monitor:main`
  - flags: `--infra-health --infra`
- **`workspace-clean`**: Automated workspace cleanup (15min → 2min!) — `tools.workspace_auto_cleaner:main`
  - flags: `--workspace-clean --clean`
- **`workspace-health`**: Check workspace health (consolidates workspace_health_checker.py) — `tools.workspace_health_monitor:main`
  - flags: `--workspace-health --health`

### `messaging`
- **`fix-stuck`**: Fix stuck messages in queue — `tools.reset_stuck_messages:main`
  - flags: `--fix-stuck --unstuck`
- **`get-task`**: Claim next task from centralized task system (Step 1 of workflow) — `src.services.messaging_cli:main`
  - flags: `--get-task --next-task`
  - override_args: `['--get-next-task']`
- **`list-tasks`**: List all available tasks in queue — `src.services.messaging_cli:main`
  - flags: `--tasks --task-list`
  - override_args: `['--list-tasks']`
- **`message`**: Send messages to agents via messaging system — `src.services.messaging_cli:main`
  - flags: `--message-cli --msg`
- **`message-history`**: View recent agent message exchanges — `tools.agent_message_history:main`
  - flags: `--message-history --msg-history`
- **`queue-diagnose`**: Diagnose message queue issues — `tools.diagnose_message_queue:main`
  - flags: `--queue-diagnose --diagnose-queue`
- **`queue-status`**: Unified messaging infrastructure validator - checks queue status, persistence, and configuration (consolidates check_queue_status.py) — `tools.communication.messaging_infrastructure_validator:main`
  - flags: `--queue-status --q-status`

### `other`
- **`arch-review`**: Request/provide expert architecture reviews — `tools.architecture_review:main`
  - flags: `--arch-review --review`
- **`auto-track`**: Auto-update status.json from git commits — `tools.progress_auto_tracker:main`
  - flags: `--auto-track --track-progress`
- **`check-imports`**: Validate import chains and find missing modules — `tools.import_chain_validator:main`
  - flags: `--check-imports --import-check`
- **`check-integration`**: Unified integration validator - checks integration issues, health, and readiness (consolidates check_integration_issues.py + integration_health_checker.py) — `tools.communication.integration_validator:main`
  - flags: `--check-integration --int-check`
- **`consolidation-exec`**: Execute repository consolidations — `tools.consolidation_executor:main`
  - flags: `--consolidation-exec --consolidate`
- **`consolidation-status`**: Track GitHub consolidation progress and identify next opportunities — `tools.consolidation_progress_tracker:main`
  - flags: `--consolidation-status --consolidation-track`
- **`devlog-post`**: Auto-post devlogs to Discord (10min → 30sec!) — `tools.devlog_poster:main`
  - flags: `--devlog-post --post-devlog`
- **`discord-start`**: Start Discord bot system — `tools.start_discord_system:main`
  - flags: `--discord-start --start-discord`
- **`discord-verify`**: Verify Discord bot is running — `tools.check_service_status:main`
  - flags: `--discord-verify --verify-discord`
- **`execute-cleanup`**: Execute cleanup operations for DreamVault (Agent-2's tool) — `tools.execute_dreamvault_cleanup:main`
  - flags: `--execute-cleanup --cleanup`
- **`extract-module`**: Extract functions/classes into focused modules — `tools.module_extractor:main`
  - flags: `--extract-module --extract`
- **`extraction-roadmap`**: Auto-generate extraction plans (30min → 5min!) — `tools.extraction_roadmap_generator:main`
  - flags: `--extraction-roadmap --roadmap`
- **`functionality`**: Verify functionality preservation — `tools.functionality_verification:main`
  - flags: `--functionality --verify`
- **`integration-validate`**: Comprehensive system integration validation (C-048-5) — `tools.communication.integration_validator:main`
  - flags: `--integration-validate --int-val`
- **`leaderboard`**: Show agent performance leaderboard — `tools.autonomous_leaderboard:main`
  - flags: `--leaderboard -l`
- **`line-count`**: Quickly count lines in files for V2 compliance — `tools.quick_linecount:main`
  - flags: `--line-count --count-lines --lc`
- **`linecount`**: Quick line count for files/directories — `tools.quick_linecount:main`
  - flags: `--linecount --lines`
- **`pattern-extract`**: Semi-automated code pattern extraction (30min → 5min!) — `tools.extraction_roadmap_generator:main`
  - flags: `--pattern-extract --extract`
- **`pattern-validator`**: Validate architectural patterns (Agent-2's tool) — `tools.architecture_review:main`
  - flags: `--validate-patterns --patterns`
- **`qa-checklist`**: Automated QA validation checklist — `tools.qa_validation_checklist:main`
  - flags: `--qa-checklist --qa`
- **`review-integration`**: Comprehensive integration review for merged repos (Agent-2's tool) — `tools.review_dreamvault_integration:main`
  - flags: `--review-integration --int-review`
- **`soft-onboard`**: Soft onboard agents (6-step session cleanup protocol) — `tools.soft_onboard_cli:main`
  - flags: `--soft-onboard --soft`
- **`task`**: Quick task management (get/list/status/complete) — `tools.task_cli:main`
  - flags: `--task -t`
- **`unified-cleanup`**: Consolidated cleanup operations - archive, delete, cleanup, disk (consolidates 15+ cleanup/archive tools) — `tools.unified_cleanup:main`
  - flags: `--unified-cleanup --cleanup`
- **`unified-discord`**: Consolidated Discord operations - system, test, verify, upload (consolidates 14+ Discord tools) — `tools.unified_discord:main`
  - flags: `--unified-discord --discord`
- **`unified-validator`**: Consolidated validation tool - SSOT config, imports, refactor status, session transition, tracker status (consolidates 19+ validation tools) — `tools.unified_validator:main`
  - flags: `--unified-validator --validate --validator`
- **`unified-verifier`**: Consolidated verification tool - repo, merge, file, cicd, credentials (consolidates 25+ verification tools) — `tools.unified_verifier:main`
  - flags: `--unified-verifier --verify`
- **`validate-imports`**: Validate import statements and dependencies — `tools.validate_imports:main`
  - flags: `--validate-imports --imports`
- **`verify-cicd`**: Verify CI/CD pipelines for merged repositories via unified verifier (category=cicd, action=merged) — `tools.unified_verifier:main`
  - flags: `--verify-cicd --cicd-verify`
  - override_args: `['--category', 'cicd', '--action', 'merged']`
- **`verify-complete`**: Verify work completion before sending messages — `tools.work_completion_verifier:main`
  - flags: `--verify-complete --verify-work`
- **`verify-phase1`**: Verify Phase 1 consolidation repos — `tools.verify_phase1_repos:main`
  - flags: `--verify-phase1 --phase1-verify`

### `testing`
- **`coverage`**: Analyze test coverage gaps and usage patterns — `tools.coverage_analyzer:main`
  - flags: `--coverage --test-coverage`
- **`coverage-check`**: Validate test coverage meets thresholds (uses coverage analyzer) — `tools.coverage_analyzer:main`
  - flags: `--coverage-check --cov`
- **`extension-test`**: VSCode extension testing with coverage — `tools.extension_test_runner:main`
  - flags: `--extension-test --ext-test`
- **`test-health`**: Monitor test suite health via unified verifier (category=file, action=comprehensive) — `tools.unified_verifier:main`
  - flags: `--test-health --health`
  - override_args: `['--category', 'file', '--action', 'comprehensive']`
- **`test-pyramid`**: Analyze test distribution vs 60/30/10 target — `tools.test_pyramid_analyzer:main`
  - flags: `--test-pyramid --pyramid`
- **`test-usage-analyzer`**: Identify unused functionality via test coverage analysis - finds methods only tested but never used in production — `tools.test_usage_analyzer:main`
  - flags: `--test-usage-analyzer --test-usage --unused-via-tests`

### `website`
- **`unified-wordpress`**: Consolidated WordPress operations - deploy, theme, debug, admin (consolidates 16+ WordPress tools) — `tools.unified_wordpress:main`
  - flags: `--unified-wordpress --wordpress --wp`

## Overlap hot-spots (same capability exposed in multiple surfaces)

### `analysis`
- **Toolbelt V2**: 3 tools
  - `analysis.complexity`
  - `analysis.duplicates`
  - `analysis.scan`
- **Legacy toolbelt**: 16 tools
  - `analyze-dreamvault`
  - `analyze-duplicates`
  - `complexity`
  - `duplication`
  - `memory-scan`
  - `merge-duplicates`
  - `pattern-suggest`
  - `real-violations`
  - `refactor`
  - `refactor-analyze`
  - `repo-batch`
  - `repo-overlap`
  - `resolve-duplicates`
  - `scan`
  - `technical-debt`
  - `unified-analyzer`

### `compliance`
- **MCP**: 4 tools
  - `v2-compliance:check_function_size`
  - `v2-compliance:check_v2_compliance`
  - `v2-compliance:get_v2_exceptions`
  - `v2-compliance:validate_file_size`
- **Toolbelt V2**: 2 tools
  - `comp.check`
  - `comp.history`
- **Legacy toolbelt**: 5 tools
  - `dashboard`
  - `history`
  - `ssot-validate`
  - `v2-batch`
  - `v2-check`

### `coordination`
- **Toolbelt V2**: 3 tools
  - `coord.check-patterns`
  - `coord.find-expert`
  - `coord.request-review`
- **Legacy toolbelt**: 12 tools
  - `agent-orient`
  - `agent-status`
  - `agent-task-finder`
  - `captain-find-idle`
  - `captain-next-task`
  - `markov-optimize`
  - `mission-control`
  - `orchestrate`
  - `swarm-brain`
  - `system-inventory`
  - `unified-agent`
  - `unified-captain`

### `git/github`
- **MCP**: 5 tools
  - `git-operations:check_file_history`
  - `git-operations:get_recent_commits`
  - `git-operations:validate_commit`
  - `git-operations:verify_git_work`
  - `git-operations:verify_work_exists`
- **Legacy toolbelt**: 6 tools
  - `fix-github-prs`
  - `git-verify`
  - `git-work-verify`
  - `github-pr-debug`
  - `spreadsheet-github`
  - `unified-github`

### `infrastructure`
- **Toolbelt V2**: 3 tools
  - `infra.extract_planner`
  - `infra.file_lines`
  - `infra.orchestrator_scan`
- **Legacy toolbelt**: 3 tools
  - `infra-health`
  - `workspace-clean`
  - `workspace-health`

### `messaging`
- **MCP**: 3 tools
  - `swarm-messaging:broadcast_message`
  - `swarm-messaging:get_agent_coordinates`
  - `swarm-messaging:send_agent_message`
- **Toolbelt V2**: 3 tools
  - `msg.broadcast`
  - `msg.inbox`
  - `msg.send`
- **Legacy toolbelt**: 7 tools
  - `fix-stuck`
  - `get-task`
  - `list-tasks`
  - `message`
  - `message-history`
  - `queue-diagnose`
  - `queue-status`

### `testing`
- **Toolbelt V2**: 2 tools
  - `test.coverage`
  - `test.mutation`
- **Legacy toolbelt**: 6 tools
  - `coverage`
  - `coverage-check`
  - `extension-test`
  - `test-health`
  - `test-pyramid`
  - `test-usage-analyzer`

### `website`
- **MCP**: 8 tools
  - `website-manager:add_page_to_menu`
  - `website-manager:create_blog_post`
  - `website-manager:create_report_page`
  - `website-manager:create_wordpress_page`
  - `website-manager:deploy_file_to_wordpress`
  - `website-manager:generate_image_prompts`
  - `website-manager:list_wordpress_pages`
  - `website-manager:purge_wordpress_cache`
- **Legacy toolbelt**: 1 tools
  - `unified-wordpress`

## High-signal direct overlaps to review

- **Messaging**: MCP (`send_agent_message`, `broadcast_message`) vs Toolbelt V2 (`msg.send`, `msg.broadcast`) vs Legacy (`message`, `queue-*`).
- **V2/Compliance**: MCP (`check_v2_compliance`, `validate_file_size`, `check_function_size`) vs Toolbelt V2 (`v2.check`, `v2.report`) vs Legacy (`v2-check`, `v2-batch`, `real-violations`, `line-count`).
- **Git verification**: MCP (`verify_git_work`, `verify_work_exists`, `validate_commit`) vs Legacy (`git-verify`, `git-work-verify`) and Toolbelt V2 (Captain git verification tools).
- **Swarm Brain**: MCP (`share_learning`, `search_swarm_knowledge`, …) vs Legacy (`swarm-brain`) and Toolbelt V2 (`brain.*`).
- **Website/WordPress**: MCP website-manager tools vs Legacy `unified-wordpress` + multiple WordPress deploy scripts.

