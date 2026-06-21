# AgentTools Code Inventory

Generated inventory of Python classes and functions for domain discovery.

## `swarm_mcp/__init__.py`

_No top-level classes or functions._

## `swarm_mcp/cli.py`

### Functions
- `cmd_status()`
- `cmd_send()`
- `cmd_inbox()`
- `cmd_search()`
- `cmd_learn()`
- `cmd_tasks()`
- `cmd_assign()`
- `cmd_vote()`
- `cmd_conflict()`
- `cmd_profile()`
- `cmd_prove()`
- `cmd_patterns()`
- `main()`

## `swarm_mcp/core/__init__.py`

_No top-level classes or functions._

## `swarm_mcp/core/agent_dna.py`

### Classes
- `TaskRecord`
- `AgentProfile`
- `AgentDNA`
  - `__init__()`
  - `_load_data()`
  - `_save_profile()`
  - `_extract_module()`
  - `record_task()`
  - `_update_profile()`
  - `_calculate_strengths()`
  - `get_profile()`
  - `find_best_agent()`
  - `get_task_estimate()`
  - `get_leaderboard()`
  - `suggest_pairing()`

## `swarm_mcp/core/brain.py`

### Classes
- `Learning`
- `Decision`
- `SwarmBrain`
  - `__init__()`
  - `_generate_id()`
  - `share_learning()`
  - `record_decision()`
  - `search()`
  - `get_agent_notes()`
  - `add_note()`
  - `get_stats()`

## `swarm_mcp/core/conflict.py`

### Classes
- `ConflictSeverity`
- `WorkIntent`
- `Conflict`
- `ConflictDetector`
  - `__init__()`
  - `_generate_id()`
  - `_load_intents()`
  - `_save_intents()`
  - `_normalize_path()`
  - `_extract_module()`
  - `_calculate_similarity()`
  - `declare_intent()`
  - `check_conflicts()`
  - `complete_work()`
  - `abandon_work()`
  - `get_active_intents()`
  - `get_agent_intent()`
  - `get_blocked_files()`

## `swarm_mcp/core/consensus.py`

### Classes
- `VoteType`
- `ConsensusRule`
- `Vote`
- `Proposal`
- `ConsensusEngine`
  - `__init__()`
  - `_generate_id()`
  - `_load_proposals()`
  - `_save_proposal()`
  - `propose()`
  - `vote()`
  - `get_tally()`
  - `resolve()`
  - `get_open_proposals()`
  - `get_agent_pending_votes()`

## `swarm_mcp/core/coordinator.py`

### Classes
- `WolfStatus`
- `Prey`
- `PackCoordinator`
  - `__init__()`
  - `get_status()`
  - `roll_call()`
  - `get_ready_wolves()`
  - `assign_hunt()`
  - `broadcast()`
  - `scout_territory()`
  - `get_best_prey()`

## `swarm_mcp/core/memory.py`

### Classes
- `HuntingLore`
- `HuntRecord`
- `PackMemory`
  - `__init__()`
  - `_generate_id()`
  - `share_lore()`
  - `record_hunt()`
  - `recall()`
  - `get_wolf_notes()`
  - `add_note()`
  - `pack_stats()`

## `swarm_mcp/core/messaging.py`

### Classes
- `HowlUrgency`
- `HowlType`
- `Howl`
- `MessageQueue`
  - `__init__()`
  - `_generate_id()`
  - `send()`
  - `listen()`
  - `mark_heard()`
  - `count_unheard()`

### Functions
- `get_queue()`
- `howl()`
- `broadcast()`

## `swarm_mcp/core/messaging_templates.py`

### Classes
- `MessageTemplateCategory`
- `MessageTemplateInput`

### Functions
- `_coerce_category()`
- `render_message_template()`

## `swarm_mcp/core/pattern_miner.py`

### Classes
- `CoordinationEvent`
- `Pattern`
- `Suggestion`
- `PatternMiner`
  - `__init__()`
  - `_generate_id()`
  - `_load_data()`
  - `_save_event()`
  - `_save_pattern()`
  - `record_event()`
  - `_mine_patterns()`
  - `_mine_pairing_patterns()`
  - `_mine_sequence_patterns()`
  - `_mine_timing_patterns()`
  - `_mine_context_patterns()`
  - `suggest()`
  - `get_patterns()`
  - `get_stats()`

## `swarm_mcp/core/recovery.py`

### Classes
- `FailureEvent`
- `RecoveryManager`
  - `__init__()`
  - `analyze_failure()`
  - `propose_strategy()`
  - `execute_recovery()`
  - `_git_rollback()`
  - `_reinstall_deps()`

## `swarm_mcp/core/task_scoring.py`

### Classes
- `ScoredTask`
  - `roi_score()`
