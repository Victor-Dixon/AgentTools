from tools.discord.webhook_sender import send_payload


def test_discord_webhook_sender_missing_env_is_safe(monkeypatch):
    monkeypatch.delenv("DISCORD_TRADING_WEBHOOK_URL", raising=False)
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)

    result = send_payload({"content": "test"})

    assert result.ok is False
    assert result.status_code is None
    assert "missing" in result.message.lower()
