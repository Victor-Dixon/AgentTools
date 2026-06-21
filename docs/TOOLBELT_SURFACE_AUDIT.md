# Toolbelt Surface Audit

## Summary

- `tools`: 139 Python files
- `tools_v2`: 89 Python files
- `mcp_servers`: 28 Python files
- `swarm_mcp`: 23 Python files

## Classification Policy

- `keep_active`: canonical runtime/toolbelt code.
- `adapter_surface`: MCP wrapper/server layer requiring registry tests.
- `legacy_review`: old toolbelt surface requiring migration or archive decision.
- `broken`: syntax or parse failure.

## Files

### `tools/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/agent/unified_agent.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `UnifiedAgent`
- functions: `main, __init__, orient_agent, tasks_find, status_check, status_activity, lifecycle_automate, onboard_hard, lifecycle_heal`

### `tools/analysis/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/analysis/analyze_swarm_coordination_patterns.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `load_agent_statuses, analyze_force_multiplier_delegations, analyze_coordination_loops, analyze_communication_bottlenecks, identify_optimization_opportunities, generate_report, main`

### `tools/analysis/comprehensive_tool_analyzer.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `ToolAnalyzer`
- functions: `main, __init__, get_all_tools, categorize_tool, analyze_imports, check_if_unified_tool_exists, analyze_tool, check_toolbelt_registration, check_has_main, identify_consolidation_opportunities, identify_deletion_candidates, identify_integration_opportunities, analyze, generate_report`

### `tools/analysis/consolidation_analyzer.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `ConsolidationAnalyzer`
- functions: `main, __init__, analyze_tool_file, is_qa_tool, categorize_qa_tools, group_tools_by_category, identify_duplicates, analyze_tools_directory, analyze_from_json, generate_consolidation_plan, analyze, save_results`

### `tools/analysis/github_architecture_audit.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `ArchitectureCriteria`
- functions: `scan_repo_architecture, get_user_repos, main`

### `tools/analysis/refactoring_ast_analyzer.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `ASTAnalyzer`
- functions: `analyze_file`

### `tools/analysis/refactoring_models.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `CodeEntity, ModuleSuggestion, RefactoringSuggestion`
- functions: `none`

### `tools/analysis/refactoring_suggestion_engine.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `RefactoringSuggestionEngine, RefactoringSuggestionService`
- functions: `main, __init__, suggest_refactoring, _group_entities_by_category, _generate_module_suggestions, _estimate_main_file_size, _generate_import_changes, _calculate_confidence, _generate_reasoning, __init__, analyze_and_suggest, analyze_directory, _should_skip_file`

### `tools/analysis/scan_technical_debt.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TechnicalDebtScanner`
- functions: `main, __init__, scan, _get_files_to_scan, _scan_file, generate_report, generate_summary`

### `tools/analysis/seo_meta_tag_extractor.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `MetaTagExtractor`
- functions: `main, __init__, fetch_html, extract_primary_meta_tags, extract_open_graph_tags, extract_twitter_card_tags, extract_schema_org_json_ld, extract_all_meta_tags, validate_completeness`

### `tools/analysis/source_analyzer.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `SourceAnalyzer`
- functions: `main, __init__, analyze_file, _analyze_python, _analyze_javascript, _analyze_markdown, _analyze_yaml, get_directory_structure, analyze_directories, analyze_messaging_files, analyze, save_results`

### `tools/analysis/src_directory_report_generator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `generate_summary_report, save_analysis_results, print_analysis_summary`

### `tools/analysis/tech_debt_ci_summary.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `run_technical_debt_analysis, summarize_markers, summarize_duplicates, summarize_v2_size, render_dashboard_markdown, render_devlog_markdown, main`

### `tools/analysis/technical_debt_analyzer.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TechnicalDebtAnalyzer`
- functions: `main, __init__, find_source_files, analyze_markers, calculate_hash, detect_duplicates, determine_ssot, generate_consolidation_recommendations, analyze_codebase, save_results, generate_report`

### `tools/analysis/temp_violation_scanner.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `scan_violations`

### `tools/analysis/unified_analyzer.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `UnifiedAnalyzer`
- functions: `main, __init__, analyze_repository, analyze_project_structure, analyze_file, detect_consolidation_opportunities, _calculate_similarity, analyze_overlaps, _extract_repo_name, _extract_tech_stack, run_full_analysis, print_analysis_report, track_tool_usage`

### `tools/autonomous/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/autonomous/task_models.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TaskOpportunity, AgentProfile, TaskRecommendation`
- functions: `none`

### `tools/captain/claim_and_fix_master_task.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `parse_master_task_log, identify_task_type, claim_task, generate_fix_template, main`

### `tools/captain/create_work_session.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TimeoutConstants`
- functions: `generate_session_id, get_timestamp, create_session_file, extract_git_commits, main`

### `tools/captain/session_transition_automator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `SessionTransitionAutomator`
- functions: `main, __init__, generate_passdown, create_devlog_template, update_swarm_brain, update_state_report, validate_deliverables, send_handoff_message, run`

### `tools/captain/task_cli.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `main`

### `tools/captain/unified_captain.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `UnifiedCaptain`
- functions: `main, __init__, inbox_analyze, inbox_summary, coordination_assign_tasks, coordination_close_loops, monitoring_status_check, monitoring_find_idle, tasks_assign, cleanup_workspace`

### `tools/cleanup/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/cleanup/cleanup_obsolete_files.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `cleanup, main`

### `tools/cleanup/cleanup_stub_files.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `count_lines, is_empty_or_stub, create_archive_structure, archive_file, cleanup_empty_directories, main`

### `tools/cleanup/session_cleanup_automation.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `SessionCleanupAutomation`
- functions: `main, __init__, create_passdown, create_devlog, post_to_discord, update_swarm_brain, run_cleanup`

### `tools/cleanup/unified_cleanup.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `UnifiedCleanup`
- functions: `create_parser, main, __init__, handle_archive, handle_delete, handle_cleanup, handle_disk`

### `tools/cleanup/workspace_auto_cleaner.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `archive_old_messages, clean_temp_files, organize_workspace, generate_cleanup_report, main`