- `TaskScorer`
  - `__init__()`
  - `score_tasks()`
  - `select_next_task()`
  - `parse_task_metadata()`

## `swarm_mcp/core/verification.py`

### Classes
- `VerificationType`
- `VerificationResult`
- `VerificationHarness`
  - `__init__()`
  - `verify_page_fetch()`
  - `verify_unit_test()`
  - `verify_file_exists()`
  - `run_suite()`

## `swarm_mcp/core/work_proof.py`

### Classes
- `FileSnapshot`
- `WorkCommitment`
- `WorkProof`
- `WorkProofSystem`
  - `__init__()`
  - `_generate_hash()`
  - `_file_hash()`
  - `_snapshot_file()`
  - `_load_commitments()`
  - `_save_commitment()`
  - `_get_git_commits_since()`
  - `_get_git_diff_stats()`
  - `commit()`
  - `prove()`
  - `verify()`
  - `get_agent_proofs()`

## `swarm_mcp/servers/__init__.py`

_No top-level classes or functions._

## `swarm_mcp/servers/control.py`

### Functions
- `get_coordinator()`
- `check_pack_status()`
- `assign_hunt()`
- `scout_territory()`
- `main()`

## `swarm_mcp/servers/memory.py`

### Functions
- `share_learning()`
- `record_decision()`
- `search_knowledge()`
- `main()`

## `swarm_mcp/servers/messaging.py`

### Functions
- `send_agent_message()`
- `broadcast_message()`
- `read_messages()`
- `main()`

## `swarm_mcp/servers/tasks.py`

### Functions
- `read_task_log()`
- `write_task_log()`
- `add_to_inbox()`
- `mark_task_complete()`
- `get_tasks()`
- `select_next_task()`
- `verify_task_completion()`
- `recover_system()`
- `main()`

## `swarm_mcp/servers/tools.py`

### Functions
- `execute_toolbelt()`
- `list_available_tools()`
- `main()`

## `swarm_mcp/tools/__init__.py`

_No top-level classes or functions._

## `mcp_servers/__init__.py`

_No top-level classes or functions._

## `mcp_servers/backup_automation_server.py`

### Functions
- `create_backup()`
- `list_backups()`
- `restore_backup()`
- `verify_backup()`
- `get_storage_usage()`
- `apply_retention()`
- `list_backup_contents()`
- `compare_backups()`
- `sync_to_cloud()`
- `main()`

## `mcp_servers/cicd_helper_server.py`

### Functions
- `_run_command()`
- `_get_current_branch()`
- `check_ci_status()`
- `get_failed_logs()`
- `retry_failed_job()`
- `list_workflows()`
- `cancel_workflow()`
- `get_workflow_artifacts()`
- `main()`

## `mcp_servers/code_quality_server.py`

### Functions
- `detect_linter()`
- `run_linter()`
- `auto_fix_lint()`
- `format_code()`
- `check_types()`
- `find_dead_code()`
- `handle_tool_call()`
- `main()`

## `mcp_servers/database_operations_server.py`

### Functions
- `detect_orm()`
- `run_migration()`
- `rollback_migration()`
- `seed_database()`
- `backup_database()`
- `reset_database()`
- `handle_tool_call()`
- `main()`

## `mcp_servers/dependency_management_server.py`

### Functions
- `_run_command()`
- `_detect_package_manager()`
- `check_outdated()`
- `check_vulnerabilities()`
- `update_package()`
- `add_package()`
- `remove_unused()`
- `main()`

## `mcp_servers/discord_integration_server.py`

### Functions
- `_get_webhook_manager()`
- `_get_status_poster()`
- `_get_role_sync()`
- `add_webhook()`
- `remove_webhook()`
- `list_webhooks()`
- `test_webhook()`
- `send_message()`
- `send_server_status()`
- `send_alert()`
- `send_player_notification()`
- `send_leaderboard()`
- `create_status_message()`
- `update_status_message()`
- `list_status_messages()`
- `add_role_mapping()`
- `list_role_mappings()`
- `link_account()`
- `get_linked_account()`
- `update_player_roles()`
- `main()`

## `mcp_servers/documentation_generator_server.py`

### Functions
- `generate_api_docs()`
- `update_readme()`
- `generate_type_docs()`
- `check_doc_coverage()`
- `validate_links()`
- `handle_tool_call()`
- `main()`

## `mcp_servers/environment_setup_server.py`

### Functions
- `install_dependencies()`
- `setup_env_file()`
- `validate_environment()`
- `setup_database()`
- `health_check()`
- `handle_tool_call()`
- `main()`

## `mcp_servers/git_operations_server.py`

