"""Deploy package contract tests for VPS Swarm Commander."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DEPLOY = ROOT / "deploy" / "vps" / "swarm-commander"


class TestVpsDeployPackage:
    def test_deploy_files_exist(self):
        required = [
            DEPLOY / "README.md",
            DEPLOY / ".env.example",
            DEPLOY / "requirements-headless.txt",
            DEPLOY / "systemd" / "swarm-commander.service",
            DEPLOY / "scripts" / "install.sh",
            DEPLOY / "scripts" / "healthcheck.sh",
            DEPLOY / "scripts" / "start.sh",
            DEPLOY / "scripts" / "stop.sh",
        ]
        missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
        assert not missing, f"missing deploy files: {missing}"

    def test_env_example_placeholders_only(self):
        lines = (DEPLOY / ".env.example").read_text(encoding="utf-8").splitlines()
        keys = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            assert "=" in line
            key, _, value = line.partition("=")
            keys.append(key)
            assert value == "", f"{key} must have empty placeholder value"
        assert "DISCORD_BOT_TOKEN" in keys
        assert "DISCORD_WEBHOOK_AGENT_8" in keys

    def test_systemd_uses_external_env(self):
        unit = (DEPLOY / "systemd" / "swarm-commander.service").read_text(encoding="utf-8")
        assert "EnvironmentFile=-/opt/dreamos/secrets/swarm-commander.env" in unit
        assert "journal" in unit
        assert "Restart=on-failure" in unit
        assert "pyautogui" not in unit.lower()

    def test_no_pyautogui_in_headless_requirements(self):
        req = (DEPLOY / "requirements-headless.txt").read_text(encoding="utf-8").lower()
        assert "pyautogui" not in req

    def test_healthcheck_no_live_discord(self):
        script = (DEPLOY / "scripts" / "healthcheck.sh").read_text(encoding="utf-8")
        assert "importlib.import_module" in script
        assert "bot.start" not in script

    def test_install_skips_start_without_secrets(self):
        script = (DEPLOY / "scripts" / "install.sh").read_text(encoding="utf-8")
        assert "SECRETS=missing" in script
        assert "bot not started" in script


class TestHeadlessImportSmoke:
    def test_discord_commander_imports_without_pyautogui(self):
        import sys

        src = ROOT / "src"
        if str(src) not in sys.path:
            sys.path.insert(0, str(src))
        import agent_tools.discord_commander.agent_message_sender as ams
        import agent_tools.discord_commander.unified_discord_bot as bot

        assert ams.normalize_agent_id("3") == "Agent-3"
        assert "!message" in bot.PREFIX_COMMANDS

    def test_queue_bridge_optional(self):
        import sys

        src = ROOT / "src"
        if str(src) not in sys.path:
            sys.path.insert(0, str(src))
        from agent_tools.discord_commander.queue_bridge import deliver_message

        assert deliver_message("hi", "Agent-1", None) is False