### `tools/cli/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/cli/__main__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/cli/command_discovery.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `CommandDiscovery`
- functions: `main, __init__, discover_commands, _analyze_file, _extract_command_name, _get_module_path, _extract_description, _extract_function_name, _categorize_command, generate_registry_code`

### `tools/cli/commands/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/cli/commands/registry.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/cli/dispatchers/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/cli/dispatchers/unified_dispatcher.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `UnifiedCLIDispatcher`
- functions: `create_parser, main, __init__, _load_command_registry, register_command, dispatch`

### `tools/cli/main.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `main, _should_use_toolbelt, _should_propagate_system_exit`

### `tools/cli.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/codemods/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/codemods/replace_prints_with_logger.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `PrintTransformer`
- functions: `should_skip_file, transform_file, main, visit_Call`

### `tools/communication/agent_status_validator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `AgentStatusValidator`
- functions: `main, __init__, check_status_staleness, _verify_agent_activity, _parse_timestamp, get_agent_status, validate_status_health, get_summary, print_report`

### `tools/communication/coordination_pattern_validator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `CoordinationPatternValidator`
- functions: `main, __init__, validate_coordination_pattern, validate_workflow, validate_session_transition, validate_pattern_compliance, get_summary, print_report`

### `tools/communication/coordination_validator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TrackerSnapshot, CoordinationValidator`
- functions: `main, __init__, validate_coordination_system, validate_message_structure, parse_tracker_file, validate_trackers_consistency, get_summary, print_report`

### `tools/communication/integration_validator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `IntegrationValidator`
- functions: `main, __init__, get_file_hash, find_venv_directories, find_duplicate_files, check_tool_availability, validate_integration_health, get_summary, print_report`

### `tools/communication/message_validator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `MessageValidator`
- functions: `main, __init__, validate_discord_message, validate_discord_embed, _validate_field, validate_protocol, validate_message_structure, validate_file, get_summary, print_report`

### `tools/communication/messaging_infrastructure_validator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `MessagingInfrastructureValidator`
- functions: `main, __init__, check_queue_status, validate_queue_file, validate_queue_directory, validate_infrastructure_health, get_summary, print_report`

### `tools/communication/multi_agent_validator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `MultiAgentValidator`
- functions: `main, __init__, check_pending_request, validate_agent_can_send, validate_all_agents, get_summary, print_report`

### `tools/communication/swarm_status_validator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `SwarmStatusValidator`
- functions: `main, __init__, validate_agent_status, validate_swarm_status, validate_coordination_status, get_summary, print_report`

### `tools/communication/unified_communication_validator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `UnifiedCommunicationValidator`
- functions: `main, __init__, validate_all, get_summary`

### `tools/consolidation/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/consolidation/analyze_dependencies.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `main`

### `tools/consolidation/consolidate_messaging.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `consolidate_messaging, main`

### `tools/consolidation/dependency_mapper.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `DependencyType, DependencyNode, DependencyMapper`
- functions: `extract_imports, _is_internal_module, _is_stdlib, find_circular_dependencies, load_registry_dependencies, map_registry_relationships, to_dict, dfs, __init__, scan_directory, _get_tool_id, build_dependency_graph, _find_tool_by_module, get_external_dependencies, get_internal_dependencies, get_circular_dependencies, export_to_json`

### `tools/consolidation/tests/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/consolidation/tests/test_dependency_mapper.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TestExtractImports, TestDependencyNode, TestDependencyMapper, TestCircularDependencies, TestRegistryDependencies, TestDependencyMapperIntegration`
- functions: `test_extract_simple_import, test_extract_from_import, test_extract_internal_import, test_extract_tools_v2_import, test_extract_relative_import, test_extract_third_party_import, test_extract_stdlib_import, test_extract_complex_imports, test_create_node, test_node_to_dict, test_initialize_mapper, test_scan_directory, test_build_dependency_graph, test_get_external_dependencies, test_get_internal_dependencies, test_find_simple_circular_dependency, test_find_complex_circular_dependency, test_no_circular_dependency`

### `tools/consolidation/tests/test_tool_inventory.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TestToolMetadata, TestDiscoverTools, TestExtractMetadata, TestToolInventory, TestGenerateInventory`
- functions: `test_tool_metadata_creation, test_tool_metadata_defaults, test_tool_metadata_to_dict, test_discover_tools_in_directory, test_discover_tools_recursive, test_discover_tools_excludes_pycache, test_extract_metadata_from_unified_tool, test_extract_metadata_from_category_tool, test_extract_metadata_counts_lines, test_extract_metadata_detects_v2_compliance, test_tool_inventory_creation, test_tool_inventory_add_tool, test_tool_inventory_to_dict, test_tool_inventory_save_to_json, test_tool_inventory_load_from_json, test_generate_inventory_from_directories, test_generate_inventory_handles_missing_directories, test_generate_inventory_detects_duplicates`

### `tools/consolidation/tool_inventory.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `ToolMetadata, ToolInventory`
- functions: `discover_tools, extract_metadata, _extract_dependencies, _extract_cli_flags, generate_inventory, to_dict, __init__, add_tool, to_dict, save_to_json, load_from_json`

### `tools/coordination/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/coordination/discord_commands_test_helper.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `test_command_registration, test_cog_loading, main`

### `tools/coordination/discord_commands_tester.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `find_discord_command_files, analyze_command_file, generate_test_report, print_report, test_commands_in_discord, main`

### `tools/coordination/discord_simple_test.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `send_discord_command, test_commands_interactive`

### `tools/debug/check_stuck_messages.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `check_stuck_messages, main`

### `tools/debug/debug_message_queue.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `check_queue_file, analyze_queue_entries, check_lock_files, check_queue_processor_running, fix_queue_issues, main`

### `tools/debug/diagnose_github_cli_auth.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `check_gh_installed, check_gh_auth_status, check_environment_tokens, check_git_remote_auth, test_github_api_access, generate_solutions, main`

### `tools/debug/fix_message_queue.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `clear_lock_files, reset_stuck_messages, main`

### `tools/debug/unified_debugger.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `check_queue_health, scan_logs_for_errors, check_agent_processes, main`

