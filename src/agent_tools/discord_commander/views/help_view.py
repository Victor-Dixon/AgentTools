"""Restored interactive help view — toolbelt-adapted from V2."""

from __future__ import annotations

import discord

VIEW_TIMEOUT = 300

HELP_PAGES = {
    "main": (
        "Discord Commander Help",
        "Restored V2 views + slash commands wired to DreamVault toolbelt.\n"
        "Use buttons below to browse sections.",
    ),
    "messaging": (
        "Messaging",
        "• `/send` — message one agent\n"
        "• `/swarm` or `/broadcast` — broadcast to Agent-1..8\n"
        "• `!message Agent-N <text>` — prefix send\n"
        "• `!broadcast <text>` — prefix broadcast\n"
        "• `/gui` — control panel (select, broadcast, quad status)",
    ),
    "onboard": (
        "Onboard (local PyAutoGUI)",
        "• `/onboard status` — quad gas readiness\n"
        "• `/onboard soft Agent-N` — soft onboard\n"
        "• `/onboard hard Agent-N` — hard onboard (closeout → new chat)\n"
        "• `/onboard quad` — group onboard when 4/4 ready\n"
        "• Prefix: `!onboard status|soft|hard|quad [force]`",
    ),
    "swarm": (
        "Swarm",
        "• `/agents` — list agents\n"
        "• `/agent-status` — detailed status for one agent\n"
        "• `/swarm-status` — embed from status.json\n"
        "• `/fleet-audit` — masked bot roster audit\n"
        "• `/prompts list|show|render|next|search|source|send|parity` — governed prompt tools",
    ),
    "commands": (
        "All Slash Commands",
        "Tier 1 restored: `/send` `/swarm` `/broadcast` `/agents` `/agent-status` `/commands` "
        "`/swarm-help` `/info` `/gui` `/onboard`\n"
        "Tier 2 existing: `/ping` `/status` `/help` `/swarm-status` `/fleet-audit` `/prompts`",
    ),
}


class HelpGUIView(discord.ui.View):
  def __init__(self) -> None:
    super().__init__(timeout=VIEW_TIMEOUT)
    for label, page, row in (
        ("Messaging", "messaging", 0),
        ("Onboard", "onboard", 0),
        ("Swarm", "swarm", 0),
        ("Commands", "commands", 1),
        ("Main", "main", 1),
    ):
      btn = discord.ui.Button(label=label, style=discord.ButtonStyle.primary, row=row)
      btn.callback = self._make_callback(page)
      self.add_item(btn)

  def _make_callback(self, page: str):
    async def handler(interaction: discord.Interaction) -> None:
      title, body = HELP_PAGES[page]
      embed = discord.Embed(title=title, description=body, color=0x0099FF)
      await interaction.response.edit_message(embed=embed, view=self)

    return handler

  @staticmethod
  def main_embed() -> discord.Embed:
    title, body = HELP_PAGES["main"]
    return discord.Embed(title=title, description=body, color=0x0099FF)
