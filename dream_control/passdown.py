"""Assemble a continuation packet from every control-plane source.

Passdown is a *view*, not a database.  Nothing here is authoritative; every
section names where its facts came from and says so when a source is
unavailable, so a receiving agent never replays stale authority as fresh.
"""

from __future__ import annotations

from typing import Any

from . import events as event_store
from . import state as state_store
from .collectors import github as github_collector
from .collectors import local as local_collector
from .collectors import projectscanner as scanner_collector
from .collectors import vps as vps_collector
from .config import OperatorConfig, detect_environment, paths
from .integrations import agenttools as agenttools_integration
from .integrations import brain as brain_integration
from .integrations import cpc as cpc_integration
from .integrations import dreamvault as dreamvault_integration
from .models import SCHEMA, utc_now
from .policy import branch as branch_policy
from .policy import duplication as duplication_policy
from .policy import worktree as worktree_policy


def _authority_for(repo: str, config: OperatorConfig, *, with_ci: bool) -> dict[str, Any]:
    authority = github_collector.collect_authority(repo, config)
    if with_ci and authority.get("available"):
        for pull in authority.get("open_prs", []):
            pull["ci"] = github_collector.collect_exact_head_ci(repo, pull.get("head") or "", config)
    return authority


def assemble(
    *,
    repo: str | None = None,
    lane: str | None = None,
    capability: str | None = None,
    include_vps: bool = True,
    include_github: bool = True,
    include_ci: bool = True,
    config: OperatorConfig | None = None,
) -> dict[str, Any]:
    """Build the passdown packet. Safe to call offline."""
    config = config or OperatorConfig.load()
    p = paths().ensure()
    environment = detect_environment()
    primary_repo = repo or "DreamVault"

    packet: dict[str, Any] = {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "generated_by": {"environment": environment, "machine": local_collector.collect_machine()},
        "operator": {
            "operator": config.operator,
            "cliprun": cpc_integration.locate(config),
            "projects_root": config.projects_root,
            "notes": config.notes,
        },
        "focus": {"repo": primary_repo, "lane": lane, "capability": capability},
        "tools": local_collector.collect_tools(config),
        "repositories": local_collector.collect_repositories(config),
        "warnings": [],
        "blockers": [],
    }

    # --- durable intent (DreamVault) -------------------------------------
    packet["dreamvault"] = {
        "authority": dreamvault_integration.collect_authority(config),
        "planner": dreamvault_integration.collect_planner(config),
    }

    # --- live GitHub authority -------------------------------------------
    if include_github:
        packet["github"] = _authority_for(primary_repo, config, with_ci=include_ci)
        if not packet["github"].get("available"):
            packet["warnings"].append(
                f"GitHub authority unavailable for {primary_repo}: {packet['github'].get('reason')}"
            )
        elif packet["github"].get("stale_risk"):
            packet["warnings"].append(
                "GitHub authority came from a local fetched ref and may be stale; "
                "run `gh auth login` or `git fetch` before trusting master."
            )
    else:
        packet["github"] = {"available": False, "reason": "skipped by request"}

    # --- VPS runtime node --------------------------------------------------
    if include_vps:
        packet["vps"] = vps_collector.collect(config)
        packet["vps"]["ssh_hint"] = vps_collector.ssh_command_hint(config)
        if not packet["vps"].get("reachable"):
            packet["blockers"].append(f"VPS unreachable: {packet['vps'].get('reason')}")
        elif not packet["vps"].get("healthy"):
            packet["blockers"].append(f"VPS unhealthy: {packet['vps'].get('reason')}")
    else:
        packet["vps"] = {
            "host": config.vps.get("host"),
            "user": config.vps.get("user"),
            "runner_name": config.vps.get("runner_name"),
            "runner_dir": config.vps.get("runner_dir"),
            "runner_labels": config.vps.get("runner_labels", []),
            "reachable": False,
            "healthy": False,
            "reason": "not probed (--no-vps); state unknown, do not assume healthy",
            "ssh_hint": vps_collector.ssh_command_hint(config),
        }

    # --- dreamosd ----------------------------------------------------------
    packet["dreamosd"] = brain_integration.health(config)

    # --- worktrees ---------------------------------------------------------
    repo_record = packet["repositories"].get(primary_repo) or {}
    worktrees: list[dict[str, Any]] = []
    if repo_record.get("present"):
        from pathlib import Path

        worktrees = [
            worktree_policy.worktree_disposition(worktree)
            for worktree in local_collector.collect_worktrees(Path(repo_record["path"]))
        ]
    packet["worktrees"] = worktrees

    # --- fleet state -------------------------------------------------------
    agents = state_store.load_agents(p)
    lanes = state_store.load_lanes(p)
    packet["agents"] = [
        {**agent.to_dict(), "stale": agent.is_stale()} for agent in agents.values()
    ]
    packet["lanes"] = [lane_record.to_dict() for lane_record in lanes.values()]
    packet["recent_events"] = [event.to_dict() for event in event_store.recent(20, p=p)]
    packet["completed_work"] = [
        event.to_dict()
        for event in event_store.recent(
            10, p=p, event_types=["lane_completed", "pr_merged", "verification_passed"]
        )
    ]

    # --- preservation constraints ------------------------------------------
    holds = branch_policy.preserved_branches(p=p)
    packet["preservation"] = {
        "holds": holds,
        "rule": "No automated cleanup process may delete a branch under a HOLD_* disposition.",
        "present_locally": sorted(
            branch for branch in holds if branch in (repo_record.get("remote_branches") or [])
        ),
    }

    # --- discovery + capability --------------------------------------------
    packet["projectscanner"] = scanner_collector.collect(config)
    packet["agenttools"] = agenttools_integration.collect(config)

    if capability:
        packet["capability_search"] = capability_report(capability, config=config)
        verdict = packet["capability_search"]["verdict"]
        if verdict["verdict"] == duplication_policy.NOT_AUTHORIZED:
            packet["warnings"].append(verdict["warning"])
    else:
        packet["capability_search"] = None

    # --- lane ownership + next action --------------------------------------
    lane_record = lanes.get(lane) if lane else None
    packet["next_action"] = (
        (lane_record.next_action if lane_record and lane_record.next_action else None)
        or (packet["dreamvault"]["planner"].get("next_task") if packet["dreamvault"]["planner"].get("available") else None)
        or "No next action recorded. Claim a lane with: dreamlane claim <lane> --repo <repo>"
    )
    if lane and lane_record and lane_record.owner:
        packet["focus"]["lane_owner"] = lane_record.owner

    if not packet["projectscanner"].get("available"):
        packet["warnings"].append(
            "ProjectScanner evidence unavailable: capability search is INCOMPLETE. "
            "Do not treat 'no implementation found' as proof of absence."
        )
    return packet


def capability_report(capability: str, *, config: OperatorConfig | None = None,
                      requesting_repo: str | None = None) -> dict[str, Any]:
    """Combined discovery + governance answer for one capability."""
    config = config or OperatorConfig.load()
    scanner = scanner_collector.capability_search(capability, config)
    owner = dreamvault_integration.canonical_owner(capability, config)
    toolbelt = agenttools_integration.provides(capability, config)

    implementations = list(scanner.get("implementations", []))
    if toolbelt:
        implementations.append(
            {"repo": "AgentTools", "kind": "agenttools_surface", "evidence": toolbelt.get("module")}
        )
    if owner:
        implementations.append(
            {"repo": owner, "kind": "dreamvault_canonical_authority", "evidence": "canonical_authority_registry"}
        )

    verdict = duplication_policy.check_duplication(
        capability,
        evidence={"canonical_owner": owner, "implementations": implementations},
        requesting_repo=requesting_repo,
    )
    return {
        "capability": capability,
        "canonical_owner": owner,
        "projectscanner": scanner,
        "agenttools": toolbelt,
        "verdict": verdict.to_dict(),
        "evidence_complete": bool(scanner.get("complete")),
    }
