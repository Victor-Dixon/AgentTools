import json
from pathlib import Path

from dreamvault_closeout_bridge import (
    build_closeout_card_payload,
    closeouts_dir,
    dreamvault_root,
    latest_closeout_path,
    load_latest_closeout,
    load_portfolio_candidates,
    load_resume_bullets,
    load_skill_tree,
    portfolio_candidates_path,
    render_closeout_card_text,
    resume_bullets_path,
    skills_path,
    work_log_dir,
)


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def sample_closeout() -> dict:
    return {
        "schema": "dreamos.agent_closeout.v1",
        "task_id": "implement_closeout_task_feed_001",
        "title": "Implement closeout next-up task feed",
        "owner_agent": "ChatGPT",
        "repo": "DreamVault",
        "branch": "cursor/train-agent-in-environment-with-more-gpu-2c6d",
        "status": "closed",
        "actions_taken": [
            "Added candidate inbox.",
            "Added repo/title dedupe.",
            "Added master task promotion.",
        ],
        "files_touched": [
            {"path": "dreamvault_closeout.py", "action": "modified"},
            {"path": "tests/test_closeout_task_feed.py", "action": "created"},
        ],
        "verification": [
            {
                "command": "pytest -q tests/test_closeout_task_feed.py",
                "exit_code": 0,
                "result_summary": "37 passed in 0.88s",
                "evidence_path": "runtime/reports/implement_closeout_task_feed_001.md",
            }
        ],
        "evidence": [
            {
                "path": "runtime/reports/implement_closeout_task_feed_001.md",
                "type": "report",
                "summary": "Task feed passed.",
            }
        ],
        "risks": [],
        "next_up": [
            {
                "title": "Add Discord closeout-card payload tests",
                "repo": "discord_ops_manager",
                "reason": "Discord should display closeout evidence.",
                "priority": "P1",
            }
        ],
        "commit": {
            "commit_hash": "002053df",
            "commit_message": "feat: feed closeout next-up into task candidates",
            "pushed": True,
        },
        "final_status": {"closed": True, "reason": "Tests passed."},
        "score": {"score": 95, "accepted": True, "reasons": ["+25 passing verification"]},
    }


def test_paths_point_to_dreamvault(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DREAMVAULT_ROOT", str(tmp_path / "DreamVault"))

    assert dreamvault_root() == tmp_path / "DreamVault"
    assert closeouts_dir().as_posix().endswith("DreamVault/data/closeouts")
    assert latest_closeout_path().as_posix().endswith("DreamVault/data/closeouts/latest.json")
    assert work_log_dir().as_posix().endswith("DreamVault/data/work_log")
    assert skills_path().as_posix().endswith("DreamVault/data/skills/skill_tree.json")
    assert resume_bullets_path().as_posix().endswith("DreamVault/data/resume/resume_bullets.md")
    assert portfolio_candidates_path().as_posix().endswith("DreamVault/data/portfolio/publish_candidates.json")


def test_missing_latest_closeout_fails_softly(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DREAMVAULT_ROOT", str(tmp_path))

    loaded = load_latest_closeout()
    payload = build_closeout_card_payload()

    assert loaded["ok"] is False
    assert loaded["missing"] is True
    assert payload["ok"] is False
    assert payload["missing"] is True
    assert payload["title"] == "No closeout found"


def test_load_latest_closeout(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DREAMVAULT_ROOT", str(tmp_path))
    write_json(tmp_path / "data/closeouts/latest.json", sample_closeout())

    loaded = load_latest_closeout()

    assert loaded["ok"] is True
    assert loaded["data"]["task_id"] == "implement_closeout_task_feed_001"


def test_build_closeout_card_payload_from_latest(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DREAMVAULT_ROOT", str(tmp_path))
    write_json(tmp_path / "data/closeouts/latest.json", sample_closeout())

    payload = build_closeout_card_payload()

    assert payload["ok"] is True
    assert payload["task_id"] == "implement_closeout_task_feed_001"
    assert payload["repo"] == "DreamVault"
    assert payload["agent"] == "ChatGPT"
    assert payload["status"] == "closed"
    assert payload["score"] == 95
    assert payload["accepted"] is True
    assert payload["tests_summary"] == "37 passed in 0.88s"
    assert payload["commit_hash"] == "002053df"
    assert payload["pushed"] is True
    assert payload["evidence_count"] == 1
    assert payload["risk_count"] == 0
    assert payload["next_up"][0]["repo"] == "discord_ops_manager"
    assert payload["next_up"][0]["priority"] == "P1"


def test_render_closeout_card_text() -> None:
    payload = build_closeout_card_payload(sample_closeout())

    text = render_closeout_card_text(payload)

    assert "✅ CLOSEOUT: Implement closeout next-up task feed" in text
    assert "Repo: DreamVault" in text
    assert "Agent: ChatGPT" in text
    assert "Tests: 37 passed in 0.88s" in text
    assert "Commit: 002053df" in text
    assert "P1 discord_ops_manager: Add Discord closeout-card payload tests" in text


def test_projection_sources_fail_softly(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DREAMVAULT_ROOT", str(tmp_path))

    assert load_skill_tree()["ok"] is False
    assert load_resume_bullets()["ok"] is False
    assert load_portfolio_candidates()["ok"] is False


def test_projection_sources_load(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DREAMVAULT_ROOT", str(tmp_path))

    write_json(tmp_path / "data/skills/skill_tree.json", {"software_engineering": {}})
    (tmp_path / "data/resume").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data/resume/resume_bullets.md").write_text("- Built closeout spine\n", encoding="utf-8")
    write_json(tmp_path / "data/portfolio/publish_candidates.json", [{"title": "DreamVault"}])

    assert load_skill_tree()["data"] == {"software_engineering": {}}
    assert "Built closeout spine" in load_resume_bullets()["data"]
    assert load_portfolio_candidates()["data"][0]["title"] == "DreamVault"