### `tools/devops/documentation_assistant.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `DocumentationAssistant`
- functions: `main, __init__, create_mission_doc, create_completion_report, create_milestone_doc, create_enhancement_request, create_status_snapshot, _count_active_agents, _list_recent_missions, _list_recent_milestones`

### `tools/devops/type_annotation_fixer.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TypeAnnotationFixer`
- functions: `main, __init__, find_files_needing_annotations, _should_skip_file, _needs_annotations, infer_return_type, _infer_from_body, infer_parameter_type, fix_file_annotations, process_all`

### `tools/devops/unified_environment.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `check_tools, check_env_vars, check_docker_status, main`

### `tools/discord/unified_discord.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `UnifiedDiscord`
- functions: `main, __init__, system_start, system_restart, test_commands, test_bot_debug, test_channels, verify_buttons, verify_running, upload_file`

### `tools/doc_templates_achievements.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `create_milestone_template, create_enhancement_request_template`

### `tools/doc_templates_mission.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `create_mission_tracking_template, create_completion_report_template`

### `tools/fixes/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/github/unified_github.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `UnifiedGitHub`
- functions: `main, __init__, pr_create, pr_debug, pr_fix, repo_audit, merge_analyze_failures, merge_analyze_plans, merge_complete, audit_architecture`

### `tools/migration/discover_repos_manual.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `clone_repo, clone_from_list, create_template_list, main`

### `tools/migration/migrate_with_downloader.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `find_github_repo_downloader, run_migration, main`

### `tools/migration/repo_analyzer.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `RepoMetadata, RepoAnalyzer`
- functions: `main, to_dict, __init__, analyze_repo, _analyze_files, _detect_language, _detect_technologies, _detect_dependencies, _analyze_git, _detect_project_type, _calculate_similarity_hash, _assess_status, analyze_all, find_similar_repos, generate_report, print_summary`

### `tools/migration/repo_migration_helper.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `RepoMigrationHelper`
- functions: `main, __init__, _load_status, _save_status, clone_repo, clone_from_list, update_review_status, list_status, list_ready_to_publish, generate_publish_script`

### `tools/monitoring/unified_monitor.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `UnifiedMonitor, WorkspaceHealth`
- functions: `main, __init__, monitor_queue_health, check_message_queue_file, monitor_service_health, monitor_disk_usage, monitor_agent_status, monitor_workspace_health, monitor_test_coverage, run_full_monitoring, print_monitoring_report, check_agent_workspace`

### `tools/security/check_sensitive_files.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `run_git_command, check_tracked_sensitive_files, check_gitignore_coverage, print_security_report, main`

### `tools/security/unified_security_scanner.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `run_command, scan_sensitive_files, scan_content_secrets, audit_python_dependencies, audit_npm_dependencies, main`

### `tools/swarm/agents/import_healer.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `RewriteDecision`
- functions: `discover_modules, load_rewrite_map, resolve_module, rewrite_line, compile_safe, process_file, parse_args, main`

### `tools/swarm/tests/check_import_healer_coverage.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `to_relpath, calculate_coverage, load_baseline, write_baseline, main`

### `tools/swarm/tests/fixtures/broken_imports.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/swarm/tests/fixtures/modules/pkg_alpha/config.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/swarm/tests/fixtures/modules/pkg_alpha/helpers.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `ping`

### `tools/swarm/tests/fixtures/modules/pkg_beta/config.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/swarm/tests/test_import_healer.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `test_import_healer_validation`

### `tools/swarm/tests/validate_import_healer.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `run_validation`

### `tools/thea/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/thea/analyze_chatgpt_selectors.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `ChatGPTAnalyzer`
- functions: `main, __init__, setup_driver, load_page, analyze_input_elements, analyze_button_elements, _analyze_element, _score_element_relevance, suggest_selectors, generate_selector_report, _generate_recommendations, save_report`

### `tools/thea/debug_chatgpt_elements.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `debug_chatgpt_elements`

### `tools/thea/demo_thea_interactive.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `interactive_demo`

### `tools/thea/demo_thea_live.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `demo_thea_automation`

### `tools/thea/demo_thea_simple.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/thea/demo_working_thea.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `demo_working`

### `tools/thea/run_headless_refresh.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `main`

### `tools/thea/send_prompt_file.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `send_prompt_from_file, main`

### `tools/thea/setup_thea_cookies.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TheaCookieSetup`
- functions: `main, __init__, initialize_driver, wait_for_manual_login, _debug_page_state, save_cookies_after_login, verify_setup, run_setup, cleanup`

### `tools/thea/simple_thea_communication.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `SimpleTheaCommunication`
- functions: `main, __init__, initialize_driver, ensure_login, send_message, wait_for_response, save_response, communicate, cleanup`

### `tools/thea/tell_thea_session_summary.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `tell_thea`

### `tools/thea/thea_authentication_handler.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TheaAuthenticationHandler`
- functions: `__init__, ensure_login, _automated_login, _handle_2fa, _manual_login, force_logout`

### `tools/thea/thea_automation.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TheaConfig, TheaAutomation`
- functions: `main, __init__, save_cookies, load_cookies, has_valid_cookies, start_browser, is_logged_in, ensure_login, send_message, wait_for_response, save_conversation, communicate, cleanup, __enter__, __exit__`

### `tools/thea/thea_automation_browser.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TheaBrowserManager`
- functions: `__init__, start_browser, is_logged_in, ensure_login, _handle_manual_login, cleanup, get_driver`

### `tools/thea/thea_automation_cookie_manager.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TheaCookieManager`
- functions: `__init__, save_cookies, load_cookies, has_valid_cookies, _filter_auth_cookies, _load_cookies_into_driver, _filter_valid_cookies`

### `tools/thea/thea_automation_messaging.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TheaMessagingManager`
- functions: `__init__, send_message, wait_for_response, _process_response_result, save_conversation`

### `tools/thea/thea_cookie_manager.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TheaCookieManager`
- functions: `__init__, save_cookies, load_cookies, has_valid_cookies, clear_cookies`

### `tools/thea/thea_headless_send.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `run_headless_prompt, main`

### `tools/thea/thea_keepalive.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `read_last_refresh, write_last_refresh, ensure_keepalive, main`

