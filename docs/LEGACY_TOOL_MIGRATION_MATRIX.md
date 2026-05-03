# Legacy Tool Migration Matrix

Purpose: classify `tools/` modules before porting, archiving, or deleting.

## Summary

- `legacy_review`: 5
- `possible_duplicate`: 15
- `salvage_candidate`: 31
- `script_candidate`: 88

## Records

### `tools/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/agent/unified_agent.py`

- status: `script_candidate`
- classes: `UnifiedAgent`
- functions: `main, __init__, orient_agent, tasks_find, status_check, status_activity, lifecycle_automate, onboard_hard, lifecycle_heal`
- has_main_guard: `True`

### `tools/analysis/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/analysis/analyze_swarm_coordination_patterns.py`

- status: `script_candidate`
- classes: `none`
- functions: `load_agent_statuses, analyze_force_multiplier_delegations, analyze_coordination_loops, analyze_communication_bottlenecks, identify_optimization_opportunities, generate_report, main`
- has_main_guard: `True`

### `tools/analysis/comprehensive_tool_analyzer.py`

- status: `script_candidate`
- classes: `ToolAnalyzer`
- functions: `main, __init__, get_all_tools, categorize_tool, analyze_imports, check_if_unified_tool_exists, analyze_tool, check_toolbelt_registration, check_has_main, identify_consolidation_opportunities, identify_deletion_candidates, identify_integration_opportunities`
- has_main_guard: `True`

### `tools/analysis/consolidation_analyzer.py`

- status: `script_candidate`
- classes: `ConsolidationAnalyzer`
- functions: `main, __init__, analyze_tool_file, is_qa_tool, categorize_qa_tools, group_tools_by_category, identify_duplicates, analyze_tools_directory, analyze_from_json, generate_consolidation_plan, analyze, save_results`
- has_main_guard: `True`

### `tools/analysis/github_architecture_audit.py`

- status: `script_candidate`
- classes: `ArchitectureCriteria`
- functions: `scan_repo_architecture, get_user_repos, main`
- has_main_guard: `True`

### `tools/analysis/refactoring_ast_analyzer.py`

- status: `salvage_candidate`
- classes: `ASTAnalyzer`
- functions: `analyze_file`
- has_main_guard: `False`

### `tools/analysis/refactoring_models.py`

- status: `salvage_candidate`
- classes: `CodeEntity, ModuleSuggestion, RefactoringSuggestion`
- functions: `none`
- has_main_guard: `False`

### `tools/analysis/refactoring_suggestion_engine.py`

- status: `script_candidate`
- classes: `RefactoringSuggestionEngine, RefactoringSuggestionService`
- functions: `main, __init__, suggest_refactoring, _group_entities_by_category, _generate_module_suggestions, _estimate_main_file_size, _generate_import_changes, _calculate_confidence, _generate_reasoning, __init__, analyze_and_suggest, analyze_directory`
- has_main_guard: `True`

### `tools/analysis/scan_technical_debt.py`

- status: `script_candidate`
- classes: `TechnicalDebtScanner`
- functions: `main, __init__, scan, _get_files_to_scan, _scan_file, generate_report, generate_summary`
- has_main_guard: `True`

### `tools/analysis/seo_meta_tag_extractor.py`

- status: `script_candidate`
- classes: `MetaTagExtractor`
- functions: `main, __init__, fetch_html, extract_primary_meta_tags, extract_open_graph_tags, extract_twitter_card_tags, extract_schema_org_json_ld, extract_all_meta_tags, validate_completeness`
- has_main_guard: `True`

### `tools/analysis/source_analyzer.py`

- status: `script_candidate`
- classes: `SourceAnalyzer`
- functions: `main, __init__, analyze_file, _analyze_python, _analyze_javascript, _analyze_markdown, _analyze_yaml, get_directory_structure, analyze_directories, analyze_messaging_files, analyze, save_results`
- has_main_guard: `True`

### `tools/analysis/src_directory_report_generator.py`

- status: `salvage_candidate`
- classes: `none`
- functions: `generate_summary_report, save_analysis_results, print_analysis_summary`
- has_main_guard: `False`

