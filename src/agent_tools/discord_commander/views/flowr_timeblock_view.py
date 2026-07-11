"""Persistent Flowr timeblock panels for #timeblock-victor and #timeblock-aria."""

from __future__ import annotations

import os
from typing import Any

import discord

FLOWR_POMODORO_URL = "https://victor-dixon.github.io/Flowr/flowr/"
FLOWR_MAIN_URL = "https://victor-dixon.github.io/Flowr/"

OWNER_META: dict[str, dict[str, str]] = {
    "victor": {"display_name": "Victor", "flowr_url": FLOWR_POMODORO_URL},
    "aria": {"display_name": "Aria", "flowr_url": FLOWR_POMODORO_URL},
}


def _dreamvault_store() -> dict[str, Any]:
    from agent_tools.discord_commander.dreamvault_discord_loader import load_flowr_store

    return load_flowr_store()


def _persistent_timeout() -> float | None:
    if os.environ.get("DISCORD_PERSISTENT_VIEWS", "").strip().lower() in {"1", "true", "yes"}:
        return None
    return 300


class AddTimeblockModal(discord.ui.Modal):
    def __init__(self, owner: str, prefix: str) -> None:
        meta = OWNER_META[owner]
        super().__init__(title=f"Add timeblock — {meta['display_name']}")
        self.owner = owner
        self.prefix = prefix
        self.title_field = discord.ui.TextInput(
            label="Block title",
            placeholder="Deep work, admin, trading review…",
            max_length=80,
            required=True,
        )
        self.minutes_field = discord.ui.TextInput(
            label="Minutes",
            placeholder="25",
            default="25",
            max_length=4,
            required=True,
        )
        self.add_item(self.title_field)
        self.add_item(self.minutes_field)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        store = _dreamvault_store()
        try:
            minutes = int(str(self.minutes_field.value or "25").strip())
        except ValueError:
            minutes = 25
        block = store["add_block"](
            self.owner,
            title=str(self.title_field.value or "Focus Block"),
            minutes=minutes,
        )
        await interaction.response.send_message(
            f"Added **{block['title']}** ({block['minutes']}m) — `{block['status']}`",
            ephemeral=True,
        )


def _build_flowr_timeblock_view(owner: str) -> type:
    prefix = f"flowr_{owner}"
    meta = OWNER_META[owner]

    class FlowrTimeblockView(discord.ui.View):
        """Always-on Flowr + planner timeblock panel."""

        def __init__(self) -> None:
            super().__init__(timeout=_persistent_timeout())
            self.add_item(
                discord.ui.Button(
                    label="Open Flowr",
                    style=discord.ButtonStyle.link,
                    url=meta["flowr_url"],
                    row=0,
                )
            )
            self.add_item(
                discord.ui.Button(
                    label="Flowr Timer",
                    style=discord.ButtonStyle.link,
                    url=FLOWR_MAIN_URL,
                    row=0,
                )
            )

        @discord.ui.button(
            label="Today's Blocks",
            custom_id=f"{prefix}_blocks",
            style=discord.ButtonStyle.primary,
            row=1,
        )
        async def todays_blocks(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            store = _dreamvault_store()
            state = store["load_state"](owner)
            text = store["format_blocks_summary"](state)
            await interaction.response.send_message(text, ephemeral=True)

        @discord.ui.button(
            label="Start Focus 25m",
            custom_id=f"{prefix}_start_focus",
            style=discord.ButtonStyle.success,
            row=1,
        )
        async def start_focus(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            store = _dreamvault_store()
            timer = store["start_focus_timer"](owner, minutes=25)
            await interaction.response.send_message(
                f"Focus timer started — `{timer['minutes']}m`",
                ephemeral=True,
            )

        @discord.ui.button(
            label="Pause",
            custom_id=f"{prefix}_pause",
            style=discord.ButtonStyle.secondary,
            row=1,
        )
        async def pause(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            store = _dreamvault_store()
            store["pause_timer"](owner)
            await interaction.response.send_message("Timer paused.", ephemeral=True)

        @discord.ui.button(
            label="Reset",
            custom_id=f"{prefix}_reset",
            style=discord.ButtonStyle.secondary,
            row=1,
        )
        async def reset(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            store = _dreamvault_store()
            timer = store["reset_timer"](owner)
            await interaction.response.send_message(
                f"Timer reset — `{timer['minutes']}m` ready.",
                ephemeral=True,
            )

        @discord.ui.button(
            label="Add Block",
            custom_id=f"{prefix}_add_block",
            style=discord.ButtonStyle.primary,
            row=2,
        )
        async def add_block_btn(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.send_modal(AddTimeblockModal(owner, prefix))

        @discord.ui.button(
            label="Complete Active",
            custom_id=f"{prefix}_complete",
            style=discord.ButtonStyle.success,
            row=2,
        )
        async def complete_active(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            store = _dreamvault_store()
            block = store["complete_active_block"](owner)
            if block is None:
                await interaction.response.send_message("No active block to complete.", ephemeral=True)
                return
            await interaction.response.send_message(
                f"Completed **{block.get('title', 'block')}**.",
                ephemeral=True,
            )

        @discord.ui.button(
            label="Planner Sync",
            custom_id=f"{prefix}_planner",
            style=discord.ButtonStyle.secondary,
            row=2,
        )
        async def planner_sync(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            store = _dreamvault_store()
            await interaction.response.send_message(store["planner_focus_lines"](), ephemeral=True)

        @discord.ui.button(
            label="Clear Blocks",
            custom_id=f"{prefix}_clear",
            style=discord.ButtonStyle.danger,
            row=2,
        )
        async def clear(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            store = _dreamvault_store()
            count = store["clear_blocks"](owner)
            await interaction.response.send_message(f"Cleared {count} block(s).", ephemeral=True)

        @discord.ui.button(
            label="Panel Status",
            custom_id=f"{prefix}_status",
            style=discord.ButtonStyle.secondary,
            row=3,
        )
        async def panel_status(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            store = _dreamvault_store()
            await interaction.response.send_message(store["build_panel_summary"](owner), ephemeral=True)

    FlowrTimeblockView.__name__ = f"FlowrTimeblock{owner.title()}View"
    return FlowrTimeblockView


FlowrTimeblockVictorView = _build_flowr_timeblock_view("victor")
FlowrTimeblockAriaView = _build_flowr_timeblock_view("aria")

VIEW_BY_ID: dict[str, Any] = {
    "FlowrTimeblockVictorView": FlowrTimeblockVictorView,
    "FlowrTimeblockAriaView": FlowrTimeblockAriaView,
}

CHANNEL_DEFAULTS: dict[str, tuple[str, str]] = {
    "timeblock-victor": ("FlowrTimeblockVictorView", "victor"),
    "timeblock-aria": ("FlowrTimeblockAriaView", "aria"),
}
