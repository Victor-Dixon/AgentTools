from __future__ import annotations

from tools.messaging_ssot_bridge import (
    build_hard_onboard_cmd,
    build_soft_onboard_cmd,
    dreamvault_send_cli,
)


def test_hard_onboard_prefers_dreamvault_ssot():
    send = dreamvault_send_cli()
    if not send.is_file():
        return
    cmd = build_hard_onboard_cmd("Agent-1", "reset workspace")
    assert cmd[0] == "python"
    assert str(send) in cmd
    assert "--category" in cmd and "s2a" in cmd
    assert "--s2a-variant" in cmd and "onboarding" in cmd
    assert "--live" in cmd
    assert "Agent-1" in cmd
    assert "reset workspace" in cmd


def test_soft_onboard_prefers_dreamvault_ssot():
    send = dreamvault_send_cli()
    if not send.is_file():
        return
    cmd = build_soft_onboard_cmd("Agent-4", "session cleanup")
    assert str(send) in cmd
    assert "--category" in cmd
    assert "session cleanup" in cmd