### `tools/analysis/tech_debt_ci_summary.py`

- status: `script_candidate`
- classes: `none`
- functions: `run_technical_debt_analysis, summarize_markers, summarize_duplicates, summarize_v2_size, render_dashboard_markdown, render_devlog_markdown, main`
- has_main_guard: `True`

### `tools/analysis/technical_debt_analyzer.py`

- status: `script_candidate`
- classes: `TechnicalDebtAnalyzer`
- functions: `main, __init__, find_source_files, analyze_markers, calculate_hash, detect_duplicates, determine_ssot, generate_consolidation_recommendations, analyze_codebase, save_results, generate_report`
- has_main_guard: `True`

### `tools/analysis/temp_violation_scanner.py`

- status: `salvage_candidate`
- classes: `none`
- functions: `scan_violations`
- has_main_guard: `False`

### `tools/analysis/unified_analyzer.py`

- status: `script_candidate`
- classes: `UnifiedAnalyzer`
- functions: `main, __init__, analyze_repository, analyze_project_structure, analyze_file, detect_consolidation_opportunities, _calculate_similarity, analyze_overlaps, _extract_repo_name, _extract_tech_stack, run_full_analysis, print_analysis_report`
- has_main_guard: `True`

### `tools/autonomous/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/autonomous/task_models.py`

- status: `salvage_candidate`
- classes: `TaskOpportunity, AgentProfile, TaskRecommendation`
- functions: `none`
- has_main_guard: `False`

### `tools/captain/claim_and_fix_master_task.py`

- status: `script_candidate`
- classes: `none`
- functions: `parse_master_task_log, identify_task_type, claim_task, generate_fix_template, main`
- has_main_guard: `True`

### `tools/captain/create_work_session.py`

- status: `script_candidate`
- classes: `TimeoutConstants`
- functions: `generate_session_id, get_timestamp, create_session_file, extract_git_commits, main`
- has_main_guard: `True`

### `tools/captain/session_transition_automator.py`

- status: `script_candidate`
- classes: `SessionTransitionAutomator`
- functions: `main, __init__, generate_passdown, create_devlog_template, update_swarm_brain, update_state_report, validate_deliverables, send_handoff_message, run`
- has_main_guard: `True`

### `tools/captain/task_cli.py`

- status: `script_candidate`
- classes: `none`
- functions: `main`
- has_main_guard: `True`

### `tools/captain/unified_captain.py`

- status: `script_candidate`
- classes: `UnifiedCaptain`
- functions: `main, __init__, inbox_analyze, inbox_summary, coordination_assign_tasks, coordination_close_loops, monitoring_status_check, monitoring_find_idle, tasks_assign, cleanup_workspace`
- has_main_guard: `True`

### `tools/cleanup/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/cleanup/cleanup_obsolete_files.py`

- status: `script_candidate`
- classes: `none`
- functions: `cleanup, main`
- has_main_guard: `True`

### `tools/cleanup/cleanup_stub_files.py`

- status: `script_candidate`
- classes: `none`
- functions: `count_lines, is_empty_or_stub, create_archive_structure, archive_file, cleanup_empty_directories, main`
- has_main_guard: `True`

### `tools/cleanup/session_cleanup_automation.py`

- status: `script_candidate`
- classes: `SessionCleanupAutomation`
- functions: `main, __init__, create_passdown, create_devlog, post_to_discord, update_swarm_brain, run_cleanup`
- has_main_guard: `True`

### `tools/cleanup/unified_cleanup.py`

- status: `script_candidate`
- classes: `UnifiedCleanup`
- functions: `create_parser, main, __init__, handle_archive, handle_delete, handle_cleanup, handle_disk`
- has_main_guard: `True`

### `tools/cleanup/workspace_auto_cleaner.py`

- status: `script_candidate`
- classes: `none`
- functions: `archive_old_messages, clean_temp_files, organize_workspace, generate_cleanup_report, main`
- has_main_guard: `True`

### `tools/cli/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/cli/__main__.py`

- status: `script_candidate`
- classes: `none`
- functions: `none`
- has_main_guard: `True`

