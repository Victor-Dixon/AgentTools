"""Acceptance tests for the Dream.OS control-plane client.

Numbered tests map to the V1 acceptance criteria in
``docs/DREAM_CONTROL_V1.md``.
"""

from __future__ import annotations

import json

import pytest

from dream_control import events as event_store
from dream_control import passdown as passdown_module
from dream_control import renderer
from dream_control import state as state_store
from dream_control.cli import main as cli_main
from dream_control.config import OperatorConfig, Paths
from dream_control.models import Agent, Event
from dream_control.policy import branch as branch_policy
from dream_control.policy import duplication as duplication_policy
from dream_control.policy.publish import publish_allowed
from dream_control.policy.worktree import worktree_disposition


@pytest.fixture()
def control_home(tmp_path, monkeypatch):
    home = tmp_path / "control"
    monkeypatch.setenv("DREAMOS_CONTROL_HOME", str(home))
    monkeypatch.delenv("DREAMOS_BRAIN_URL", raising=False)
    return Paths(home).ensure()


def _offline_packet(**kwargs):
    return passdown_module.assemble(include_vps=False, include_github=False, **kwargs)


def test_1_passdown_renders_from_a_cold_start(control_home):
    """TEST 1: passdown works from a fresh shell and produces a handoff."""
    packet = _offline_packet()
    text = renderer.render(packet)
    assert "DREAM.OS PASSDOWN" in text
    for section in (
        "CURRENT OPERATOR ENVIRONMENT", "HOW TO USE CLIPRUN", "HOW TO ACCESS VPS",
        "CURRENT RUNNER STATE", "CURRENT ACTIVE AGENTS", "CURRENT LANE OWNERSHIP",
        "RECENT EVENTS", "CURRENT BLOCKERS", "CURRENT NEXT ACTION",
        "PRESERVATION CONSTRAINTS", "EXISTING CAPABILITY SEARCH",
        "AVAILABLE AGENTTOOLS", "DUPLICATE-CREATION WARNING",
    ):
        assert section in text, f"missing passdown section: {section}"


def test_2_authority_is_read_live_not_replayed(control_home, monkeypatch):
    """TEST 2: a new master is reported; stale authority is never replayed."""
    from dream_control.collectors import github as github_collector

    heads = iter(["999ce26" * 5, "98b56ac" * 5])

    def fake_authority(repo, config=None):
        return {"repo": f"Victor-Dixon/{repo}", "available": True, "source": "gh",
                "default_branch": "master", "master_head": next(heads), "open_prs": []}

    monkeypatch.setattr(github_collector, "collect_authority", fake_authority)
    first = passdown_module.assemble(include_vps=False)
    second = passdown_module.assemble(include_vps=False)
    assert first["github"]["master_head"] != second["github"]["master_head"]
    assert "98b56ac" in renderer.render(second)


def test_2b_unavailable_authority_is_declared_not_assumed(control_home):
    packet = _offline_packet()
    text = renderer.render(packet)
    assert "do NOT assume the previous handoff's master still holds" in text


def test_3_a_fourth_agent_sees_what_three_others_did(control_home):
    """TEST 3: agents A (repo), B (VPS), C (scan) are visible to agent D."""
    for agent_id, environment in (
        ("aria_phone_001", "android_termux"),
        ("vps_agent_001", "dreamos_vps"),
        ("claude_cleanup_001", "claude"),
    ):
        state_store.upsert_agent(Agent(agent_id=agent_id, environment=environment), control_home)

    event_store.record(Event(event="pr_merged", actor="aria_phone_001",
                             environment="android_termux", repo="DreamVault",
                             lane="dreamvault_branch_cleanup",
                             authority={"pr": 73, "new_master": "98b56ac"}), p=control_home)
    event_store.record(Event(event="vps_process_started", actor="vps_agent_001",
                             environment="dreamos_vps", repo="dreamos-brain"), p=control_home)
    event_store.record(Event(event="project_scan_completed", actor="claude_cleanup_001",
                             environment="claude", status="success"), p=control_home)

    text = renderer.render(_offline_packet())
    for expected in ("aria_phone_001", "vps_agent_001", "claude_cleanup_001",
                     "pr_merged", "vps_process_started", "project_scan_completed"):
        assert expected in text