### `tools/thea/thea_login_detector.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TheaLoginDetector`
- functions: `__init__, is_logged_in, _check_url_patterns, _check_logout_button, _check_user_menu, _check_new_chat_button, _check_login_buttons`

### `tools/thea/thea_login_handler.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TheaCookieManager, TheaLoginHandler`
- functions: `create_thea_login_handler, check_thea_login_status, __init__, save_cookies, load_cookies, has_valid_cookies, clear_cookies, __init__, ensure_login, _is_logged_in, _automated_login, _manual_login, _is_on_thea_page, _navigate_to_thea, force_logout`

### `tools/thea/thea_login_handler_refactored.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `TheaLoginHandler`
- functions: `__init__, ensure_login, force_logout, _is_logged_in`

### `tools/thea/thea_undetected_helper.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `create_undetected_driver, create_standard_driver, check_undetected_available, get_installation_instructions`

### `tools/toolbelt/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/toolbelt/__main__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `main, print_help, print_tools`

### `tools/toolbelt/executors/__init__.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools/toolbelt/executors/agent_executor.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `AgentExecutor`
- functions: `execute`

### `tools/toolbelt/executors/compliance_executor.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `ComplianceExecutor`
- functions: `execute, _count_classes, _count_functions, _check_file, _scan_violations, _test_imports`

### `tools/toolbelt/executors/compliance_tracking_executor.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `ComplianceTrackingExecutor`
- functions: `__init__, execute, _take_snapshot, _show_history, _show_trends, _launch_dashboard, _compare_snapshots`

### `tools/toolbelt/executors/consolidation_executor.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `ConsolidationExecutor`
- functions: `execute, _find_duplicates, _suggest_consolidation, _verify_consolidation`

### `tools/toolbelt/executors/leaderboard_executor.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `LeaderboardExecutor`
- functions: `__init__, execute, _show_leaderboard, _agent_details, _top_agents, _award_achievement`

### `tools/toolbelt/executors/messaging_executor.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `MessagingExecutor`
- functions: `execute`

### `tools/toolbelt/executors/onboarding_executor.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `OnboardingExecutor`
- functions: `__init__, execute, _soft_onboarding, _hard_onboarding, _onboarding_status`

### `tools/toolbelt/executors/refactor_executor.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `RefactorExecutor`
- functions: `execute, _split_file, _auto_group_classes, _apply_facade, _extract_classes`

### `tools/toolbelt/executors/swarm_executor.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `SwarmExecutor`
- functions: `__init__, execute, _captain_snapshot, _agent_checkin, _active_agents, _swarm_health`

### `tools/toolbelt/executors/v2_executor.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `V2Executor`
- functions: `execute`

### `tools/toolbelt/executors/vector_executor.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `VectorExecutor`
- functions: `execute`

### `tools/toolbelt_registry.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `ToolRegistry`
- functions: `__init__, _build_flag_map, get_tool_for_flag, get_tool_by_name, list_tools, get_all_flags`

### `tools/validation/audit_imports.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `test_import, file_to_module_path, audit_imports, main`

### `tools/validation/schema_org_validator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `SchemaOrgValidator`
- functions: `main, __init__, fetch_html, extract_json_ld, validate_schema_structure, validate_required_properties, validate_all_schemas, check_google_rich_results_compatibility`

### `tools/validation/template_structure_linter.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `_create_message, _assert_sections_present, _assert_in_order, lint_template, main`

### `tools/validation/unified_validator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `UnifiedValidator`
- functions: `main, __init__, validate_ssot_config, _get_import_string, validate_imports, validate_tracker_status, validate_session_transition, validate_refactor_status, validate_consolidation, validate_queue, validate_all, print_validation_report`

### `tools/verification/integration_test_coordinator.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `ModuleInfo, TestCoverage, IntegrationTestCoordinator`
- functions: `main, __init__, analyze_module, generate_test_template, validate_test_coverage, create_coordination_report, analyze_dependencies, check_integration_points`

### `tools/verification/stress_test_messaging_queue.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `none`
- functions: `create_mock_delivery_callback, create_real_delivery_callback, run_stress_test, run_comparison_mode, main, delivery_callback, delivery_callback, delivery_callback, process_queue`

### `tools/verification/unified_verifier.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `UnifiedVerifier`
- functions: `create_parser, main, __init__, verify_repo, verify_merge, verify_file, verify_cicd, verify_credentials`

### `tools/website_audit_ollama.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `WebsiteAuditOllama`
- functions: `__init__, capture_screenshot_selenium, save_screenshot, _generate_recommendations, _generate_batch_summary`

### `tools/wordpress/unified_wordpress.py`

- risk: `legacy_review`
- syntax_ok: `True`
- classes: `UnifiedWordPress`
- functions: `main, __init__, deploy_admin, deploy_rest_api, deploy_sftp, theme_activate, theme_check_syntax, debug_enable, debug_deployer, admin_clear_transients, admin_diagnose_path`

### `tools_v2/__init__.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ToolbeltCore`
- functions: `none`

### `tools_v2/adapters/__init__.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools_v2/adapters/base_adapter.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ToolSpec, ToolResult, IToolAdapter`
- functions: `validate_params, to_dict, get_spec, validate, execute, get_help`

### `tools_v2/adapters/error_types.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ToolbeltError, ToolNotFoundError, ToolValidationError, ToolExecutionError, ToolDependencyError, ToolConfigurationError`
- functions: `format_toolbelt_error, __init__, __init__, __init__, __init__`

### `tools_v2/advisor_cli.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `main, _print_recommendation, _print_validation, _print_swarm_analysis`

### `tools_v2/categories/__init__.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools_v2/categories/agent_activity_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `AgentActivityTrackerTool, AgentActivityMonitorTool`
- functions: `get_name, get_description, get_spec, validate, execute, _check_agent_activity, get_name, get_description, get_spec, validate, execute`