### `tools/cli/command_discovery.py`

- status: `script_candidate`
- classes: `CommandDiscovery`
- functions: `main, __init__, discover_commands, _analyze_file, _extract_command_name, _get_module_path, _extract_description, _extract_function_name, _categorize_command, generate_registry_code`
- has_main_guard: `True`

### `tools/cli/commands/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/cli/commands/registry.py`

- status: `legacy_review`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/cli/dispatchers/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/cli/dispatchers/unified_dispatcher.py`

- status: `script_candidate`
- classes: `UnifiedCLIDispatcher`
- functions: `create_parser, main, __init__, _load_command_registry, register_command, dispatch`
- has_main_guard: `True`

### `tools/cli/main.py`

- status: `salvage_candidate`
- classes: `none`
- functions: `main, _should_use_toolbelt, _should_propagate_system_exit`
- has_main_guard: `False`

### `tools/cli.py`

- status: `script_candidate`
- classes: `none`
- functions: `none`
- has_main_guard: `True`

### `tools/codemods/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/codemods/replace_prints_with_logger.py`

- status: `script_candidate`
- classes: `PrintTransformer`
- functions: `should_skip_file, transform_file, main, visit_Call`
- has_main_guard: `True`

### `tools/communication/agent_status_validator.py`

- status: `script_candidate`
- classes: `AgentStatusValidator`
- functions: `main, __init__, check_status_staleness, _verify_agent_activity, _parse_timestamp, get_agent_status, validate_status_health, get_summary, print_report`
- has_main_guard: `True`

### `tools/communication/coordination_pattern_validator.py`

- status: `script_candidate`
- classes: `CoordinationPatternValidator`
- functions: `main, __init__, validate_coordination_pattern, validate_workflow, validate_session_transition, validate_pattern_compliance, get_summary, print_report`
- has_main_guard: `True`

### `tools/communication/coordination_validator.py`

- status: `script_candidate`
- classes: `TrackerSnapshot, CoordinationValidator`
- functions: `main, __init__, validate_coordination_system, validate_message_structure, parse_tracker_file, validate_trackers_consistency, get_summary, print_report`
- has_main_guard: `True`

### `tools/communication/integration_validator.py`

- status: `script_candidate`
- classes: `IntegrationValidator`
- functions: `main, __init__, get_file_hash, find_venv_directories, find_duplicate_files, check_tool_availability, validate_integration_health, get_summary, print_report`
- has_main_guard: `True`

### `tools/communication/message_validator.py`

- status: `script_candidate`
- classes: `MessageValidator`
- functions: `main, __init__, validate_discord_message, validate_discord_embed, _validate_field, validate_protocol, validate_message_structure, validate_file, get_summary, print_report`
- has_main_guard: `True`

### `tools/communication/messaging_infrastructure_validator.py`

- status: `script_candidate`
- classes: `MessagingInfrastructureValidator`
- functions: `main, __init__, check_queue_status, validate_queue_file, validate_queue_directory, validate_infrastructure_health, get_summary, print_report`
- has_main_guard: `True`

### `tools/communication/multi_agent_validator.py`

- status: `script_candidate`
- classes: `MultiAgentValidator`
- functions: `main, __init__, check_pending_request, validate_agent_can_send, validate_all_agents, get_summary, print_report`
- has_main_guard: `True`

### `tools/communication/swarm_status_validator.py`

- status: `script_candidate`
- classes: `SwarmStatusValidator`
- functions: `main, __init__, validate_agent_status, validate_swarm_status, validate_coordination_status, get_summary, print_report`
- has_main_guard: `True`

### `tools/communication/unified_communication_validator.py`

- status: `script_candidate`
- classes: `UnifiedCommunicationValidator`
- functions: `main, __init__, validate_all, get_summary`
- has_main_guard: `True`

### `tools/consolidation/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/consolidation/analyze_dependencies.py`

- status: `script_candidate`
- classes: `none`
- functions: `main`
- has_main_guard: `True`

### `tools/consolidation/consolidate_messaging.py`

- status: `script_candidate`
- classes: `none`
- functions: `consolidate_messaging, main`
- has_main_guard: `True`

### `tools/consolidation/dependency_mapper.py`

- status: `salvage_candidate`
- classes: `DependencyType, DependencyNode, DependencyMapper`
- functions: `extract_imports, _is_internal_module, _is_stdlib, find_circular_dependencies, load_registry_dependencies, map_registry_relationships, to_dict, dfs, __init__, scan_directory, _get_tool_id, build_dependency_graph`
- has_main_guard: `False`

### `tools/consolidation/tests/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/consolidation/tests/test_dependency_mapper.py`

- status: `salvage_candidate`
- classes: `TestExtractImports, TestDependencyNode, TestDependencyMapper, TestCircularDependencies, TestRegistryDependencies, TestDependencyMapperIntegration`
- functions: `test_extract_simple_import, test_extract_from_import, test_extract_internal_import, test_extract_tools_v2_import, test_extract_relative_import, test_extract_third_party_import, test_extract_stdlib_import, test_extract_complex_imports, test_create_node, test_node_to_dict, test_initialize_mapper, test_scan_directory`
- has_main_guard: `False`

### `tools/consolidation/tests/test_tool_inventory.py`

- status: `script_candidate`
- classes: `TestToolMetadata, TestDiscoverTools, TestExtractMetadata, TestToolInventory, TestGenerateInventory`
- functions: `test_tool_metadata_creation, test_tool_metadata_defaults, test_tool_metadata_to_dict, test_discover_tools_in_directory, test_discover_tools_recursive, test_discover_tools_excludes_pycache, test_extract_metadata_from_unified_tool, test_extract_metadata_from_category_tool, test_extract_metadata_counts_lines, test_extract_metadata_detects_v2_compliance, test_tool_inventory_creation, test_tool_inventory_add_tool`
- has_main_guard: `True`

### `tools/consolidation/tool_inventory.py`

- status: `script_candidate`
- classes: `ToolMetadata, ToolInventory`
- functions: `discover_tools, extract_metadata, _extract_dependencies, _extract_cli_flags, generate_inventory, to_dict, __init__, add_tool, to_dict, save_to_json, load_from_json`
- has_main_guard: `True`

### `tools/coordination/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/coordination/discord_commands_test_helper.py`

- status: `script_candidate`
- classes: `none`
- functions: `test_command_registration, test_cog_loading, main`
- has_main_guard: `True`

### `tools/coordination/discord_commands_tester.py`

- status: `script_candidate`
- classes: `none`
- functions: `find_discord_command_files, analyze_command_file, generate_test_report, print_report, test_commands_in_discord, main`
- has_main_guard: `True`

### `tools/coordination/discord_simple_test.py`

- status: `script_candidate`
- classes: `none`
- functions: `send_discord_command, test_commands_interactive`
- has_main_guard: `True`

### `tools/debug/check_stuck_messages.py`

- status: `script_candidate`
- classes: `none`
- functions: `check_stuck_messages, main`
- has_main_guard: `True`

### `tools/debug/debug_message_queue.py`

- status: `script_candidate`
- classes: `none`
- functions: `check_queue_file, analyze_queue_entries, check_lock_files, check_queue_processor_running, fix_queue_issues, main`
- has_main_guard: `True`

### `tools/debug/diagnose_github_cli_auth.py`

- status: `script_candidate`
- classes: `none`
- functions: `check_gh_installed, check_gh_auth_status, check_environment_tokens, check_git_remote_auth, test_github_api_access, generate_solutions, main`
- has_main_guard: `True`

### `tools/debug/fix_message_queue.py`

- status: `script_candidate`
- classes: `none`
- functions: `clear_lock_files, reset_stuck_messages, main`
- has_main_guard: `True`

### `tools/debug/unified_debugger.py`

- status: `script_candidate`
- classes: `none`
- functions: `check_queue_health, scan_logs_for_errors, check_agent_processes, main`
- has_main_guard: `True`

### `tools/devops/documentation_assistant.py`

- status: `script_candidate`
- classes: `DocumentationAssistant`
- functions: `main, __init__, create_mission_doc, create_completion_report, create_milestone_doc, create_enhancement_request, create_status_snapshot, _count_active_agents, _list_recent_missions, _list_recent_milestones`
- has_main_guard: `True`

### `tools/devops/type_annotation_fixer.py`

- status: `script_candidate`
- classes: `TypeAnnotationFixer`
- functions: `main, __init__, find_files_needing_annotations, _should_skip_file, _needs_annotations, infer_return_type, _infer_from_body, infer_parameter_type, fix_file_annotations, process_all`
- has_main_guard: `True`

### `tools/devops/unified_environment.py`

- status: `script_candidate`
- classes: `none`
- functions: `check_tools, check_env_vars, check_docker_status, main`
- has_main_guard: `True`

### `tools/discord/unified_discord.py`

- status: `script_candidate`
- classes: `UnifiedDiscord`
- functions: `main, __init__, system_start, system_restart, test_commands, test_bot_debug, test_channels, verify_buttons, verify_running, upload_file`
- has_main_guard: `True`

### `tools/doc_templates_achievements.py`

- status: `salvage_candidate`
- classes: `none`
- functions: `create_milestone_template, create_enhancement_request_template`
- has_main_guard: `False`

### `tools/doc_templates_mission.py`

- status: `salvage_candidate`
- classes: `none`
- functions: `create_mission_tracking_template, create_completion_report_template`
- has_main_guard: `False`

### `tools/fixes/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/github/unified_github.py`

- status: `script_candidate`
- classes: `UnifiedGitHub`
- functions: `main, __init__, pr_create, pr_debug, pr_fix, repo_audit, merge_analyze_failures, merge_analyze_plans, merge_complete, audit_architecture`
- has_main_guard: `True`

### `tools/migration/discover_repos_manual.py`

- status: `script_candidate`
- classes: `none`
- functions: `clone_repo, clone_from_list, create_template_list, main`
- has_main_guard: `True`

### `tools/migration/migrate_with_downloader.py`

- status: `script_candidate`
- classes: `none`
- functions: `find_github_repo_downloader, run_migration, main`
- has_main_guard: `True`

### `tools/migration/repo_analyzer.py`

- status: `script_candidate`
- classes: `RepoMetadata, RepoAnalyzer`
- functions: `main, to_dict, __init__, analyze_repo, _analyze_files, _detect_language, _detect_technologies, _detect_dependencies, _analyze_git, _detect_project_type, _calculate_similarity_hash, _assess_status`
- has_main_guard: `True`

### `tools/migration/repo_migration_helper.py`

- status: `script_candidate`
- classes: `RepoMigrationHelper`
- functions: `main, __init__, _load_status, _save_status, clone_repo, clone_from_list, update_review_status, list_status, list_ready_to_publish, generate_publish_script`
- has_main_guard: `True`

### `tools/monitoring/unified_monitor.py`

- status: `script_candidate`
- classes: `UnifiedMonitor, WorkspaceHealth`
- functions: `main, __init__, monitor_queue_health, check_message_queue_file, monitor_service_health, monitor_disk_usage, monitor_agent_status, monitor_workspace_health, monitor_test_coverage, run_full_monitoring, print_monitoring_report, check_agent_workspace`
- has_main_guard: `True`

### `tools/security/check_sensitive_files.py`

- status: `script_candidate`
- classes: `none`
- functions: `run_git_command, check_tracked_sensitive_files, check_gitignore_coverage, print_security_report, main`
- has_main_guard: `True`

### `tools/security/unified_security_scanner.py`

- status: `script_candidate`
- classes: `none`
- functions: `run_command, scan_sensitive_files, scan_content_secrets, audit_python_dependencies, audit_npm_dependencies, main`
- has_main_guard: `True`

### `tools/swarm/agents/import_healer.py`

- status: `script_candidate`
- classes: `RewriteDecision`
- functions: `discover_modules, load_rewrite_map, resolve_module, rewrite_line, compile_safe, process_file, parse_args, main`
- has_main_guard: `True`

### `tools/swarm/tests/check_import_healer_coverage.py`

- status: `script_candidate`
- classes: `none`
- functions: `to_relpath, calculate_coverage, load_baseline, write_baseline, main`
- has_main_guard: `True`

### `tools/swarm/tests/fixtures/broken_imports.py`

- status: `legacy_review`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/swarm/tests/fixtures/modules/pkg_alpha/config.py`

