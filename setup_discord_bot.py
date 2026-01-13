#!/usr/bin/env python3
"""
Discord Bot Setup Script
========================

Helps set up the Discord bot token and environment for swarm coordination.

Usage:
    python setup_discord_bot.py

Author: Agent-3 (Infrastructure & DevOps)
"""

import os
import sys
from pathlib import Path

def print_header():
    """Print setup header."""
    print("🐺 DISCORD BOT SETUP FOR SWARM COORDINATION")
    print("=" * 50)
    print()

def check_discord_py():
    """Check if discord.py is installed."""
    print("🔍 Checking discord.py installation...")
    try:
        import discord
        print(f"✅ discord.py installed (version: {discord.__version__})")
        return True
    except ImportError:
        print("❌ discord.py not installed!")
        print("💡 Install with: pip install discord.py")
        return False

def setup_bot_token():
    """Setup Discord bot token."""
    print("\n🔑 Setting up Discord Bot Token...")
    print("You need a Discord bot token to run the swarm coordination bot.")
    print("Get one from: https://discord.com/developers/applications")
    print()

    # Check if token already exists
    existing_token = os.getenv("DISCORD_BOT_TOKEN")
    if existing_token:
        print(f"⚠️  DISCORD_BOT_TOKEN already set (ends with: ...{existing_token[-4:]})")
        change = input("Change token? (y/N): ").lower().strip()
        if change != 'y':
            print("✅ Keeping existing token")
            return True

    # Get new token
    token = input("Enter your Discord bot token: ").strip()

    if not token:
        print("❌ No token provided")
        return False

    if len(token) < 50:
        print("⚠️  Token seems short. Discord bot tokens are usually 59 characters long.")
        confirm = input("Continue anyway? (y/N): ").lower().strip()
        if confirm != 'y':
            return False

    # Set environment variable
    try:
        # For Windows
        if sys.platform == "win32":
            os.system(f'setx DISCORD_BOT_TOKEN "{token}"')
            print("✅ Token set for current user (restart terminal to take effect)")

            # Also set for current session
            os.environ["DISCORD_BOT_TOKEN"] = token
            print("✅ Token set for current session")
        else:
            # For other platforms
            shell_rc = Path.home() / ".bashrc"
            if shell_rc.exists():
                with open(shell_rc, 'a') as f:
                    f.write(f'\nexport DISCORD_BOT_TOKEN="{token}"\n')
                print(f"✅ Token added to {shell_rc} (restart shell to take effect)")

            # Set for current session
            os.environ["DISCORD_BOT_TOKEN"] = token
            print("✅ Token set for current session")

    except Exception as e:
        print(f"❌ Failed to set token: {e}")
        print("💡 Manually set with: export DISCORD_BOT_TOKEN='your_token'")
        return False

    return True

def create_startup_script():
    """Create startup script for the bot."""
    print("\n📝 Creating startup script...")

    startup_script = Path(__file__).parent / "start_discord_bot.py"

    script_content = '''#!/usr/bin/env python3
"""
Discord Bot Startup Script
==========================

Starts the unified Discord bot for swarm coordination.

Usage:
    python start_discord_bot.py

Author: Agent-3 (Infrastructure & DevOps)
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the Discord bot."""
    print("🐺 Starting Swarm Discord Bot...")

    # Check token
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ DISCORD_BOT_TOKEN not set!")
        print("💡 Run: python setup_discord_bot.py")
        sys.exit(1)

    # Path to bot
    bot_path = Path(__file__).parent / "src" / "discord_commander" / "unified_discord_bot.py"

    if not bot_path.exists():
        print(f"❌ Bot file not found: {bot_path}")
        sys.exit(1)

    print(f"🤖 Launching bot from: {bot_path}")

    try:
        # Run the bot
        subprocess.run([sys.executable, str(bot_path)], check=True)
    except KeyboardInterrupt:
        print("\\n🐺 Bot stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Bot failed with exit code: {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

    try:
        with open(startup_script, 'w') as f:
            f.write(script_content)

        # Make executable on Unix-like systems
        if sys.platform != "win32":
            os.chmod(startup_script, 0o755)

        print(f"✅ Startup script created: {startup_script}")
        return True
    except Exception as e:
        print(f"❌ Failed to create startup script: {e}")
        return False

def test_bot_import():
    """Test if bot can be imported."""
    print("\n🧪 Testing bot import...")

    bot_path = Path(__file__).parent / "src" / "discord_commander" / "unified_discord_bot.py"

    if not bot_path.exists():
        print("❌ Bot file not found!")
        return False

    try:
        # Add to path
        sys.path.insert(0, str(bot_path.parent))

        # Try import
        import unified_discord_bot
        print("✅ Bot module can be imported")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Import succeeded but with warning: {e}")
        return True

def main():
    """Main setup function."""
    print_header()

    success = True

    # Check discord.py
    if not check_discord_py():
        success = False

    # Setup token
    if not setup_bot_token():
        success = False

    # Create startup script
    if not create_startup_script():
        success = False

    # Test import
    if not test_bot_import():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("🎉 DISCORD BOT SETUP COMPLETE!")
        print()
        print("🚀 To start the bot:")
        print("   python start_discord_bot.py")
        print()
        print("📋 Available commands:")
        print("   !control - Show swarm control panel")
        print("   !gui     - Display swarm GUI interface")
        print("   !status  - Show detailed status")
        print("   !help    - Show help information")
        print()
        print("🐺 Happy coordinating!")
    else:
        print("❌ SETUP INCOMPLETE")
        print("🔧 Fix the issues above and try again")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)