### `tools_v2/categories/agent_ops_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `AgentStatusTool, ClaimTaskTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/analysis_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ProjectScanTool, ComplexityTool, DuplicationTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/autonomous_workflow_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `WorkflowAssignmentTask, Agent, Assignment, AutoAssignmentEngine, AgentStatusData, TeamCoordinationDashboard`
- functions: `get_tools, __post_init__, __post_init__, __init__, assign_task, _calculate_fit_score, _calculate_skill_match, _get_available_agents, _load_agents, _send_assignment_message, __init__, get_dashboard_view, _load_all_agent_statuses, _parse_agent_status, _estimate_gas_level, _detect_blockers, _suggest_next_action, _generate_summary`

### `tools_v2/categories/bi_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `QuickMetricsTool, RepoROICalculatorTool, TaskROICalculatorTool, MarkovROIOptimizerTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/captain_coordination_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `CompletionProcessorTool, LeaderboardUpdaterTool, NextTaskPickerTool, ROIQuickCalculatorTool`
- functions: `get_spec, validate, execute, _update_agent_status, _log_to_swarm_brain, get_spec, validate, execute, get_spec, validate, execute, _calculate_task_fit, get_spec, validate, execute`

### `tools_v2/categories/captain_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools_v2/categories/captain_tools_advanced.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `PointsCalculatorTool, MissionAssignTool, MarkovOptimizerTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/captain_tools_architecture.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ArchitecturalCheckerTool`
- functions: `get_spec, validate, execute`

### `tools_v2/categories/captain_tools_coordination.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `MultiFuelDelivery, MarkovROIRunner, SwarmStatusDashboard, MorningBriefingTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, _generate_markdown_briefing`

### `tools_v2/categories/captain_tools_core.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `StatusCheckTool, GitVerifyTool, WorkVerifyTool, IntegrityCheckTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/captain_tools_extension.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools_v2/categories/captain_tools_messaging.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `SelfMessageTool, MessageAllAgentsTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/captain_tools_monitoring.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `GasDeliveryTool, LeaderboardUpdateTool, CycleReportTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, _update_agent_entry, get_spec, validate, execute`

### `tools_v2/categories/captain_tools_utilities.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `FindIdleAgentsTool, GasCheckTool, UpdateLogTool, ToolbeltHelpTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/captain_tools_validation.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `FileExistenceValidator, ProjectScanRunner, PhantomTaskDetector`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/communication_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `DiscordRouterPoster, DiscordPostTool`
- functions: `get_tools, __init__, post_update, __init__, execute`

### `tools_v2/categories/compliance_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ComplianceHistoryTool, PolicyCheckTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/config_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ValidateConfigSSOTAdapter, ListConfigSourcesAdapter, CheckConfigImportsAdapter`
- functions: `get_spec, get_help, validate, execute, get_spec, get_help, validate, execute, get_spec, get_help, validate, execute`

### `tools_v2/categories/coordination_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `FindDomainExpertAdapter, RequestExpertReviewAdapter, CheckCoordinationPatternsAdapter, SwarmOrchestratorAdapter, SwarmStatusBroadcasterAdapter, MissionControlAdapter, CoordinateValidatorAdapter`
- functions: `get_spec, get_help, validate, execute, get_spec, get_help, validate, execute, get_spec, get_help, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/dashboard_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `DashboardGenerateTool, DashboardDataAggregateTool, DashboardHTMLTool, DashboardChartsTool, DashboardStylesTool, DiscordStatusDashboardTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/debate_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `DebateStartTool, DebateVoteTool, DebateStatusTool, DebateNotifyTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/discord_profile_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `DiscordProfileViewerTool`
- functions: `get_name, get_description, get_spec, validate, execute, _load_profile`

### `tools_v2/categories/discord_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `DiscordBotHealthTool, DiscordBotStartTool, DiscordTestMessageTool`
- functions: `get_name, get_description, execute, get_name, get_description, execute, get_name, get_description, execute`

### `tools_v2/categories/discord_webhook_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `CreateWebhookTool, ListWebhooksTool, SaveWebhookTool, TestWebhookTool, WebhookManagerTool`
- functions: `get_name, get_description, execute, _get_creation_instructions, get_name, get_description, execute, _load_webhooks_from_config, _extract_webhooks_from_dict, get_name, get_description, execute, _save_to_env, _save_to_config, get_name, get_description, execute, get_name`

### `tools_v2/categories/docs_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `DocsSearchTool, DocsExportTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/github_consolidation_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `GitHubRepoSimilarityAnalyzerTool, GitHubRepoConsolidationPlannerTool, GitHubRepoMergeExecutorTool`
- functions: `get_name, get_description, get_spec, validate, execute, _fetch_user_repos, _analyze_similarity, _calculate_similarity, _string_similarity, _get_group_similarity, _recommend_primary, _generate_recommendations, get_name, get_description, get_spec, validate, execute, _analyze_repo`

### `tools_v2/categories/health_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `HealthPingTool, SnapshotTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/import_fix_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ImportValidatorTool, ModuleExtractorTool, QuickLineCountTool, PublicAPIImportValidatorTool, ImportChainValidatorTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/infrastructure_audit_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `OrchestratorScanTool, FileLineCounterTool, ToolRuntimeAuditTool, BrokenToolsAuditTool, ProjectComponentsAuditTool`
- functions: `get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec`

### `tools_v2/categories/infrastructure_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools_v2/categories/infrastructure_utility_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ModuleExtractorPlannerTool, InfrastructureROICalculatorTool, BrowserPoolManagerTool`
- functions: `get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/infrastructure_workspace_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `WorkspaceHealthMonitorTool, WorkspaceAutoCleanerTool, AgentStatusQuickCheckTool, AutoStatusUpdaterTool, SessionTransitionAutomatorTool, SwarmStatusBroadcasterTool`
- functions: `get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec`

### `tools_v2/categories/integration_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `FindSSOTViolationsAdapter, FindDuplicateFunctionalityAdapter, FindIntegrationOpportunitiesAdapter, CheckImportDependenciesAdapter, AuditImportsTool`
- functions: `get_spec, get_help, validate, execute, get_spec, get_help, validate, execute, get_spec, get_help, validate, execute, get_spec, get_help, validate, execute, get_spec, get_help`