- status: `legacy_review`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/swarm/tests/fixtures/modules/pkg_alpha/helpers.py`

- status: `salvage_candidate`
- classes: `none`
- functions: `ping`
- has_main_guard: `False`

### `tools/swarm/tests/fixtures/modules/pkg_beta/config.py`

- status: `legacy_review`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/swarm/tests/test_import_healer.py`

- status: `salvage_candidate`
- classes: `none`
- functions: `test_import_healer_validation`
- has_main_guard: `False`

### `tools/swarm/tests/validate_import_healer.py`

- status: `script_candidate`
- classes: `none`
- functions: `run_validation`
- has_main_guard: `True`

### `tools/thea/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/thea/analyze_chatgpt_selectors.py`

- status: `script_candidate`
- classes: `ChatGPTAnalyzer`
- functions: `main, __init__, setup_driver, load_page, analyze_input_elements, analyze_button_elements, _analyze_element, _score_element_relevance, suggest_selectors, generate_selector_report, _generate_recommendations, save_report`
- has_main_guard: `True`

### `tools/thea/debug_chatgpt_elements.py`

- status: `script_candidate`
- classes: `none`
- functions: `debug_chatgpt_elements`
- has_main_guard: `True`

### `tools/thea/demo_thea_interactive.py`

- status: `script_candidate`
- classes: `none`
- functions: `interactive_demo`
- has_main_guard: `True`