def test_4_existing_implementation_blocks_duplicate_creation(control_home):
    """TEST 4: an existing implementation yields DUPLICATE_IMPLEMENTATION_RISK."""
    verdict = duplication_policy.check_duplication(
        "branch_governance",
        evidence={
            "canonical_owner": "DreamVault",
            "implementations": [
                {"repo": "DreamVault", "kind": "current"},
                {"repo": "AgentTools", "kind": "partial"},
            ],
        },
        requesting_repo="Dream.os-Core",
    )
    assert verdict.verdict == duplication_policy.NOT_AUTHORIZED
    assert duplication_policy.RISK in verdict.warning
    assert "DreamVault" in verdict.warning


def test_4b_absent_capability_authorizes_creation(control_home):
    verdict = duplication_policy.check_duplication("a_capability_nobody_has", evidence={})
    assert verdict.verdict == duplication_policy.AUTHORIZED


def test_5_agenttools_capability_redirects_the_agent(control_home, monkeypatch):
    """TEST 5: an AgentTools-provided utility is surfaced as the thing to reuse."""
    from dream_control.integrations import agenttools as agenttools_integration

    monkeypatch.setattr(
        agenttools_integration, "provides",
        lambda capability, config=None: {"repo": "AgentTools", "capability": "mcp_servers",
                                         "module": "swarm_mcp.servers"},
    )
    report = passdown_module.capability_report("mcp_servers", requesting_repo="DreamVault")
    assert report["verdict"]["verdict"] == duplication_policy.NOT_AUTHORIZED
    assert any(i["repo"] == "AgentTools" for i in report["verdict"]["implementations"])


def test_6_unhealthy_vps_runner_surfaces_as_a_blocker(control_home, monkeypatch):
    """TEST 6: an offline runner or daemon must appear in the handoff."""
    from dream_control.collectors import vps as vps_collector

    monkeypatch.setattr(
        vps_collector, "collect",
        lambda config=None, timeout=20: {
            "host": "2.25.64.233", "user": "dreamos", "runner_name": "dreamvault-vps-01",
            "runner_dir": "/home/dreamos/runners/dreamvault", "runner_labels": [],
            "reachable": True, "healthy": False, "runner_alive": False,
            "runner_registered": True,
            "reason": "runner dreamvault-vps-01 process not running",
        },
    )
    packet = passdown_module.assemble(include_vps=True, include_github=False)
    assert any("VPS unhealthy" in blocker for blocker in packet["blockers"])
    assert "runner dreamvault-vps-01 process not running" in renderer.render(packet)


def test_7_hold_preserve_branches_are_never_auto_deleted(control_home):
    """TEST 7: HOLD_* branches are protected from automated cleanup."""
    for branch, hold in branch_policy.PRESERVATION_HOLDS.items():
        disposition = branch_policy.branch_disposition(branch)
        assert disposition["preserved"] is True
        assert disposition["cleanup_allowed"] is False
        assert disposition["hold"] == hold
        assert branch_policy.cleanup_allowed(branch) is False
    assert branch_policy.cleanup_allowed("chore/ordinary-stale-branch") is True


def test_7b_worktree_on_a_held_branch_is_protected(control_home):
    held = worktree_disposition({"path": "/tmp/wt", "branch": "polish/product-surface-001",
                                 "dirty": False})
    assert held["cleanup_allowed"] is False
    dirty = worktree_disposition({"path": "/tmp/wt2", "branch": "feature/x", "dirty": True})
    assert dirty["cleanup_allowed"] is False
    clean = worktree_disposition({"path": "/tmp/wt3", "branch": "feature/x", "dirty": False})
    assert clean["cleanup_allowed"] is True