### Functions
- `verify_git_work()`
- `get_recent_commits()`
- `check_file_history()`
- `validate_commit()`
- `verify_work_exists_mcp()`
- `main()`

## `mcp_servers/issue_todo_tracker_server.py`

### Functions
- `extract_todos()`
- `create_issue_from_todo()`
- `link_todo_to_issue()`
- `list_stale_issues()`
- `close_completed()`
- `handle_tool_call()`
- `main()`

## `mcp_servers/memory_safety_server.py`

### Functions
- `main()`

## `mcp_servers/messaging_server.py`

### Functions
- `send_agent_message()`
- `broadcast_message()`
- `get_agent_status()`
- `main()`

## `mcp_servers/mission_control_server.py`

### Functions
- `check_agent_status()`
- `assign_mission()`
- `check_integrity()`
- `update_leaderboard()`
- `calculate_points()`
- `main()`

## `mcp_servers/mod_deployment_server.py`

### Functions
- `search_mods()`
- `get_mod_info()`
- `install_mod()`
- `update_mods()`
- `list_installed_mods()`
- `resolve_dependencies()`
- `check_server_health()`
- `create_rollback_point()`
- `rollback()`
- `manage_profile()`
- `main()`

## `mcp_servers/observability_server.py`

### Functions
- `get_metrics_snapshot()`
- `get_metric()`
- `check_system_health()`
- `check_slo_compliance()`
- `main()`

## `mcp_servers/performance_profiler_server.py`

### Functions
- `profile_startup()`
- `find_slow_tests()`
- `analyze_bundle()`
- `memory_snapshot()`
- `benchmark_function()`
- `handle_tool_call()`
- `main()`

## `mcp_servers/player_analytics_server.py`

### Functions
- `_get_db()`
- `_get_tracker()`
- `_get_analytics()`
- `_get_reports()`
- `player_join()`
- `player_leave()`
- `log_event()`
- `get_active_players()`
- `get_player()`
- `search_players()`
- `get_player_sessions()`
- `get_player_events()`
- `get_engagement_metrics()`
- `get_retention_metrics()`
- `get_peak_hours()`
- `get_player_segments()`
- `get_leaderboard()`
- `get_server_comparison()`
- `generate_daily_report()`
- `generate_weekly_report()`
- `list_reports()`
- `get_stats()`
- `main()`

## `mcp_servers/refactoring_server.py`

### Functions
- `check_file_size()`
- `auto_extract_code()`
- `fix_linting_issues()`
- `analyze_test_pyramid()`
- `main()`

## `mcp_servers/release_management_server.py`

### Functions
- `_run_command()`
- `_get_current_version()`
- `_parse_version()`
- `bump_version()`
- `generate_changelog()`
- `create_release()`
- `tag_version()`
- `validate_release()`
- `main()`

## `mcp_servers/security_scanner_server.py`

### Functions
- `scan_secrets()`
- `check_dependencies()`
- `audit_permissions()`
- `check_env_exposure()`
- `generate_security_report()`
- `handle_tool_call()`
- `main()`

## `mcp_servers/server_monitoring_server.py`

### Functions
- `collect_metrics()`
- `analyze_performance()`
- `check_alerts()`
- `acknowledge_alert()`
- `configure_discord_alerts()`
- `get_metric_history()`
- `get_weekly_report()`
- `main()`

## `mcp_servers/swarm_brain_server.py`

### Functions
- `share_learning()`
- `record_decision()`
- `search_swarm_knowledge()`
- `take_note()`
- `get_agent_notes()`
- `main()`

## `mcp_servers/task_manager_server.py`

### Functions
- `read_task_log()`
- `write_task_log()`
- `add_to_inbox()`
- `mark_task_complete()`
- `move_to_waiting_on()`
- `get_tasks()`
- `main()`

## `mcp_servers/testing_server.py`

### Functions
- `run_coverage_analysis()`
- `run_mutation_tests()`
- `main()`

## `mcp_servers/v2_compliance_server.py`

### Functions
- `count_lines()`
- `count_function_lines()`
- `check_v2_compliance()`
- `validate_file_size()`
- `check_function_size()`
- `get_v2_exceptions()`
- `main()`

## `mcp_servers/website_audit_server.py`

### Functions
- `audit_website_screenshot()`
- `audit_multiple_websites()`
- `get_available_ollama_models()`
- `analyze_website_design()`
- `analyze_website_ux()`
- `analyze_website_seo()`
- `audit_website_full()`
- `audit_website_batch()`
- `check_ollama_status()`

## `mcp_servers/website_manager_server.py`

### Functions
- `create_wordpress_page()`
- `deploy_file_to_wordpress()`
- `add_page_to_menu()`
- `list_wordpress_pages()`
- `create_blog_post_for_site()`
- `create_report_page_for_site()`
- `generate_image_prompts()`
- `purge_wordpress_cache()`
- `main()`