### `tools/thea/demo_thea_live.py`

- status: `script_candidate`
- classes: `none`
- functions: `demo_thea_automation`
- has_main_guard: `True`

### `tools/thea/demo_thea_simple.py`

- status: `legacy_review`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/thea/demo_working_thea.py`

- status: `script_candidate`
- classes: `none`
- functions: `demo_working`
- has_main_guard: `True`

### `tools/thea/run_headless_refresh.py`

- status: `script_candidate`
- classes: `none`
- functions: `main`
- has_main_guard: `True`

### `tools/thea/send_prompt_file.py`

- status: `script_candidate`
- classes: `none`
- functions: `send_prompt_from_file, main`
- has_main_guard: `True`

### `tools/thea/setup_thea_cookies.py`

- status: `script_candidate`
- classes: `TheaCookieSetup`
- functions: `main, __init__, initialize_driver, wait_for_manual_login, _debug_page_state, save_cookies_after_login, verify_setup, run_setup, cleanup`
- has_main_guard: `True`

### `tools/thea/simple_thea_communication.py`

- status: `script_candidate`
- classes: `SimpleTheaCommunication`
- functions: `main, __init__, initialize_driver, ensure_login, send_message, wait_for_response, save_response, communicate, cleanup`
- has_main_guard: `True`

### `tools/thea/tell_thea_session_summary.py`

- status: `script_candidate`
- classes: `none`
- functions: `tell_thea`
- has_main_guard: `True`

### `tools/thea/thea_authentication_handler.py`

- status: `salvage_candidate`
- classes: `TheaAuthenticationHandler`
- functions: `__init__, ensure_login, _automated_login, _handle_2fa, _manual_login, force_logout`
- has_main_guard: `False`

### `tools/thea/thea_automation.py`

- status: `script_candidate`
- classes: `TheaConfig, TheaAutomation`
- functions: `main, __init__, save_cookies, load_cookies, has_valid_cookies, start_browser, is_logged_in, ensure_login, send_message, wait_for_response, save_conversation, communicate`
- has_main_guard: `True`

### `tools/thea/thea_automation_browser.py`

- status: `salvage_candidate`
- classes: `TheaBrowserManager`
- functions: `__init__, start_browser, is_logged_in, ensure_login, _handle_manual_login, cleanup, get_driver`
- has_main_guard: `False`

### `tools/thea/thea_automation_cookie_manager.py`

- status: `salvage_candidate`
- classes: `TheaCookieManager`
- functions: `__init__, save_cookies, load_cookies, has_valid_cookies, _filter_auth_cookies, _load_cookies_into_driver, _filter_valid_cookies`
- has_main_guard: `False`

### `tools/thea/thea_automation_messaging.py`

- status: `salvage_candidate`
- classes: `TheaMessagingManager`
- functions: `__init__, send_message, wait_for_response, _process_response_result, save_conversation`
- has_main_guard: `False`

### `tools/thea/thea_cookie_manager.py`

- status: `salvage_candidate`
- classes: `TheaCookieManager`
- functions: `__init__, save_cookies, load_cookies, has_valid_cookies, clear_cookies`
- has_main_guard: `False`

### `tools/thea/thea_headless_send.py`

- status: `script_candidate`
- classes: `none`
- functions: `run_headless_prompt, main`
- has_main_guard: `True`

### `tools/thea/thea_keepalive.py`

- status: `script_candidate`
- classes: `none`
- functions: `read_last_refresh, write_last_refresh, ensure_keepalive, main`
- has_main_guard: `True`

### `tools/thea/thea_login_detector.py`

- status: `salvage_candidate`
- classes: `TheaLoginDetector`
- functions: `__init__, is_logged_in, _check_url_patterns, _check_logout_button, _check_user_menu, _check_new_chat_button, _check_login_buttons`
- has_main_guard: `False`

### `tools/thea/thea_login_handler.py`

- status: `script_candidate`
- classes: `TheaCookieManager, TheaLoginHandler`
- functions: `create_thea_login_handler, check_thea_login_status, __init__, save_cookies, load_cookies, has_valid_cookies, clear_cookies, __init__, ensure_login, _is_logged_in, _automated_login, _manual_login`
- has_main_guard: `True`

### `tools/thea/thea_login_handler_refactored.py`

- status: `salvage_candidate`
- classes: `TheaLoginHandler`
- functions: `__init__, ensure_login, force_logout, _is_logged_in`
- has_main_guard: `False`

### `tools/thea/thea_undetected_helper.py`

- status: `script_candidate`
- classes: `none`
- functions: `create_undetected_driver, create_standard_driver, check_undetected_available, get_installation_instructions`
- has_main_guard: `True`

### `tools/toolbelt/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/toolbelt/__main__.py`

- status: `script_candidate`
- classes: `none`
- functions: `main, print_help, print_tools`
- has_main_guard: `True`

### `tools/toolbelt/executors/__init__.py`

- status: `possible_duplicate`
- possible target: `tools_v2/utils/__init__.py`
- classes: `none`
- functions: `none`
- has_main_guard: `False`

### `tools/toolbelt/executors/agent_executor.py`

- status: `salvage_candidate`
- classes: `AgentExecutor`
- functions: `execute`
- has_main_guard: `False`

### `tools/toolbelt/executors/compliance_executor.py`

- status: `salvage_candidate`
- classes: `ComplianceExecutor`
- functions: `execute, _count_classes, _count_functions, _check_file, _scan_violations, _test_imports`
- has_main_guard: `False`

### `tools/toolbelt/executors/compliance_tracking_executor.py`

- status: `salvage_candidate`
- classes: `ComplianceTrackingExecutor`
- functions: `__init__, execute, _take_snapshot, _show_history, _show_trends, _launch_dashboard, _compare_snapshots`
- has_main_guard: `False`

### `tools/toolbelt/executors/consolidation_executor.py`

- status: `salvage_candidate`
- classes: `ConsolidationExecutor`
- functions: `execute, _find_duplicates, _suggest_consolidation, _verify_consolidation`
- has_main_guard: `False`

### `tools/toolbelt/executors/leaderboard_executor.py`

- status: `salvage_candidate`
- classes: `LeaderboardExecutor`
- functions: `__init__, execute, _show_leaderboard, _agent_details, _top_agents, _award_achievement`
- has_main_guard: `False`

### `tools/toolbelt/executors/messaging_executor.py`

- status: `salvage_candidate`
- classes: `MessagingExecutor`
- functions: `execute`
- has_main_guard: `False`

### `tools/toolbelt/executors/onboarding_executor.py`

- status: `salvage_candidate`
- classes: `OnboardingExecutor`
- functions: `__init__, execute, _soft_onboarding, _hard_onboarding, _onboarding_status`
- has_main_guard: `False`

### `tools/toolbelt/executors/refactor_executor.py`

- status: `salvage_candidate`
- classes: `RefactorExecutor`
- functions: `execute, _split_file, _auto_group_classes, _apply_facade, _extract_classes`
- has_main_guard: `False`

### `tools/toolbelt/executors/swarm_executor.py`

- status: `salvage_candidate`
- classes: `SwarmExecutor`
- functions: `__init__, execute, _captain_snapshot, _agent_checkin, _active_agents, _swarm_health`
- has_main_guard: `False`

### `tools/toolbelt/executors/v2_executor.py`

- status: `salvage_candidate`
- classes: `V2Executor`
- functions: `execute`
- has_main_guard: `False`

### `tools/toolbelt/executors/vector_executor.py`

- status: `salvage_candidate`
- classes: `VectorExecutor`
- functions: `execute`
- has_main_guard: `False`

### `tools/toolbelt_registry.py`

- status: `salvage_candidate`
- classes: `ToolRegistry`
- functions: `__init__, _build_flag_map, get_tool_for_flag, get_tool_by_name, list_tools, get_all_flags`
- has_main_guard: `False`

### `tools/validation/audit_imports.py`

- status: `script_candidate`
- classes: `none`
- functions: `test_import, file_to_module_path, audit_imports, main`
- has_main_guard: `True`

### `tools/validation/schema_org_validator.py`

- status: `script_candidate`
- classes: `SchemaOrgValidator`
- functions: `main, __init__, fetch_html, extract_json_ld, validate_schema_structure, validate_required_properties, validate_all_schemas, check_google_rich_results_compatibility`
- has_main_guard: `True`

### `tools/validation/template_structure_linter.py`

- status: `script_candidate`
- classes: `none`
- functions: `_create_message, _assert_sections_present, _assert_in_order, lint_template, main`
- has_main_guard: `True`

### `tools/validation/unified_validator.py`

- status: `script_candidate`
- classes: `UnifiedValidator`
- functions: `main, __init__, validate_ssot_config, _get_import_string, validate_imports, validate_tracker_status, validate_session_transition, validate_refactor_status, validate_consolidation, validate_queue, validate_all, print_validation_report`
- has_main_guard: `True`

### `tools/verification/integration_test_coordinator.py`

- status: `script_candidate`
- classes: `ModuleInfo, TestCoverage, IntegrationTestCoordinator`
- functions: `main, __init__, analyze_module, generate_test_template, validate_test_coverage, create_coordination_report, analyze_dependencies, check_integration_points`
- has_main_guard: `True`

### `tools/verification/stress_test_messaging_queue.py`

- status: `script_candidate`
- classes: `none`
- functions: `create_mock_delivery_callback, create_real_delivery_callback, run_stress_test, run_comparison_mode, main, delivery_callback, delivery_callback, delivery_callback, process_queue`
- has_main_guard: `True`

### `tools/verification/unified_verifier.py`

- status: `script_candidate`
- classes: `UnifiedVerifier`
- functions: `create_parser, main, __init__, verify_repo, verify_merge, verify_file, verify_cicd, verify_credentials`
- has_main_guard: `True`

### `tools/website_audit_ollama.py`

- status: `script_candidate`
- classes: `WebsiteAuditOllama`
- functions: `__init__, capture_screenshot_selenium, save_screenshot, _generate_recommendations, _generate_batch_summary`
- has_main_guard: `True`

### `tools/wordpress/unified_wordpress.py`

- status: `script_candidate`
- classes: `UnifiedWordPress`
- functions: `main, __init__, deploy_admin, deploy_rest_api, deploy_sftp, theme_activate, theme_check_syntax, debug_enable, debug_deployer, admin_clear_transients, admin_diagnose_path`
- has_main_guard: `True`