### `tools_v2/categories/intelligent_mission_advisor.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `IntelligentMissionAdvisor`
- functions: `get_mission_advisor, __init__, _load_agent_status, _identify_specialty, _load_swarm_brain, _extract_patterns, _load_other_agents_work, _load_leaderboard, get_mission_recommendation, _scan_real_available_tasks, _check_conflicts, _match_specialty, _calculate_roi, _verify_task, _generate_intelligent_briefing, _explain_specialty_match, _generate_approach_recommendation, _identify_risks`

### `tools_v2/categories/intelligent_mission_advisor_adapter.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `MissionAdvisorTool, OrderValidatorTool, SwarmAnalyzerTool, RealtimeGuidanceTool`
- functions: `get_spec, validate, execute, _format_summary, get_spec, validate, execute, _format_validation_summary, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/intelligent_mission_advisor_analysis.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `IntelligentMissionAnalysis`
- functions: `__init__, scan_real_available_tasks, check_conflicts, match_specialty, calculate_roi, verify_task, identify_risks, calculate_success_probability`

### `tools_v2/categories/intelligent_mission_advisor_guidance.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `IntelligentMissionGuidance`
- functions: `__init__, generate_intelligent_briefing, explain_specialty_match, generate_approach_recommendation, calculate_confidence, get_current_rank, find_relevant_patterns, generate_execution_guidance, get_realtime_guidance, analyze_swarm_state, generate_fallback_suggestions`

### `tools_v2/categories/memory_safety_adapters.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `MemoryLeakDetectorTool, FileVerificationTool, UnboundedScanTool, MemorySafetyImportValidatorTool, FileHandleCheckTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/memory_safety_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `detect_memory_leaks, verify_files_exist, scan_unbounded_structures, validate_imports, check_file_handles`

### `tools_v2/categories/message_analytics_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `MessagePatternAnalyzerTool, MessageMetricsDashboardTool, MessageLearningExtractorTool`
- functions: `_counter_to_dict, __init__, get_spec, validate, execute, get_help, __init__, get_spec, validate, execute, _is_recent, get_help, __init__, get_spec, validate, execute, get_help`

### `tools_v2/categories/message_history_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `MessageHistoryViewerTool, MessageHistoryAnalyzerTool, MessageCompressionTool`
- functions: `get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec, validate, execute`

### `tools_v2/categories/message_task_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `MessageIngestTool, TaskParserTool, TaskFingerprintTool`
- functions: `execute, execute, execute`

### `tools_v2/categories/messaging_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `SendMessageTool, BroadcastTool, InboxCheckTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/mission_calculator.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `calculate_optimal_task, build_context_package, format_mission_brief`

### `tools_v2/categories/mod_deployment_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ThunderstoreSearchTool, ModInstallTool, ModUpdateTool, ModDependencyResolverTool, ModProfileTool, ServerHealthCheckTool, ModRollbackTool`
- functions: `get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec`

### `tools_v2/categories/observability_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `MetricsSnapshotTool, MetricsTool, SystemHealthTool, SLOCheckTool`
- functions: `execute, execute, execute, execute`

### `tools_v2/categories/onboarding_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `SoftOnboardTool, HardOnboardTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/oss_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `OSSCloneTool, OSSFetchIssuesTool, OSSImportIssuesTool, OSSPortfolioTool, OSSStatusTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/proposal_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `CreateProposalTool, ListProposalsTool, ViewProposalTool, ContributeProposalTool, StartDebateTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/queue_monitor_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `QueueStatusMonitorTool`
- functions: `get_name, get_description, get_spec, validate, execute`

### `tools_v2/categories/refactoring_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `FileSizeCheckTool, AutoExtractTool, TestPyramidAnalyzerTool, LintFixTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, _generate_recommendations, get_spec, validate, execute`

### `tools_v2/categories/security_audit_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ExternalResource, ResourceParser, SecurityAuditTool, FetchResult`
- functions: `_apex_domain, _fetch_status, __init__, handle_starttag, get_spec, validate, execute, _fetch, _check_security_headers, _analyze_resources, _check_rate_limits, _probe_rate_limit, _extract_backend_info, _probe_paths, _scan_ports, _probe_subdomains, _score_findings`

### `tools_v2/categories/session_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `SessionCleanupTool, PassdownTool, SessionPointsCalculatorTool`
- functions: `get_spec, validate, execute, _create_passdown, _create_devlog, _update_swarm_brain, _update_status, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/ssot_validation_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `SSOTViolationDetector, SSOTPatternValidator`
- functions: `get_spec, validate, execute, _detect_violations, _find_duplicate_classes, _find_duplicate_functions, _find_multiple_repositories, _find_scattered_config, _find_duplicate_constants, _generate_summary, get_spec, validate, execute, _validate_pattern, _validate_repository_pattern, _validate_service_pattern, _validate_config_pattern`

### `tools_v2/categories/swarm_brain_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `TakeNoteTool, ShareLearningTool, SearchKnowledgeTool, LogSessionTool, GetAgentNotesTool`
- functions: `execute, execute, execute, execute, execute`

### `tools_v2/categories/swarm_consciousness.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `SwarmPulseTool`
- functions: `get_spec, validate, execute, _collect_swarm_pulse, _get_agent_pulse, _dashboard_view, _detect_conflicts, _find_related_work, _captain_command_center`

### `tools_v2/categories/swarm_mission_control.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `SwarmMissionControl, SwarmConflictDetector, ContextPackageBuilder`
- functions: `get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec, validate, execute, _find_related_files, _find_similar_work, _find_current_violations`

### `tools_v2/categories/swarm_state_reader.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `read_swarm_state, read_agent_context, get_agent_specialty, analyze_available_work`

### `tools_v2/categories/system_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `SystemDateTimeTool, CheckInSystemTool, CheckInViewerTool`
- functions: `get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec, validate, execute, get_name, get_description, get_spec, validate, execute`

### `tools_v2/categories/test_generation_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `TestFileGeneratorTool, CoveragePyramidReportTool`
- functions: `get_spec, validate, execute, _generate_test_template, get_spec, validate, execute`