## `tools_v2/__init__.py`

_No top-level classes or functions._

## `tools_v2/adapters/__init__.py`

_No top-level classes or functions._

## `tools_v2/adapters/base_adapter.py`

### Classes
- `ToolSpec`
  - `validate_params()`
- `ToolResult`
  - `to_dict()`
- `IToolAdapter`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `get_help()`

## `tools_v2/adapters/error_types.py`

### Classes
- `ToolbeltError`
  - `__init__()`
- `ToolNotFoundError`
- `ToolValidationError`
  - `__init__()`
- `ToolExecutionError`
  - `__init__()`
- `ToolDependencyError`
  - `__init__()`
- `ToolConfigurationError`

### Functions
- `format_toolbelt_error()`

## `tools_v2/advisor_cli.py`

### Functions
- `main()`
- `_print_recommendation()`
- `_print_validation()`
- `_print_swarm_analysis()`

## `tools_v2/categories/__init__.py`

_No top-level classes or functions._

## `tools_v2/categories/agent_activity_tools.py`

### Classes
- `AgentActivityTrackerTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_check_agent_activity()`
- `AgentActivityMonitorTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/agent_ops_tools.py`

### Classes
- `AgentStatusTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ClaimTaskTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/analysis_tools.py`

### Classes
- `ProjectScanTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ComplexityTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `DuplicationTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/autonomous_workflow_tools.py`

### Classes
- `WorkflowAssignmentTask`
  - `__post_init__()`
- `Agent`
  - `__post_init__()`
- `Assignment`
- `AutoAssignmentEngine`
  - `__init__()`
  - `assign_task()`
  - `_calculate_fit_score()`
  - `_calculate_skill_match()`
  - `_get_available_agents()`
  - `_load_agents()`
  - `_send_assignment_message()`
- `AgentStatusData`
- `TeamCoordinationDashboard`
  - `__init__()`
  - `get_dashboard_view()`
  - `_load_all_agent_statuses()`
  - `_parse_agent_status()`
  - `_estimate_gas_level()`
  - `_detect_blockers()`
  - `_suggest_next_action()`
  - `_generate_summary()`
  - `_generate_coordination_suggestions()`
  - `_identify_bottlenecks()`
  - `_analyze_resource_allocation()`

### Functions
- `get_tools()`

## `tools_v2/categories/bi_tools.py`

### Classes
- `QuickMetricsTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `RepoROICalculatorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `TaskROICalculatorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `MarkovROIOptimizerTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/captain_coordination_tools.py`

### Classes
- `CompletionProcessorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_update_agent_status()`
  - `_log_to_swarm_brain()`
- `LeaderboardUpdaterTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `NextTaskPickerTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_calculate_task_fit()`
- `ROIQuickCalculatorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/captain_tools.py`

_No top-level classes or functions._

## `tools_v2/categories/captain_tools_advanced.py`

### Classes
- `PointsCalculatorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `MissionAssignTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `MarkovOptimizerTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/captain_tools_architecture.py`

### Classes
- `ArchitecturalCheckerTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/captain_tools_coordination.py`

### Classes
- `MultiFuelDelivery`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `MarkovROIRunner`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `SwarmStatusDashboard`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `MorningBriefingTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_generate_markdown_briefing()`

## `tools_v2/categories/captain_tools_core.py`

### Classes
- `StatusCheckTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `GitVerifyTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `WorkVerifyTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `IntegrityCheckTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/captain_tools_extension.py`

_No top-level classes or functions._

## `tools_v2/categories/captain_tools_messaging.py`

### Classes
- `SelfMessageTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `MessageAllAgentsTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/captain_tools_monitoring.py`

### Classes
- `GasDeliveryTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `LeaderboardUpdateTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_update_agent_entry()`
- `CycleReportTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/captain_tools_utilities.py`

### Classes
- `FindIdleAgentsTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `GasCheckTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `UpdateLogTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ToolbeltHelpTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/captain_tools_validation.py`

### Classes
- `FileExistenceValidator`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ProjectScanRunner`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `PhantomTaskDetector`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/communication_tools.py`

### Classes
- `DiscordRouterPoster`
  - `__init__()`
  - `post_update()`
- `DiscordPostTool`
  - `__init__()`
  - `execute()`

### Functions
- `get_tools()`

## `tools_v2/categories/compliance_tools.py`

