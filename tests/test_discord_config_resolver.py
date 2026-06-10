from pathlib import Path

from tools.discord.config import resolve_discord_config


def test_resolves_freeride_token_alias_from_file(tmp_path, monkeypatch):
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    monkeypatch.delenv("FREERIDEINVESTOR_DISCORD_BOT_TOKEN", raising=False)

    secrets = tmp_path / "secrets.env"
    secrets.write_text(
        'export FREERIDEINVESTOR_DISCORD_BOT_TOKEN="abc123"\n'
        'export DISCORD_TARGET_GUILD_ID="guild123"\n',
        encoding="utf-8",
    )

    config = resolve_discord_config(secrets)

    assert config["token_present"] is True
    assert config["token_env_name"] == "FREERIDEINVESTOR_DISCORD_BOT_TOKEN"
    assert config["bot_token"] == "abc123"
    assert config["guild_id"] == "guild123"


def test_defaults_freeride_guild_when_missing(tmp_path, monkeypatch):
    monkeypatch.delenv("DISCORD_GUILD_ID", raising=False)
    monkeypatch.delenv("DISCORD_TARGET_GUILD_ID", raising=False)

    secrets = tmp_path / "secrets.env"
    secrets.write_text('export DISCORD_BOT_TOKEN="abc123"\n', encoding="utf-8")

    config = resolve_discord_config(secrets)

    assert config["guild_id"] == "1375298054357254257"
