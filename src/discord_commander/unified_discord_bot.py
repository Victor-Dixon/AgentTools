#!/usr/bin/env python3
"""
Unified Discord Bot for Swarm Coordination
==========================================

Provides Discord integration for swarm operations with !control and !gui commands.

Features:
- !control: Shows swarm control panel with status and management options
- !gui: Displays swarm GUI interface embed
- Real-time swarm status updates
- Command handling and coordination

Author: Agent-3 (Infrastructure & DevOps)
"""

import os
import sys
import asyncio
import discord
from discord.ext import commands, tasks
from pathlib import Path
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import swarm components (with fallbacks)
try:
    from swarm_mcp import SwarmCoordinator
    HAS_SWARM = True
except ImportError:
    HAS_SWARM = False
    SwarmCoordinator = None

# Bot configuration
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
COMMAND_PREFIX = "!"
BOT_STATUS = "Swarm Coordination Active 🐺"

class SwarmDiscordBot(commands.Bot):
    """Unified Discord bot for swarm coordination."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.swarm_coordinator = None
        self.start_time = time.time()

    async def setup_hook(self):
        """Setup hook called when bot is starting."""
        print("🐺 Setting up Swarm Discord Bot...")

        # Initialize swarm coordinator if available
        if HAS_SWARM:
            try:
                self.swarm_coordinator = SwarmCoordinator()
                print("✅ Swarm coordinator initialized")
            except Exception as e:
                print(f"⚠️  Swarm coordinator failed: {e}")
        else:
            print("⚠️  Swarm coordinator not available")

        # Start status update task
        self.update_status.start()

    @tasks.loop(minutes=5)
    async def update_status(self):
        """Update bot status with swarm information."""
        try:
            if self.swarm_coordinator:
                # Get swarm status
                status = await self.swarm_coordinator.get_status()
                active_agents = status.get('active_agents', 0)
                await self.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.watching,
                        name=f"🐺 {active_agents} agents coordinating"
                    )
                )
            else:
                await self.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.listening,
                        name=BOT_STATUS
                    )
                )
        except Exception as e:
            print(f"⚠️  Status update failed: {e}")

    async def on_ready(self):
        """Called when bot is ready."""
        print(f"🐺 Swarm Discord Bot ready!")
        print(f"   Logged in as: {self.user}")
        print(f"   Connected to {len(self.guilds)} guild(s)")
        print(f"   Command prefix: {COMMAND_PREFIX}")

    async def on_command_error(self, ctx, error):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Unknown command. Try `!help` for available commands.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        else:
            print(f"Command error: {error}")
            await ctx.send("❌ An error occurred while processing your command.")

async def setup_commands(bot):
    """Setup bot commands."""

    @bot.command(name="control")
    async def control_panel(ctx):
        """Show swarm control panel."""
        embed = discord.Embed(
            title="🐺 Swarm Control Panel",
            description="Manage and monitor swarm operations",
            color=0x3498db,
            timestamp=datetime.utcnow()
        )

        # Swarm status
        if bot.swarm_coordinator:
            try:
                status = await bot.swarm_coordinator.get_status()
                embed.add_field(
                    name="🟢 Active Agents",
                    value=str(status.get('active_agents', 'Unknown')),
                    inline=True
                )
                embed.add_field(
                    name="📊 Tasks",
                    value=str(status.get('active_tasks', 'Unknown')),
                    inline=True
                )
                embed.add_field(
                    name="⚡ Coordination Level",
                    value=status.get('coordination_level', 'Unknown'),
                    inline=True
                )
            except Exception as e:
                embed.add_field(
                    name="❌ Status Error",
                    value=f"Unable to get status: {str(e)[:100]}",
                    inline=False
                )
        else:
            embed.add_field(
                name="⚠️ Swarm Status",
                value="Swarm coordinator not available",
                inline=False
            )

        # Control buttons (text-based since Discord.py doesn't support buttons easily)
        embed.add_field(
            name="🎮 Available Commands",
            value="```!status - Show detailed status\n!agents - List active agents\n!tasks - Show current tasks\n!coordination - Coordination info```",
            inline=False
        )

        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @bot.command(name="gui")
    async def gui_interface(ctx):
        """Show swarm GUI interface."""
        embed = discord.Embed(
            title="🖥️ Swarm GUI Interface",
            description="Interactive swarm management interface",
            color=0x2ecc71,
            timestamp=datetime.utcnow()
        )

        embed.add_field(
            name="🌐 Web Interface",
            value="[Access Swarm GUI](https://swarm-interface.example.com)",
            inline=False
        )

        embed.add_field(
            name="📱 Mobile Access",
            value="Available via Swarm mobile app",
            inline=True
        )

        embed.add_field(
            name="🖥️ Desktop Client",
            value="Download from swarm-tools repository",
            inline=True
        )

        # GUI features
        features = """