### Classes
- `ComplianceHistoryTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `PolicyCheckTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/config_tools.py`

### Classes
- `ValidateConfigSSOTAdapter`
  - `get_spec()`
  - `get_help()`
  - `validate()`
  - `execute()`
- `ListConfigSourcesAdapter`
  - `get_spec()`
  - `get_help()`
  - `validate()`
  - `execute()`
- `CheckConfigImportsAdapter`
  - `get_spec()`
  - `get_help()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/coordination_tools.py`

### Classes
- `FindDomainExpertAdapter`
  - `get_spec()`
  - `get_help()`
  - `validate()`
  - `execute()`
- `RequestExpertReviewAdapter`
  - `get_spec()`
  - `get_help()`
  - `validate()`
  - `execute()`
- `CheckCoordinationPatternsAdapter`
  - `get_spec()`
  - `get_help()`
  - `validate()`
  - `execute()`
- `SwarmOrchestratorAdapter`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `SwarmStatusBroadcasterAdapter`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `MissionControlAdapter`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `CoordinateValidatorAdapter`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/dashboard_tools.py`

### Classes
- `DashboardGenerateTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `DashboardDataAggregateTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `DashboardHTMLTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `DashboardChartsTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `DashboardStylesTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `DiscordStatusDashboardTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/debate_tools.py`

### Classes
- `DebateStartTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `DebateVoteTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `DebateStatusTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `DebateNotifyTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/discord_profile_tools.py`

### Classes
- `DiscordProfileViewerTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_load_profile()`

## `tools_v2/categories/discord_tools.py`

### Classes
- `DiscordBotHealthTool`
  - `get_name()`
  - `get_description()`
  - `execute()`
- `DiscordBotStartTool`
  - `get_name()`
  - `get_description()`
  - `execute()`
- `DiscordTestMessageTool`
  - `get_name()`
  - `get_description()`
  - `execute()`

## `tools_v2/categories/discord_webhook_tools.py`

### Classes
- `CreateWebhookTool`
  - `get_name()`
  - `get_description()`
  - `execute()`
  - `_get_creation_instructions()`
- `ListWebhooksTool`
  - `get_name()`
  - `get_description()`
  - `execute()`
  - `_load_webhooks_from_config()`
  - `_extract_webhooks_from_dict()`
- `SaveWebhookTool`
  - `get_name()`
  - `get_description()`
  - `execute()`
  - `_save_to_env()`
  - `_save_to_config()`
- `TestWebhookTool`
  - `get_name()`
  - `get_description()`
  - `execute()`
- `WebhookManagerTool`
  - `get_name()`
  - `get_description()`
  - `execute()`

## `tools_v2/categories/docs_tools.py`

### Classes
- `DocsSearchTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `DocsExportTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/github_consolidation_tools.py`

### Classes
- `GitHubRepoSimilarityAnalyzerTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_fetch_user_repos()`
  - `_analyze_similarity()`
  - `_calculate_similarity()`
  - `_string_similarity()`
  - `_get_group_similarity()`
  - `_recommend_primary()`
  - `_generate_recommendations()`
- `GitHubRepoConsolidationPlannerTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_analyze_repo()`
  - `_create_steps()`
  - `_estimate_effort()`
  - `_identify_risks()`
- `GitHubRepoMergeExecutorTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/health_tools.py`

### Classes
- `HealthPingTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `SnapshotTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/import_fix_tools.py`

### Classes
- `ImportValidatorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ModuleExtractorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `QuickLineCountTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `PublicAPIImportValidatorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ImportChainValidatorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/infrastructure_audit_tools.py`

### Classes
- `OrchestratorScanTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `FileLineCounterTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ToolRuntimeAuditTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `BrokenToolsAuditTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ProjectComponentsAuditTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/infrastructure_tools.py`

_No top-level classes or functions._

## `tools_v2/categories/infrastructure_utility_tools.py`

### Classes
- `ModuleExtractorPlannerTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `InfrastructureROICalculatorTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `BrowserPoolManagerTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/infrastructure_workspace_tools.py`