### `tools_v2/categories/testing_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `CoverageReportTool, MutationGateTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/v2_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `V2CheckTool, V2ReportTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/validation_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `SmokeTestTool, FeatureFlagTool, RollbackTool, ValidationReportTool, IntegrityValidatorTool, SSOTValidatorTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/vector_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `TaskContextTool, VectorSearchTool, IndexWorkTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/web_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `DiscordMermaidRendererTool, DiscordWebTestTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/categories/workflow_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `InboxCleanupTool, MissionClaimTool, ROICalculatorTool`
- functions: `get_spec, validate, execute, get_spec, validate, execute, get_spec, validate, execute`

### `tools_v2/core/__init__.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools_v2/core/tool_facade.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools_v2/core/tool_spec.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ToolSpec`
- functions: `__init__, validate_params`

### `tools_v2/demo_swarm_pulse.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `demo_swarm_pulse`

### `tools_v2/rank_tools_v2.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `main`

### `tools_v2/test_bi_tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `test_bi_metrics, test_bi_roi_task, test_bi_roi_optimize, main`

### `tools_v2/test_toolbelt_basic.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `test_basic_functionality`

### `tools_v2/tests/__init__.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools_v2/tests/test_adapters.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `TestToolSpec, TestToolResult, TestIToolAdapter`
- functions: `test_spec_creation, test_validate_params_success, test_validate_params_failure, test_result_creation, test_result_to_dict, test_adapter_implements_interface, test_adapter_get_spec, test_adapter_validate, test_adapter_get_help`

### `tools_v2/tests/test_core.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `TestToolbeltCore`
- functions: `test_core_initialization, test_list_tools, test_list_categories, test_tool_not_found, test_execution_history_recording, test_clear_history, test_get_execution_history`

### `tools_v2/tests/test_registry.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `TestToolRegistry`
- functions: `test_registry_initialization, test_singleton_pattern, test_list_tools, test_list_by_category, test_resolve_valid_tool, test_resolve_invalid_tool, test_caching, test_export_lock`

### `tools_v2/tests/test_smoke_categories.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `TestCategoryImports, TestAdapterInterface`
- functions: `test_import_vector_tools, test_import_messaging_tools, test_import_analysis_tools, test_import_v2_tools, test_import_agent_ops_tools, test_import_testing_tools, test_import_compliance_tools, test_import_onboarding_tools, test_import_docs_tools, test_import_health_tools, test_adapter_implements_interface`

### `tools_v2/tool_registry.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ToolRegistry`
- functions: `get_tool_registry, __init__, _load_registry_data, _resolve_tool_class, get_tool_class, get_tool, resolve, list_tools, list_by_category, export_lock, get_categories, clear_cache`

### `tools_v2/toolbelt_core.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ToolbeltCore`
- functions: `get_toolbelt_core, __init__, run, list_tools, list_categories, get_tool_help, get_execution_history, clear_history, _record_execution`

### `tools_v2/utils/__init__.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `tools_v2/utils/discord_mermaid_renderer.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `DiscordMermaidRenderer`
- functions: `__init__, extract_mermaid_diagrams, render_mermaid_to_image_url, render_mermaid_to_file, render_to_file, replace_mermaid_with_images, post_to_discord_with_mermaid`

### `mcp_servers/__init__.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `mcp_servers/backup_automation_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `create_backup, list_backups, restore_backup, verify_backup, get_storage_usage, apply_retention, list_backup_contents, compare_backups, sync_to_cloud, main`

### `mcp_servers/cicd_helper_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `_run_command, _get_current_branch, check_ci_status, get_failed_logs, retry_failed_job, list_workflows, cancel_workflow, get_workflow_artifacts, main`

### `mcp_servers/code_quality_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `detect_linter, run_linter, auto_fix_lint, format_code, check_types, find_dead_code, handle_tool_call, main`

### `mcp_servers/database_operations_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `detect_orm, run_migration, rollback_migration, seed_database, backup_database, reset_database, handle_tool_call, main`

### `mcp_servers/dependency_management_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `_run_command, _detect_package_manager, check_outdated, check_vulnerabilities, update_package, add_package, remove_unused, main`

### `mcp_servers/discord_integration_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `_get_webhook_manager, _get_status_poster, _get_role_sync, add_webhook, remove_webhook, list_webhooks, test_webhook, send_message, send_server_status, send_alert, send_player_notification, send_leaderboard, create_status_message, update_status_message, list_status_messages, add_role_mapping, list_role_mappings, link_account`

### `mcp_servers/documentation_generator_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `generate_api_docs, update_readme, generate_type_docs, check_doc_coverage, validate_links, handle_tool_call, main`

### `mcp_servers/environment_setup_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `install_dependencies, setup_env_file, validate_environment, setup_database, health_check, handle_tool_call, main`

### `mcp_servers/git_operations_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `verify_git_work, get_recent_commits, check_file_history, validate_commit, verify_work_exists_mcp, main`

### `mcp_servers/issue_todo_tracker_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `extract_todos, create_issue_from_todo, link_todo_to_issue, list_stale_issues, close_completed, handle_tool_call, main`

### `mcp_servers/memory_safety_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `main`

### `mcp_servers/messaging_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `MockQueue, PackCoordinator`
- functions: `send_agent_message, broadcast_message, get_agent_status, main, get_queue, send, __init__, roll_call`

### `mcp_servers/mission_control_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `check_agent_status, assign_mission, check_integrity, update_leaderboard, calculate_points, main`

### `mcp_servers/mod_deployment_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `search_mods, get_mod_info, install_mod, update_mods, list_installed_mods, resolve_dependencies, check_server_health, create_rollback_point, rollback, manage_profile, main`

### `mcp_servers/observability_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `get_metrics_snapshot, get_metric, check_system_health, check_slo_compliance, main`

### `mcp_servers/performance_profiler_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `profile_startup, find_slow_tests, analyze_bundle, memory_snapshot, benchmark_function, handle_tool_call, main`

### `mcp_servers/player_analytics_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `_get_db, _get_tracker, _get_analytics, _get_reports, player_join, player_leave, log_event, get_active_players, get_player, search_players, get_player_sessions, get_player_events, get_engagement_metrics, get_retention_metrics, get_peak_hours, get_player_segments, get_leaderboard, get_server_comparison`