• Real-time swarm monitoring
• Agent coordination dashboard
• Task management interface
• Performance analytics
• Configuration management
• Log viewer and debugging tools
        """

        embed.add_field(
            name="✨ Features",
            value=f"```css\n{features}```",
            inline=False
        )

        embed.set_footer(text=f"GUI requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @bot.command(name="status")
    async def swarm_status(ctx):
        """Show detailed swarm status."""
        embed = discord.Embed(
            title="📊 Swarm Status Report",
            color=0xf39c12,
            timestamp=datetime.utcnow()
        )

        uptime = time.time() - bot.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)

        embed.add_field(
            name="⏱️ Bot Uptime",
            value=f"{hours}h {minutes}m",
            inline=True
        )

        embed.add_field(
            name="🤖 Bot Version",
            value="Unified Discord Bot v1.0",
            inline=True
        )

        embed.add_field(
            name="🔗 Connected Guilds",
            value=str(len(bot.guilds)),
            inline=True
        )

        if bot.swarm_coordinator:
            embed.add_field(
                name="🐺 Swarm Coordinator",
                value="✅ Connected",
                inline=True
            )
        else:
            embed.add_field(
                name="🐺 Swarm Coordinator",
                value="❌ Not Available",
                inline=True
            )

        await ctx.send(embed=embed)

    @bot.command(name="help")
    async def help_command(ctx):
        """Show help information."""
        embed = discord.Embed(
            title="🐺 Swarm Discord Bot Help",
            description=f"Prefix: `{COMMAND_PREFIX}`",
            color=0x9b59b6
        )

        commands = """
**Core Commands:**
`!control` - Show swarm control panel
`!gui` - Display swarm GUI interface
`!status` - Detailed swarm status
`!help` - Show this help message

**Swarm Management:**
`!agents` - List active agents
`!tasks` - Show current tasks
`!coordination` - Coordination information
        """

        embed.add_field(
            name="📋 Available Commands",
            value=f"```css\n{commands}```",
            inline=False
        )

        embed.set_footer(text="Swarm coordination system")
        await ctx.send(embed=embed)

def main():
    """Main function to run the Discord bot."""
    if not BOT_TOKEN:
        print("❌ ERROR: DISCORD_BOT_TOKEN environment variable not set!")
        print("💡 Set it with: $env:DISCORD_BOT_TOKEN='your_bot_token_here'")
        sys.exit(1)

    # Create intents
    intents = discord.Intents.default()
    intents.message_content = True

    # Create bot
    bot = SwarmDiscordBot(
        command_prefix=COMMAND_PREFIX,
        intents=intents,
        help_command=None  # Disable default help
    )

    # Setup commands
    asyncio.run(setup_commands(bot))

    print("🐺 Starting Swarm Discord Bot...")
    print(f"   Token: {'*' * (len(BOT_TOKEN)-10)}...{BOT_TOKEN[-4:]}")
    print(f"   Command prefix: {COMMAND_PREFIX}")

    try:
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ ERROR: Invalid bot token!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()