def test_8_cpc_capture_records_internally_without_publishing(control_home, monkeypatch):
    """TEST 8: internal capture is automatic; Discord publishing is not."""
    monkeypatch.delenv("DREAMOS_PUBLISH_DISCORD", raising=False)
    from dream_control.integrations import cpc as cpc_integration

    event = cpc_integration.capture_event(
        actor="aria_phone_001", environment="android_termux",
        command="cliprun ~/task_001.sh", status="PASS", repo="DreamVault",
    )
    assert event.event == "cpc_capture_created"
    assert len(event_store.recent(10, p=control_home)) == 1

    plan = cpc_integration.publication_plan()
    assert plan["internal"]["control_plane_event"] is True
    assert plan["external"]["discord"]["allowed"] is False
    assert publish_allowed("discord").allowed is False


def test_8b_discord_publishing_requires_explicit_authorization(control_home, monkeypatch):
    monkeypatch.setenv("DREAMOS_PUBLISH_DISCORD", "1")
    assert publish_allowed("discord").allowed is True


def test_lane_ownership_prevents_two_agents_claiming_one_lane(control_home):
    state_store.claim_lane("dreamvault_branch_cleanup", "DreamVault", "aria_phone_001",
                           p=control_home)
    with pytest.raises(state_store.LaneConflict):
        state_store.claim_lane("dreamvault_branch_cleanup", "DreamVault", "windows_agent_001",
                               p=control_home)
    assert state_store.lane_owner("dreamvault_branch_cleanup", control_home) == "aria_phone_001"


def test_events_serialize_into_the_dreamosd_api_shape(control_home):
    event = Event(event="pr_merged", actor="aria_phone_001", environment="android_termux",
                  repo="DreamVault", lane="cleanup", authority={"pr": 73})
    payload = event.to_brain_payload()
    assert payload["event_type"] == "pr_merged"
    assert payload["repo"] == "DreamVault"
    assert payload["payload"]["authority"] == {"pr": 73}
    assert set(payload) == {"event_type", "source", "actor", "project", "task_id", "repo",
                            "status", "payload"}


def test_strict_mode_rejects_an_out_of_vocabulary_event(control_home):
    with pytest.raises(event_store.UnknownEventType):
        event_store.record(Event(event="not_a_real_event", actor="a", environment="linux"),
                           p=control_home, strict=True)


def test_selftest_exits_zero_without_network(control_home, capsys):
    assert cli_main(["passdown", "selftest", "--no-vps"]) == 0
    assert "PASSDOWN_SELFTEST=PASS" in capsys.readouterr().out


def test_cli_records_and_lists_events(control_home, capsys):
    assert cli_main(["event", "lane_claimed", "--repo", "DreamVault", "--lane", "x",
                     "--actor", "agent_a", "--strict"]) == 0
    capsys.readouterr()
    assert cli_main(["event", "--list"]) == 0
    listed = json.loads(capsys.readouterr().out)
    assert listed[0]["event"] == "lane_claimed"


def test_cap_check_exits_nonzero_when_duplication_is_not_authorized(control_home, monkeypatch):
    monkeypatch.setattr(passdown_module, "capability_report", lambda *a, **k: {
        "capability": "governance", "canonical_owner": "DreamVault",
        "evidence_complete": True,
        "verdict": {"verdict": "NOT_AUTHORIZED", "canonical_owner": "DreamVault",
                    "implementations": [{"repo": "DreamVault", "kind": "current"}],
                    "warning": "DUPLICATE_IMPLEMENTATION_RISK: governance exists",
                    "directive": "extend DreamVault"},
    })
    assert cli_main(["cap", "check", "governance", "--repo", "AgentTools"]) == 3


def test_operator_config_never_loses_the_canonical_vps(control_home):
    (control_home.operator_file).write_text(json.dumps({"operator": "Victor", "vps": {}}),
                                            encoding="utf-8")
    config = OperatorConfig.load(control_home)
    assert config.vps["host"] == "2.25.64.233"
    assert config.vps["runner_name"] == "dreamvault-vps-01"