### Classes
- `WorkspaceHealthMonitorTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `WorkspaceAutoCleanerTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `AgentStatusQuickCheckTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `AutoStatusUpdaterTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `SessionTransitionAutomatorTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `SwarmStatusBroadcasterTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/integration_tools.py`

### Classes
- `FindSSOTViolationsAdapter`
  - `get_spec()`
  - `get_help()`
  - `validate()`
  - `execute()`
- `FindDuplicateFunctionalityAdapter`
  - `get_spec()`
  - `get_help()`
  - `validate()`
  - `execute()`
- `FindIntegrationOpportunitiesAdapter`
  - `get_spec()`
  - `get_help()`
  - `validate()`
  - `execute()`
- `CheckImportDependenciesAdapter`
  - `get_spec()`
  - `get_help()`
  - `validate()`
  - `execute()`
- `AuditImportsTool`
  - `get_spec()`
  - `get_help()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/intelligent_mission_advisor.py`

### Classes
- `IntelligentMissionAdvisor`
  - `__init__()`
  - `_load_agent_status()`
  - `_identify_specialty()`
  - `_load_swarm_brain()`
  - `_extract_patterns()`
  - `_load_other_agents_work()`
  - `_load_leaderboard()`
  - `get_mission_recommendation()`
  - `_scan_real_available_tasks()`
  - `_check_conflicts()`
  - `_match_specialty()`
  - `_calculate_roi()`
  - `_verify_task()`
  - `_generate_intelligent_briefing()`
  - `_explain_specialty_match()`
  - `_generate_approach_recommendation()`
  - `_identify_risks()`
  - `_calculate_success_probability()`
  - `_calculate_confidence()`
  - `_get_current_rank()`
  - `_generate_fallback_suggestions()`
  - `validate_captain_order()`
  - `_find_relevant_patterns()`
  - `_generate_execution_guidance()`
  - `get_realtime_guidance()`
  - `analyze_swarm_state()`

### Functions
- `get_mission_advisor()`

## `tools_v2/categories/intelligent_mission_advisor_adapter.py`

### Classes
- `MissionAdvisorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_format_summary()`
- `OrderValidatorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_format_validation_summary()`
- `SwarmAnalyzerTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `RealtimeGuidanceTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/intelligent_mission_advisor_analysis.py`

### Classes
- `IntelligentMissionAnalysis`
  - `__init__()`
  - `scan_real_available_tasks()`
  - `check_conflicts()`
  - `match_specialty()`
  - `calculate_roi()`
  - `verify_task()`
  - `identify_risks()`
  - `calculate_success_probability()`

## `tools_v2/categories/intelligent_mission_advisor_guidance.py`

### Classes
- `IntelligentMissionGuidance`
  - `__init__()`
  - `generate_intelligent_briefing()`
  - `explain_specialty_match()`
  - `generate_approach_recommendation()`
  - `calculate_confidence()`
  - `get_current_rank()`
  - `find_relevant_patterns()`
  - `generate_execution_guidance()`
  - `get_realtime_guidance()`
  - `analyze_swarm_state()`
  - `generate_fallback_suggestions()`

## `tools_v2/categories/memory_safety_adapters.py`

### Classes
- `MemoryLeakDetectorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `FileVerificationTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `UnboundedScanTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `MemorySafetyImportValidatorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `FileHandleCheckTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/memory_safety_tools.py`

### Functions
- `detect_memory_leaks()`
- `verify_files_exist()`
- `scan_unbounded_structures()`
- `validate_imports()`
- `check_file_handles()`

## `tools_v2/categories/message_analytics_tools.py`

### Classes
- `MessagePatternAnalyzerTool`
  - `__init__()`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `get_help()`
- `MessageMetricsDashboardTool`
  - `__init__()`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_is_recent()`
  - `get_help()`
- `MessageLearningExtractorTool`
  - `__init__()`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `get_help()`

### Functions
- `_counter_to_dict()`

## `tools_v2/categories/message_history_tools.py`

### Classes
- `MessageHistoryViewerTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `MessageHistoryAnalyzerTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `MessageCompressionTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/message_task_tools.py`

### Classes
- `MessageIngestTool`
  - `execute()`
- `TaskParserTool`
  - `execute()`
- `TaskFingerprintTool`
  - `execute()`

## `tools_v2/categories/messaging_tools.py`

### Classes
- `SendMessageTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `BroadcastTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `InboxCheckTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/mission_calculator.py`

### Functions
- `calculate_optimal_task()`
- `build_context_package()`
- `format_mission_brief()`

## `tools_v2/categories/mod_deployment_tools.py`

### Classes
- `ThunderstoreSearchTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ModInstallTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ModUpdateTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ModDependencyResolverTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ModProfileTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ServerHealthCheckTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ModRollbackTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/observability_tools.py`

### Classes
- `MetricsSnapshotTool`
  - `execute()`
- `MetricsTool`
  - `execute()`
- `SystemHealthTool`
  - `execute()`
- `SLOCheckTool`
  - `execute()`

## `tools_v2/categories/onboarding_tools.py`

### Classes
- `SoftOnboardTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `HardOnboardTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/oss_tools.py`

### Classes
- `OSSCloneTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `OSSFetchIssuesTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `OSSImportIssuesTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `OSSPortfolioTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `OSSStatusTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/proposal_tools.py`

