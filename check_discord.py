#!/usr/bin/env python3
try:
    import discord
    print(f"✅ discord.py available (version: {discord.__version__})")
except ImportError:
    print("❌ discord.py NOT installed")

try:
    import discord.ext.commands
    print("✅ discord.ext.commands available")
except ImportError:
    print("❌ discord.ext.commands NOT available")

try:
    import os
    token = os.getenv("DISCORD_BOT_TOKEN")
    if token:
        print(f"✅ DISCORD_BOT_TOKEN found (length: {len(token)})")
    else:
        print("❌ DISCORD_BOT_TOKEN not set")
except:
    print("❌ Error checking token")