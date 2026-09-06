"""Render a passdown packet into the handoff a receiving agent reads."""

from __future__ import annotations

from typing import Any

RULE = "=" * 62


def _section(title: str) -> str:
    return f"\n{RULE}\n{title}\n{RULE}\n"


def _yes(value: Any) -> str:
    return "yes" if value else "no"


def _kv(pairs: list[tuple[str, Any]]) -> str:
    return "\n".join(f"  {key}: {value}" for key, value in pairs if value not in (None, ""))


def render(packet: dict[str, Any]) -> str:
    out: list[str] = []
    focus = packet.get("focus", {})
    add = out.append

    add(f"DREAM.OS PASSDOWN  ({packet.get('generated_at')})")
    add(f"schema: {packet.get('schema')}   focus repo: {focus.get('repo')}   lane: {focus.get('lane') or 'unassigned'}")

    # ---------------------------------------------------------- environment
    machine = packet.get("generated_by", {}).get("machine", {})
    operator = packet.get("operator", {})
    add(_section("CURRENT OPERATOR ENVIRONMENT"))
    add(_kv([
        ("operator", operator.get("operator")),
        ("environment", machine.get("environment")),
        ("projects root", operator.get("projects_root")),
    ]))
    for note in operator.get("notes", []):
        add(f"  note: {note}")

    add(_section("CURRENT MACHINE"))
    add(_kv([
        ("hostname", machine.get("hostname")),
        ("platform", machine.get("platform")),
        ("python", machine.get("python")),
        ("user", machine.get("user")),
        ("cwd", machine.get("cwd")),
    ]))
    tools = packet.get("tools", {})
    add("  tools: " + ", ".join(f"{name}={_yes(value)}" for name, value in sorted(tools.items())))

    # ------------------------------------------------------------- cliprun
    cliprun = operator.get("cliprun", {})
    add(_section("HOW TO USE CLIPRUN"))
    add("  Victor runs important work from Android Termux via CPC. Give him")
    add("  paste-ready scripts in this exact shape:")
    add("")
    add("    cat > /tmp/<task_name>_001.sh << 'EOF'")
    add("    #!/usr/bin/env bash")
    add("    set -euo pipefail")
    add("")
    add("    # commands")
    add("    EOF")
    add("")
    add("    chmod +x /tmp/<task_name>_001.sh")
    default_usage = '"$HOME/bin/cliprun" bash /tmp/<task_name>_001.sh'
    add("    " + str(cliprun.get("usage") or default_usage))
    add("")
    add(_kv([
        ("cliprun present here", _yes(cliprun.get("cliprun_present"))),
        ("CPC toolchain", cliprun.get("cpc_tools_dir")),
    ]))

    # ----------------------------------------------------------------- vps
    vps = packet.get("vps", {})
    add(_section("HOW TO ACCESS VPS"))
    add(vps.get("ssh_hint", "  (no ssh hint available)"))

    add(_section("CURRENT VPS STATE"))
    add(_kv([
        ("host", f"{vps.get('user')}@{vps.get('host')}"),
        ("reachable", _yes(vps.get("reachable"))),
        ("hostname", vps.get("hostname")),
        ("uptime", vps.get("uptime")),
        ("healthy", _yes(vps.get("healthy"))),
        ("reason", vps.get("reason")),
        ("repo checkouts", ", ".join(vps.get("repo_checkouts", [])) or None),
    ]))

    add(_section("CURRENT RUNNER STATE"))
    add(_kv([
        ("runner", vps.get("runner_name")),
        ("directory", vps.get("runner_dir")),
        ("labels", ",".join(vps.get("runner_labels", []))),
        ("process alive", _yes(vps.get("runner_alive"))),
        ("registered (.runner present)", _yes(vps.get("runner_registered"))),
        ("persistence", vps.get("runner_persistence")),
        ("dreamosd process", _yes(vps.get("daemon_alive"))),
    ]))
    add("  DO NOT re-register or restart the runner casually. Reboot-persistent")
    add("  service installation is a separate, unclaimed lane.")

    # ----------------------------------------------------------- authority
    dv = packet.get("dreamvault", {})
    authority = dv.get("authority", {})
    add(_section("CURRENT DREAMVAULT AUTHORITY"))
    if authority.get("available"):
        add(f"  root: {authority.get('root')}")
        add("  canonical owners:")
        for domain, owner in sorted(authority.get("canonical_owners", {}).items()):
            add(f"    {domain}: {owner}")
        protected = authority.get("protected_repos") or []
        if protected:
            add("  destructive-cleanup protected repos: " + ", ".join(protected))
    else:
        add(f"  UNAVAILABLE: {authority.get('reason')}")
    planner = dv.get("planner", {})
    if planner.get("available"):
        add(_kv([("planner next lane", planner.get("next_lane")), ("planner next task", planner.get("next_task"))]))

    gh = packet.get("github", {})
    add(_section("CURRENT MASTER"))
    if gh.get("available"):
        add(_kv([
            ("repo", gh.get("repo")),
            ("default branch", gh.get("default_branch")),
            ("master head", gh.get("master_head")),
            ("source", gh.get("source")),
        ]))
        if gh.get("stale_risk"):
            add("  WARNING: derived from a local fetched ref; may be stale.")
    else:
        add(f"  UNAVAILABLE: {gh.get('reason')}  -- do NOT assume the previous handoff's master still holds.")

    add(_section("CURRENT OPEN PRS + EXACT-HEAD CI"))
    prs = gh.get("open_prs") or []
    if not prs:
        add("  none reported" if gh.get("available") else "  unknown (GitHub authority unavailable)")
    for pull in prs:
        add(f"  #{pull.get('number')} {pull.get('title')}")
        add(_kv([
            ("head ref", pull.get("head_ref")),
            ("exact head", pull.get("head")),
            ("draft", _yes(pull.get("draft"))),
            ("mergeable", pull.get("mergeable")),
        ]))
        ci = pull.get("ci") or {}
        if ci.get("available"):
            verdict = "GREEN" if ci.get("green") else ("FAILING" if ci.get("failing") else "PENDING")
            add(f"    exact-head CI: {verdict}")
            if ci.get("failing"):
                add("    failing: " + ", ".join(ci["failing"]))
            if ci.get("pending"):
                add("    pending: " + ", ".join(ci["pending"]))
        else:
            add(f"    exact-head CI: unknown ({ci.get('reason', 'not checked')})")

    # ----------------------------------------------------------- local repo
    add(_section("CURRENT REMOTE BRANCHES"))
    repo_record = (packet.get("repositories") or {}).get(focus.get("repo")) or {}
    if repo_record.get("present"):
        add(_kv([
            ("checkout", repo_record.get("path")),
            ("branch", repo_record.get("branch")),
            ("head", repo_record.get("head_short")),
            ("subject", repo_record.get("head_subject")),
            ("dirty files", repo_record.get("dirty_count")),
        ]))
        branches = repo_record.get("remote_branches") or []
        add(f"  origin branches ({len(branches)}): " + ", ".join(branches[:40]))
    else:
        add(f"  {focus.get('repo')} is not checked out on this machine.")

    worktrees = packet.get("worktrees") or []
    if worktrees:
        add(_section("CURRENT WORKTREES"))
        for worktree in worktrees:
            add(f"  {worktree.get('path')}  [{worktree.get('branch')}]")
            add(f"    dirty={_yes(worktree.get('dirty'))}  cleanup_allowed={_yes(worktree.get('cleanup_allowed'))}  ({worktree.get('reason')})")

    # ---------------------------------------------------------------- fleet
    add(_section("CURRENT ACTIVE AGENTS"))
    agents = packet.get("agents") or []
    if not agents:
        add("  no agents registered. Register with: agentstart --agent-id <id>")
    for agent in agents:
        add(f"  {agent.get('agent_id')}  [{agent.get('environment')}]  status={agent.get('status')}"
            + ("  STALE" if agent.get("stale") else ""))
        add(_kv([
            ("repo", agent.get("repo")),
            ("lane", agent.get("active_lane")),
            ("last seen", agent.get("last_seen")),
            ("next action", agent.get("next_action")),
        ]))

    add(_section("CURRENT LANE OWNERSHIP"))
    lanes = packet.get("lanes") or []
    if not lanes:
        add("  no lanes claimed")
    for lane in lanes:
        add(f"  {lane.get('lane_id')} [{lane.get('repo')}] status={lane.get('status')} owner={lane.get('owner') or 'unowned'}")

    add(_section("RECENT EVENTS"))
    recent = packet.get("recent_events") or []
    if not recent:
        add("  event log is empty")
    for event in recent:
        add(f"  {event.get('timestamp')}  {event.get('event'):<24} {event.get('actor')}"
            + (f"  repo={event.get('repo')}" if event.get("repo") else "")
            + (f"  lane={event.get('lane')}" if event.get("lane") else ""))

    add(_section("RECENT COMPLETED WORK"))
    completed = packet.get("completed_work") or []
    if not completed:
        add("  nothing recorded as completed yet")
    for event in completed:
        add(f"  {event.get('timestamp')}  {event.get('event')}  {event.get('repo') or ''} {event.get('lane') or ''}")

    # ------------------------------------------------------------ blockers
    add(_section("CURRENT BLOCKERS"))
    blockers = packet.get("blockers") or []
    warnings = packet.get("warnings") or []
    if not blockers and not warnings:
        add("  none detected")
    for blocker in blockers:
        add(f"  BLOCKER: {blocker}")
    for warning in warnings:
        add(f"  WARNING: {warning}")

    add(_section("CURRENT NEXT ACTION"))
    add(f"  {packet.get('next_action')}")

    # ------------------------------------------------------- preservation
    preservation = packet.get("preservation", {})
    add(_section("PRESERVATION CONSTRAINTS"))
    add(f"  {preservation.get('rule')}")
    for branch, hold in sorted((preservation.get("holds") or {}).items()):
        marker = " (present on this repo's origin)" if branch in (preservation.get("present_locally") or []) else ""
        add(f"    {branch} = {hold}{marker}")

    # --------------------------------------------------------- discovery
    scanner = packet.get("projectscanner", {})
    add(_section("PROJECTSCANNER FINDINGS RELEVANT TO THE LANE"))
    if scanner.get("available"):
        add(_kv([
            ("root", scanner.get("root")),
            ("cli", scanner.get("cli")),
            ("repo graph available", _yes(scanner.get("repo_graph_available"))),
        ]))
        if scanner.get("packets_present"):
            add("  intelligence packets present: " + ", ".join(scanner["packets_present"]))
        if scanner.get("packets_missing"):
            add("  packets MISSING (evidence incomplete): " + ", ".join(scanner["packets_missing"]))
            add("  regenerate with: projectscanner scan <repo path>")
    else:
        add(f"  UNAVAILABLE: {scanner.get('reason')}")

    add(_section("EXISTING CAPABILITY SEARCH"))
    search = packet.get("capability_search")
    if not search:
        add("  no capability requested. Before building anything new, run:")
        add("    dreamcap check \"<capability>\" --repo <repo you would build it in>")
    else:
        verdict = search["verdict"]
        add(_kv([
            ("requested capability", search.get("capability")),
            ("canonical owner", verdict.get("canonical_owner") or "none recorded"),
            ("evidence complete", _yes(search.get("evidence_complete"))),
        ]))
        add("  implementations found:")
        for implementation in verdict.get("implementations") or []:
            add(f"    {implementation.get('repo')}: {implementation.get('kind')} ({implementation.get('evidence')})")
        if not verdict.get("implementations"):
            add("    none")
        add(f"  duplicate creation: {verdict.get('verdict')}")
        if verdict.get("directive"):
            add(f"  directive: {verdict['directive']}")

    tools_state = packet.get("agenttools", {})
    add(_section("AVAILABLE AGENTTOOLS"))
    if tools_state.get("available"):
        add(f"  root: {tools_state.get('root')}")
        for name, surface in sorted((tools_state.get("surfaces") or {}).items()):
            add(f"    {name}: module={surface['module']} importable={_yes(surface['importable'])} cli={surface['cli'] or '-'} on_path={_yes(surface['cli_on_path'])}")
        add("  Reuse these before writing a new helper.")
    else:
        add(f"  UNAVAILABLE: {tools_state.get('reason')}")

    add(_section("DUPLICATE-CREATION WARNING"))
    add("  Dream.OS rule: BEFORE CREATING SOMETHING NEW, PROVE THE CAPABILITY")
    add("  DOES NOT ALREADY EXIST.")
    add("    1. dreamcap check \"<capability>\"        (ProjectScanner + DreamVault evidence)")
    add("    2. If AgentTools provides it, depend on AgentTools -- do not copy it.")
    add("    3. If DreamVault owns it, extend it there -- do not fork governance.")
    add("    4. Only a clean NOT-FOUND result authorizes a new implementation.")

    # ------------------------------------------------------------ dreamosd
    brain = packet.get("dreamosd", {})
    add(_section("CONTROL PLANE (dreamosd / dreamos-brain)"))
    add(_kv([
        ("configured", _yes(brain.get("configured"))),
        ("endpoint", brain.get("endpoint")),
        ("reachable", _yes(brain.get("reachable"))),
        ("reason", brain.get("reason")),
    ]))
    store = brain.get("local_store") or {}
    add(_kv([
        ("local events", store.get("total_events")),
        ("pending sync", store.get("pending")),
    ]))

    # -------------------------------------------------------- how to reply
    add(_section("HOW TO HAND WORK BACK TO VICTOR"))
    add("  Report exactly one outcome: COMPLETE / BLOCKED / NEEDS_REVIEW /")
    add("  FAILED_VERIFICATION, using TARGET / ACTION / VERIFY / COMMIT.")
    add("  Any command Victor must run goes back as a paste-ready cliprun block")
    add("  (see HOW TO USE CLIPRUN above). Record what you did:")
    add("    dreamevent <event_type> --repo <repo> --lane <lane> [--status ...]")

    return "\n".join(out) + "\n"