### Classes
- `CreateProposalTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ListProposalsTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ViewProposalTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ContributeProposalTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `StartDebateTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/queue_monitor_tools.py`

### Classes
- `QueueStatusMonitorTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/refactoring_tools.py`

### Classes
- `FileSizeCheckTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `AutoExtractTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `TestPyramidAnalyzerTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_generate_recommendations()`
- `LintFixTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/security_audit_tools.py`

### Classes
- `ExternalResource`
- `ResourceParser`
  - `__init__()`
  - `handle_starttag()`
- `SecurityAuditTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_fetch()`
  - `_check_security_headers()`
  - `_analyze_resources()`
  - `_check_rate_limits()`
  - `_probe_rate_limit()`
  - `_extract_backend_info()`
  - `_probe_paths()`
  - `_scan_ports()`
  - `_probe_subdomains()`
  - `_score_findings()`
- `FetchResult`

### Functions
- `_apex_domain()`
- `_fetch_status()`

## `tools_v2/categories/session_tools.py`

### Classes
- `SessionCleanupTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_create_passdown()`
  - `_create_devlog()`
  - `_update_swarm_brain()`
  - `_update_status()`
- `PassdownTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `SessionPointsCalculatorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/ssot_validation_tools.py`

### Classes
- `SSOTViolationDetector`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_detect_violations()`
  - `_find_duplicate_classes()`
  - `_find_duplicate_functions()`
  - `_find_multiple_repositories()`
  - `_find_scattered_config()`
  - `_find_duplicate_constants()`
  - `_generate_summary()`
- `SSOTPatternValidator`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_validate_pattern()`
  - `_validate_repository_pattern()`
  - `_validate_service_pattern()`
  - `_validate_config_pattern()`

## `tools_v2/categories/swarm_brain_tools.py`

### Classes
- `TakeNoteTool`
  - `execute()`
- `ShareLearningTool`
  - `execute()`
- `SearchKnowledgeTool`
  - `execute()`
- `LogSessionTool`
  - `execute()`
- `GetAgentNotesTool`
  - `execute()`

## `tools_v2/categories/swarm_consciousness.py`

### Classes
- `SwarmPulseTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_collect_swarm_pulse()`
  - `_get_agent_pulse()`
  - `_dashboard_view()`
  - `_detect_conflicts()`
  - `_find_related_work()`
  - `_captain_command_center()`

## `tools_v2/categories/swarm_mission_control.py`

### Classes
- `SwarmMissionControl`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `SwarmConflictDetector`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ContextPackageBuilder`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_find_related_files()`
  - `_find_similar_work()`
  - `_find_current_violations()`
  - `_find_dependencies()`
  - `_find_coordination_needs()`
  - `_find_success_patterns()`
  - `_generate_checklist()`
  - `_calculate_completeness()`

## `tools_v2/categories/swarm_state_reader.py`

### Functions
- `read_swarm_state()`
- `read_agent_context()`
- `get_agent_specialty()`
- `analyze_available_work()`

## `tools_v2/categories/system_tools.py`

### Classes
- `SystemDateTimeTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `CheckInSystemTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `CheckInViewerTool`
  - `get_name()`
  - `get_description()`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/test_generation_tools.py`

### Classes
- `TestFileGeneratorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
  - `_generate_test_template()`
- `CoveragePyramidReportTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/testing_tools.py`

### Classes
- `CoverageReportTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `MutationGateTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/v2_tools.py`

### Classes
- `V2CheckTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `V2ReportTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/validation_tools.py`

### Classes
- `SmokeTestTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `FeatureFlagTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `RollbackTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ValidationReportTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `IntegrityValidatorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `SSOTValidatorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/vector_tools.py`

### Classes
- `TaskContextTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `VectorSearchTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `IndexWorkTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/web_tools.py`

### Classes
- `DiscordMermaidRendererTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `DiscordWebTestTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/categories/workflow_tools.py`

### Classes
- `InboxCleanupTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `MissionClaimTool`
  - `get_spec()`
  - `validate()`
  - `execute()`
- `ROICalculatorTool`
  - `get_spec()`
  - `validate()`
  - `execute()`

## `tools_v2/core/__init__.py`

_No top-level classes or functions._

## `tools_v2/core/tool_facade.py`

_No top-level classes or functions._

## `tools_v2/core/tool_spec.py`

### Classes
- `ToolSpec`
  - `__init__()`
  - `validate_params()`

## `tools_v2/demo_swarm_pulse.py`

### Functions
- `demo_swarm_pulse()`

## `tools_v2/rank_tools_v2.py`

### Functions
- `main()`

## `tools_v2/test_bi_tools.py`

### Functions
- `test_bi_metrics()`
- `test_bi_roi_task()`
- `test_bi_roi_optimize()`
- `main()`

## `tools_v2/test_toolbelt_basic.py`

### Functions
- `test_basic_functionality()`

## `tools_v2/tests/__init__.py`

_No top-level classes or functions._

## `tools_v2/tests/test_adapters.py`

