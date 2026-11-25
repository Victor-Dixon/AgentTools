import json
import os

from mcp_servers import cicd_helper_server as ci


def test_metadata_projection(monkeypatch):
    row = {"id": 123, "name": "dreamos-metadata-fixture", "size_in_bytes": 42,
           "expired": False, "created_at": "2026-01-01T00:00:00Z",
           "expires_at": "2026-01-02T00:00:00Z", "archive_download_url": "not-returned"}
    def command(cmd, cwd):
        assert cmd == ["gh", "api", "repos/:owner/:repo/actions/runs/456/artifacts", "--jq", ".artifacts"]
        return {"success": True, "stdout": json.dumps([row])}
    monkeypatch.setattr(ci, "_run_command", command)
    result = ci.get_workflow_artifacts(456)
    assert result == {"success": True, "run_id": 456, "count": 1,
                      "artifacts": [{"id": 123, "name": row["name"], "size_bytes": 42,
                                     "expired": False, "created_at": row["created_at"],
                                     "expires_at": row["expires_at"]}]}


def test_live_fixture():
    import pytest
    run_id = os.environ.get("ARTIFACT_ACCEPTANCE_RUN_ID")
    if not run_id:
        pytest.skip("Live fixture only in artifact acceptance workflow")
    result = ci.get_workflow_artifacts(int(run_id))
    assert result["success"], result
    matches = [a for a in result["artifacts"] if a["name"] == "dreamos-metadata-fixture"]
    assert len(matches) == 1
    item = matches[0]
    assert type(item["id"]) is int and item["id"] > 0
    assert item["size_bytes"] > 0 and item["expired"] is False
    assert item["created_at"] and item["expires_at"]
    assert set(item) == {"id", "name", "size_bytes", "expired", "created_at", "expires_at"}
    print(json.dumps(item, sort_keys=True))
