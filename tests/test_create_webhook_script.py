from pathlib import Path


def test_create_webhook_script_does_not_hardcode_secrets():
    text = Path("tools/discord/create_webhook.py").read_text()

    assert "DISCORD_BOT_TOKEN" in text
    assert "DISCORD_TRADING_CHANNEL_ID" in text
    assert "secrets.env" in text
    assert "discord.com/api/webhooks" not in text
