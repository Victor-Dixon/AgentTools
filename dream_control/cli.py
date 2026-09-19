"""Dream.OS control-plane CLI.

One entrypoint, dispatched either by subcommand or by the name the binary was
invoked as (``passdown``, ``dreamstate``, ``dreamevent``, ``agentstart``, ...).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from . import __version__, clipboard, renderer
from . import events as event_store
from . import passdown as passdown_module
from . import state as state_store
from .collectors import local as local_collector
from .collectors import projectscanner as scanner_collector
from .collectors import vps as vps_collector
from .config import OperatorConfig, default_agent_id, detect_environment, paths
from .integrations import agenttools as agenttools_integration
from .integrations import brain as brain_integration
from .integrations import cpc as cpc_integration
from .integrations import dreamvault as dreamvault_integration
from .models import EVENT_TYPES, Agent, Event
from .policy import branch as branch_policy

ALIASES = {
    "passdown": "passdown",
    "dreamstate": "state",
    "dreamevent": "event",
    "agentstart": "agent-start",
    "agentstatus": "agent-status",
    "dreamagents": "agents",
    "dreamscan": "scan",
    "dreamcap": "cap",
    "dreamlane": "lane",
}


def _emit(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        print(payload if isinstance(payload, str) else json.dumps(payload, indent=2, default=str))


# ------------------------------------------------------------------ passdown

def cmd_passdown(args: argparse.Namespace) -> int:
    if args.passdown_action == "selftest":
        return _selftest(args)
    if args.passdown_action == "show":
        p = paths()
        latest = p.handoff / "latest.md"
        if not latest.is_file():
            print("No handoff generated yet. Run: passdown", file=sys.stderr)
            return 1
        print(latest.read_text(encoding="utf-8"))
        return 0

    config = OperatorConfig.load()
    packet = passdown_module.assemble(
        repo=args.repo,
        lane=args.lane,
        capability=args.capability,
        include_vps=not args.no_vps,
        include_github=not args.no_github,
        include_ci=not args.no_ci,
        config=config,
    )
    if args.json:
        _emit(packet, True)
        return 0

    text = renderer.render(packet)
    p = paths().ensure()
    (p.handoff / "latest.md").write_text(text, encoding="utf-8")
    (p.handoff / "latest.json").write_text(
        json.dumps(packet, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8"
    )

    event_store.record(
        Event(
            event="passdown_generated",
            actor=default_agent_id(),
            environment=detect_environment(),
            repo=args.repo,
            lane=args.lane,
            status="ok",
            payload={
                "master_head": (packet.get("github") or {}).get("master_head"),
                "blockers": len(packet.get("blockers", [])),
                "warnings": len(packet.get("warnings", [])),
            },
        )
    )

    copied, how = clipboard.copy(text)
    if not args.quiet:
        print(text)
    print(f"\n[passdown] handoff written to {p.handoff / 'latest.md'}", file=sys.stderr)
    print(f"[passdown] clipboard: {'copied via ' + how if copied else how}", file=sys.stderr)
    return 0


def _selftest(args: argparse.Namespace) -> int:
    """Prove every source is either reachable or explicitly accounted for."""
    config = OperatorConfig.load()
    p = paths().ensure()
    checks: list[tuple[str, bool, str]] = []

    checks.append(("control home writable", os.access(p.home, os.W_OK), str(p.home)))
    tools = local_collector.collect_tools(config)
    checks.append(("git available", tools["git"], ""))
    checks.append(("clipboard", clipboard.copy("")[0], "optional"))

    dv = dreamvault_integration.collect_authority(config)
    checks.append(("DreamVault authority", bool(dv.get("available")), dv.get("reason", "")))
    scanner = scanner_collector.collect(config)
    checks.append(("ProjectScanner", bool(scanner.get("available")), scanner.get("reason", "")))
    at = agenttools_integration.collect(config)
    checks.append(("AgentTools", bool(at.get("available")), at.get("reason", "")))
    cpc_state = cpc_integration.locate(config)
    checks.append(("cliprun / CPC", bool(cpc_state.get("cliprun_present")), cpc_state.get("cliprun", "")))

    if not args.no_vps:
        vps = vps_collector.collect(config)
        checks.append(("VPS reachable", bool(vps.get("reachable")), vps.get("reason", "")))
        checks.append(("VPS runner healthy", bool(vps.get("healthy")), vps.get("reason", "")))

    brain = brain_integration.health(config)
    checks.append(("dreamosd endpoint", bool(brain.get("reachable")), brain.get("reason", "")))

    packet = passdown_module.assemble(
        repo=args.repo, include_vps=False, include_github=False, config=config
    )
    checks.append(("passdown assembles", bool(packet.get("schema")), ""))
    checks.append(("renderer produces output", len(renderer.render(packet)) > 500, ""))

    required = {"control home writable", "git available", "passdown assembles", "renderer produces output"}
    failed_required = [name for name, ok, _ in checks if name in required and not ok]

    for name, ok, detail in checks:
        mark = "PASS" if ok else ("FAIL" if name in required else "WARN")
        print(f"[{mark}] {name}" + (f" -- {detail}" if detail and not ok else ""))
    print(f"\nPASSDOWN_SELFTEST={'PASS' if not failed_required else 'FAIL'}")
    return 1 if failed_required else 0


# --------------------------------------------------------------------- state

def cmd_state(args: argparse.Namespace) -> int:
    p = paths().ensure()
    payload = {
        "home": str(p.home),
        "agents": {k: v.to_dict() for k, v in state_store.load_agents(p).items()},
        "lanes": {k: v.to_dict() for k, v in state_store.load_lanes(p).items()},
        "capabilities": {k: v.to_dict() for k, v in state_store.load_capabilities(p).items()},
        "repositories": local_collector.collect_repositories(),
        "events": event_store.sync_state(p=p),
    }
    if args.section:
        payload = {args.section: payload.get(args.section)}
    _emit(payload, True)
    return 0


# -------------------------------------------------------------------- events

def cmd_event(args: argparse.Namespace) -> int:
    if args.list:
        found = event_store.recent(args.limit, repo=args.repo, lane=args.lane, actor=args.actor)
        _emit([event.to_dict() for event in found], True)
        return 0
    if args.sync:
        _emit(brain_integration.push_events(dry_run=args.dry_run), True)
        return 0
    if not args.event_type:
        print("error: an event type is required (or use --list/--sync)", file=sys.stderr)
        return 2

    event = Event(
        event=args.event_type,
        actor=args.actor or default_agent_id(),
        environment=detect_environment(),
        repo=args.repo,
        lane=args.lane,
        task_id=args.task_id,
        status=args.status,
        payload=json.loads(args.payload) if args.payload else {},
        authority=json.loads(args.authority) if args.authority else {},
        verification=json.loads(args.verification) if args.verification else {},
    )
    try:
        event_store.record(event, strict=args.strict)
    except event_store.UnknownEventType as exc:
        print(f"error: {exc}\nknown types: {', '.join(EVENT_TYPES)}", file=sys.stderr)
        return 2
    _emit(event.to_dict(), True)
    return 0


# -------------------------------------------------------------------- agents

def cmd_agent_start(args: argparse.Namespace) -> int:
    environment = args.environment or detect_environment()
    agent = Agent(
        agent_id=args.agent_id or default_agent_id(environment),
        environment=environment,
        provider=args.provider,
        repo=args.repo,
        active_lane=args.lane,
        task_id=args.task_id,
        status="active",
        capabilities=args.capability or [],
        tool_access=local_collector.collect_tools(),
        next_action=args.next_action,
    )
    agent = state_store.upsert_agent(agent)
    event_store.record(
        Event(
            event="agent_registered",
            actor=agent.agent_id,
            environment=agent.environment,
            repo=agent.repo,
            lane=agent.active_lane,
            status="active",
            payload={"provider": agent.provider, "tool_access": agent.tool_access},
        )
    )
    _emit(agent.to_dict(), True)
    return 0


def cmd_agent_status(args: argparse.Namespace) -> int:
    agent_id = args.agent_id or default_agent_id()
    agents = state_store.load_agents()
    agent = agents.get(agent_id)
    if agent is None:
        print(f"agent not registered: {agent_id}", file=sys.stderr)
        return 1
    if args.set_status or args.lane or args.next_action:
        agent.status = args.set_status or agent.status
        agent.active_lane = args.lane or agent.active_lane
        agent.next_action = args.next_action or agent.next_action
        agent = state_store.upsert_agent(agent)
        event_store.record(
            Event(
                event="agent_heartbeat",
                actor=agent.agent_id,
                environment=agent.environment,
                repo=agent.repo,
                lane=agent.active_lane,
                status=agent.status,
            )
        )
    _emit({**agent.to_dict(), "stale": agent.is_stale()}, True)
    return 0


def cmd_agents(args: argparse.Namespace) -> int:
    agents = state_store.load_agents()
    rows = [{**agent.to_dict(), "stale": agent.is_stale()} for agent in agents.values()]
    if args.json:
        _emit(rows, True)
        return 0
    if not rows:
        print("no agents registered")
        return 0
    for row in sorted(rows, key=lambda r: r["agent_id"]):
        flag = " STALE" if row["stale"] else ""
        print(f"{row['agent_id']:<26} {row['environment']:<16} {row['status']:<12} "
              f"lane={row.get('active_lane') or '-'}{flag}")
    return 0


# --------------------------------------------------------------------- lanes

def cmd_lane(args: argparse.Namespace) -> int:
    actor = args.actor or default_agent_id()
    if args.lane_action == "list":
        _emit({k: v.to_dict() for k, v in state_store.load_lanes().items()}, True)
        return 0
    if args.lane_action == "claim":
        try:
            lane = state_store.claim_lane(
                args.lane_id, args.repo or "DreamVault", actor, task_id=args.task_id, force=args.force
            )
        except state_store.LaneConflict as exc:
            print(f"LANE_CONFLICT: {exc}", file=sys.stderr)
            return 1
        event_store.record(
            Event(event="lane_claimed", actor=actor, environment=detect_environment(),
                  repo=lane.repo, lane=lane.lane_id, task_id=lane.task_id)
        )
        _emit(lane.to_dict(), True)
        return 0

    completed = args.lane_action == "complete"
    lane = state_store.release_lane(args.lane_id, completed=completed)
    if lane is None:
        print(f"unknown lane: {args.lane_id}", file=sys.stderr)
        return 1
    event_store.record(
        Event(event="lane_completed" if completed else "lane_released", actor=actor,
              environment=detect_environment(), repo=lane.repo, lane=lane.lane_id)
    )
    _emit(lane.to_dict(), True)
    return 0


# ------------------------------------------------------- discovery/capability

def cmd_scan(args: argparse.Namespace) -> int:
    """Delegate to ProjectScanner; never reimplement scanning here."""
    config = OperatorConfig.load()
    state = scanner_collector.available(config)
    if not state.get("available"):
        print(f"ProjectScanner unavailable: {state.get('reason')}", file=sys.stderr)
        return 1
    if args.status:
        _emit(scanner_collector.collect(config), True)
        return 0

    from .collectors._run import run

    target = args.path or str(Path.cwd())
    code, out, err = run(
        ["python3", "-m", "projectscanner", "scan", target],
        cwd=Path(state["root"]),
        timeout=args.timeout,
    )
    print(out or err)
    if code == 0:
        event_store.record(
            Event(event="project_scan_completed", actor=default_agent_id(),
                  environment=detect_environment(), status="success",
                  payload={"target": target, "runner": "projectscanner"})
        )
    return code


def cmd_cap(args: argparse.Namespace) -> int:
    config = OperatorConfig.load()
    if args.cap_action == "list":
        _emit({k: v.to_dict() for k, v in state_store.load_capabilities().items()}, True)
        return 0

    report = passdown_module.capability_report(
        args.capability, config=config, requesting_repo=args.repo
    )
    verdict = report["verdict"]
    if verdict["verdict"] != "AUTHORIZED":
        event_store.record(
            Event(event="duplicate_detected", actor=default_agent_id(),
                  environment=detect_environment(), repo=args.repo,
                  status=verdict["verdict"],
                  payload={"capability": args.capability,
                           "implementations": verdict["implementations"]})
        )
    if args.json:
        _emit(report, True)
        return 0

    print(f"CAPABILITY SEARCH\n\n  requested capability:\n    {args.capability}\n")
    print("  findings:")
    for implementation in verdict["implementations"] or []:
        print(f"    {implementation.get('repo')}: {implementation.get('kind')}")
    if not verdict["implementations"]:
        print("    none")
    print(f"\n  canonical owner:\n    {verdict['canonical_owner'] or 'none recorded'}")
    print(f"\n  duplicate creation:\n    {verdict['verdict']}")
    if verdict.get("warning"):
        print(f"\n  {verdict['warning']}")
    if verdict.get("directive"):
        print(f"  {verdict['directive']}")
    if not report["evidence_complete"]:
        print("\n  NOTE: ProjectScanner evidence incomplete; absence is NOT proven.")
    return 0 if verdict["verdict"] == "AUTHORIZED" else 3


def cmd_policy(args: argparse.Namespace) -> int:
    if args.policy_action == "branch":
        _emit(branch_policy.branch_disposition(args.name), True)
        return 0 if branch_policy.cleanup_allowed(args.name) else 3
    if args.policy_action == "publish":
        from .policy.publish import publish_allowed

        decision = publish_allowed(args.name)
        _emit(decision.to_dict(), True)
        return 0 if decision.allowed else 3
    _emit(cpc_integration.publication_plan(), True)
    return 0


# ------------------------------------------------------------------- parser

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dreamctl", description="Dream.OS control-plane client")
    parser.add_argument("--version", action="version", version=f"dream_control {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    pd = sub.add_parser("passdown", help="generate a continuation packet")
    pd.add_argument("passdown_action", nargs="?", choices=["show", "selftest"])
    pd.add_argument("--repo", default="DreamVault")
    pd.add_argument("--lane")
    pd.add_argument("--capability")
    pd.add_argument("--json", action="store_true")
    pd.add_argument("--quiet", action="store_true", help="write and copy without printing")
    pd.add_argument("--no-vps", action="store_true")
    pd.add_argument("--no-github", action="store_true")
    pd.add_argument("--no-ci", action="store_true")
    pd.set_defaults(func=cmd_passdown)

    st = sub.add_parser("state", help="dump control-plane state")
    st.add_argument("section", nargs="?",
                    choices=["agents", "lanes", "capabilities", "repositories", "events"])
    st.set_defaults(func=cmd_state)

    ev = sub.add_parser("event", help="record or read events")
    ev.add_argument("event_type", nargs="?")
    ev.add_argument("--repo")
    ev.add_argument("--lane")
    ev.add_argument("--task-id")
    ev.add_argument("--status")
    ev.add_argument("--actor")
    ev.add_argument("--payload", help="JSON object")
    ev.add_argument("--authority", help="JSON object")
    ev.add_argument("--verification", help="JSON object")
    ev.add_argument("--strict", action="store_true", help="reject unknown event types")
    ev.add_argument("--list", action="store_true")
    ev.add_argument("--limit", type=int, default=25)
    ev.add_argument("--sync", action="store_true", help="push events to dreamosd")
    ev.add_argument("--dry-run", action="store_true")
    ev.set_defaults(func=cmd_event)

    ag = sub.add_parser("agent-start", help="register this agent")
    ag.add_argument("--agent-id")
    ag.add_argument("--environment")
    ag.add_argument("--provider", default="unknown")
    ag.add_argument("--repo")
    ag.add_argument("--lane")
    ag.add_argument("--task-id")
    ag.add_argument("--capability", action="append")
    ag.add_argument("--next-action")
    ag.set_defaults(func=cmd_agent_start)

    ast_ = sub.add_parser("agent-status", help="read or update one agent")
    ast_.add_argument("--agent-id")
    ast_.add_argument("--set-status", choices=["idle", "active", "blocked", "waiting_ci", "stopped"])
    ast_.add_argument("--lane")
    ast_.add_argument("--next-action")
    ast_.set_defaults(func=cmd_agent_status)

    ags = sub.add_parser("agents", help="list the fleet")
    ags.add_argument("--json", action="store_true")
    ags.set_defaults(func=cmd_agents)

    ln = sub.add_parser("lane", help="lane ownership")
    ln.add_argument("lane_action", choices=["claim", "release", "complete", "list"])
    ln.add_argument("lane_id", nargs="?")
    ln.add_argument("--repo")
    ln.add_argument("--task-id")
    ln.add_argument("--actor")
    ln.add_argument("--force", action="store_true")
    ln.set_defaults(func=cmd_lane)

    sc = sub.add_parser("scan", help="run ProjectScanner (delegated)")
    sc.add_argument("path", nargs="?")
    sc.add_argument("--status", action="store_true")
    sc.add_argument("--timeout", type=int, default=900)
    sc.set_defaults(func=cmd_scan)

    cp = sub.add_parser("cap", help="capability search / duplication gate")
    cp.add_argument("cap_action", choices=["check", "list"])
    cp.add_argument("capability", nargs="?")
    cp.add_argument("--repo", help="repo you would implement it in")
    cp.add_argument("--json", action="store_true")
    cp.set_defaults(func=cmd_cap)

    po = sub.add_parser("policy", help="inspect policy decisions")
    po.add_argument("policy_action", choices=["branch", "publish", "plan"])
    po.add_argument("name", nargs="?", default="")
    po.set_defaults(func=cmd_policy)

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    invoked = Path(sys.argv[0]).name
    if invoked in ALIASES:
        argv = [ALIASES[invoked], *argv]
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "lane" and args.lane_action != "list" and not args.lane_id:
        parser.error("lane_id is required for claim/release/complete")
    if args.command == "cap" and args.cap_action == "check" and not args.capability:
        parser.error("a capability name is required for `cap check`")

    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