### Classes
- `TestToolSpec`
  - `test_spec_creation()`
  - `test_validate_params_success()`
  - `test_validate_params_failure()`
- `TestToolResult`
  - `test_result_creation()`
  - `test_result_to_dict()`
- `TestIToolAdapter`
  - `test_adapter_implements_interface()`
  - `test_adapter_get_spec()`
  - `test_adapter_validate()`
  - `test_adapter_get_help()`

## `tools_v2/tests/test_core.py`

### Classes
- `TestToolbeltCore`
  - `test_core_initialization()`
  - `test_list_tools()`
  - `test_list_categories()`
  - `test_tool_not_found()`
  - `test_execution_history_recording()`
  - `test_clear_history()`
  - `test_get_execution_history()`

## `tools_v2/tests/test_registry.py`

### Classes
- `TestToolRegistry`
  - `test_registry_initialization()`
  - `test_singleton_pattern()`
  - `test_list_tools()`
  - `test_list_by_category()`
  - `test_resolve_valid_tool()`
  - `test_resolve_invalid_tool()`
  - `test_caching()`
  - `test_export_lock()`

## `tools_v2/tests/test_smoke_categories.py`

### Classes
- `TestCategoryImports`
  - `test_import_vector_tools()`
  - `test_import_messaging_tools()`
  - `test_import_analysis_tools()`
  - `test_import_v2_tools()`
  - `test_import_agent_ops_tools()`
  - `test_import_testing_tools()`
  - `test_import_compliance_tools()`
  - `test_import_onboarding_tools()`
  - `test_import_docs_tools()`
  - `test_import_health_tools()`
- `TestAdapterInterface`
  - `test_adapter_implements_interface()`

## `tools_v2/tool_registry.py`

### Classes
- `ToolRegistry`
  - `__init__()`
  - `_load_registry_data()`
  - `_resolve_tool_class()`
  - `get_tool_class()`
  - `resolve()`
  - `list_tools()`
  - `list_by_category()`
  - `get_categories()`
  - `clear_cache()`

### Functions
- `get_tool_registry()`

## `tools_v2/toolbelt_core.py`

### Classes
- `ToolbeltCore`
  - `__init__()`
  - `run()`
  - `list_tools()`
  - `list_categories()`
  - `get_tool_help()`
  - `get_execution_history()`
  - `clear_history()`
  - `_record_execution()`

### Functions
- `get_toolbelt_core()`

## `tools_v2/utils/__init__.py`

_No top-level classes or functions._

## `tools_v2/utils/discord_mermaid_renderer.py`

### Classes
- `DiscordMermaidRenderer`
  - `__init__()`
  - `extract_mermaid_diagrams()`
  - `render_mermaid_to_image_url()`
  - `render_mermaid_to_file()`
  - `render_to_file()`
  - `replace_mermaid_with_images()`
  - `post_to_discord_with_mermaid()`

## `tests/test_agent_dna.py`

### Functions
- `agent_dna()`
- `test_record_task_and_profile_update()`
- `test_find_best_agent()`
- `test_calculate_strengths()`

## `tests/test_conflict.py`

### Functions
- `conflict_detector()`
- `test_declare_intent_no_conflict()`
- `test_detect_file_conflict()`
- `test_detect_module_conflict()`
- `test_expiration()`

## `tests/test_consensus.py`

### Functions
- `consensus_engine()`
- `test_propose_and_vote()`
- `test_resolution_majority()`
- `test_resolution_unanimous_fail()`

## `tests/test_mcp_servers.py`

### Classes
- `TestMCPServers`
  - `_run_server()`
  - `test_tools_server_initialize()`
  - `test_messaging_server_initialize()`
  - `test_memory_server_initialize()`
  - `test_tasks_server_initialize()`
  - `test_send_agent_message_applies_template()`
  - `test_broadcast_message_applies_template()`

## `tests/test_pattern_miner.py`

### Functions
- `miner()`
- `test_record_event()`
- `test_mine_patterns()`
- `test_suggest()`

## `tests/test_stage4_features.py`

### Classes
- `TestTaskScoring`
  - `test_roi_calculation()`
  - `test_dependency_penalty()`
  - `test_metadata_parsing()`
  - `test_selection()`
- `TestVerification`
  - `test_file_exists()`
  - `test_unit_test_run()`
- `TestRecovery`
  - `test_analyze_failure()`
  - `test_analyze_syntax_error()`

## `tests/test_toolbelt.py`

### Classes
- `TestToolbelt`
  - `test_registry_loading()`
  - `test_registry_paths_exist()`
  - `test_help_generation()`
  - `test_list_tools()`

## `tests/test_work_proof.py`

### Functions
- `proof_system()`
- `test_commit_and_prove()`
- `test_invalid_proof_no_changes()`