### `mcp_servers/refactoring_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `check_file_size, auto_extract_code, fix_linting_issues, analyze_test_pyramid, main`

### `mcp_servers/release_management_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `_run_command, _get_current_version, _parse_version, bump_version, generate_changelog, create_release, tag_version, validate_release, main`

### `mcp_servers/security_scanner_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `scan_secrets, check_dependencies, audit_permissions, check_env_exposure, generate_security_report, handle_tool_call, main`

### `mcp_servers/server_monitoring_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `collect_metrics, analyze_performance, check_alerts, acknowledge_alert, configure_discord_alerts, get_metric_history, get_weekly_report, main`

### `mcp_servers/swarm_brain_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `share_learning, record_decision, search_swarm_knowledge, take_note, get_agent_notes, main`

### `mcp_servers/task_manager_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `read_task_log, write_task_log, add_to_inbox, mark_task_complete, move_to_waiting_on, get_tasks, main`

### `mcp_servers/testing_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `run_coverage_analysis, run_mutation_tests, main`

### `mcp_servers/v2_compliance_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `count_lines, count_function_lines, check_v2_compliance, validate_file_size, check_function_size, get_v2_exceptions, main`

### `mcp_servers/website_audit_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `audit_website_screenshot, audit_multiple_websites, get_available_ollama_models, analyze_website_design, analyze_website_ux, analyze_website_seo, audit_website_full, audit_website_batch, check_ollama_status`

### `mcp_servers/website_manager_server.py`

- risk: `adapter_surface`
- syntax_ok: `True`
- classes: `none`
- functions: `create_wordpress_page, deploy_file_to_wordpress, add_page_to_menu, list_wordpress_pages, create_blog_post_for_site, create_report_page_for_site, generate_image_prompts, purge_wordpress_cache, main`

### `swarm_mcp/__init__.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `swarm_mcp/cli.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `cmd_status, cmd_send, cmd_inbox, cmd_search, cmd_learn, cmd_tasks, cmd_assign, cmd_vote, cmd_conflict, cmd_profile, cmd_prove, cmd_patterns, main`

### `swarm_mcp/core/__init__.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `swarm_mcp/core/agent_dna.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `TaskRecord, AgentProfile, AgentDNA`
- functions: `__init__, _load_data, _save_profile, _extract_module, record_task, _update_profile, _calculate_strengths, get_profile, find_best_agent, get_task_estimate, get_leaderboard, suggest_pairing`

### `swarm_mcp/core/brain.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `Learning, Decision, SwarmBrain`
- functions: `__init__, _generate_id, share_learning, record_decision, search, get_agent_notes, add_note, get_stats`

### `swarm_mcp/core/conflict.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ConflictSeverity, WorkIntent, Conflict, ConflictDetector`
- functions: `__init__, _generate_id, _load_intents, _save_intents, _normalize_path, _extract_module, _calculate_similarity, declare_intent, check_conflicts, complete_work, abandon_work, get_active_intents, get_agent_intent, get_blocked_files`

### `swarm_mcp/core/consensus.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `VoteType, ConsensusRule, Vote, Proposal, ConsensusEngine`
- functions: `__init__, _generate_id, _load_proposals, _save_proposal, propose, vote, get_tally, resolve, get_open_proposals, get_agent_pending_votes`

### `swarm_mcp/core/coordinator.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `WolfStatus, Prey, PackCoordinator`
- functions: `__init__, get_status, roll_call, get_ready_wolves, assign_hunt, broadcast, scout_territory, get_best_prey`

### `swarm_mcp/core/memory.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `HuntingLore, HuntRecord, PackMemory`
- functions: `__init__, _generate_id, share_lore, record_hunt, recall, get_wolf_notes, add_note, pack_stats`

### `swarm_mcp/core/messaging.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `HowlUrgency, HowlType, Howl, MessageQueue`
- functions: `get_queue, howl, broadcast, __init__, _generate_id, send, listen, mark_heard, count_unheard`

### `swarm_mcp/core/messaging_templates.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `MessageTemplateCategory, MessageTemplateInput`
- functions: `_coerce_category, render_message_template`

### `swarm_mcp/core/pattern_miner.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `CoordinationEvent, Pattern, Suggestion, PatternMiner`
- functions: `__init__, _generate_id, _load_data, _save_event, _save_pattern, record_event, _mine_patterns, _mine_pairing_patterns, _mine_sequence_patterns, _mine_timing_patterns, _mine_context_patterns, suggest, get_patterns, get_stats`

### `swarm_mcp/core/recovery.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `FailureEvent, RecoveryManager`
- functions: `__init__, analyze_failure, propose_strategy, execute_recovery, _git_rollback, _reinstall_deps`

### `swarm_mcp/core/task_scoring.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `ScoredTask, TaskScorer`
- functions: `roi_score, __init__, score_tasks, select_next_task, parse_task_metadata`

### `swarm_mcp/core/verification.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `VerificationType, VerificationResult, VerificationHarness`
- functions: `__init__, verify_page_fetch, verify_unit_test, verify_file_exists, run_suite`

### `swarm_mcp/core/work_proof.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `FileSnapshot, WorkCommitment, WorkProof, WorkProofSystem`
- functions: `__init__, _generate_hash, _file_hash, _snapshot_file, _load_commitments, _save_commitment, _get_git_commits_since, _get_git_diff_stats, commit, prove, verify, get_agent_proofs`

### `swarm_mcp/servers/__init__.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `none`

### `swarm_mcp/servers/control.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `get_coordinator, check_pack_status, assign_hunt, scout_territory, main`

### `swarm_mcp/servers/memory.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `share_learning, record_decision, search_knowledge, main`

### `swarm_mcp/servers/messaging.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `send_agent_message, broadcast_message, read_messages, main`

### `swarm_mcp/servers/tasks.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `read_task_log, write_task_log, add_to_inbox, mark_task_complete, get_tasks, select_next_task, verify_task_completion, recover_system, main`

### `swarm_mcp/servers/tools.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `execute_toolbelt, list_available_tools, main`

### `swarm_mcp/tools/__init__.py`

- risk: `keep_active`
- syntax_ok: `True`
- classes: `none`
- functions: `none`
