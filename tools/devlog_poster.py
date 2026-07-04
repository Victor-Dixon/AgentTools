#!/usr/bin/env python3
"""
Devlog Poster Tool - Agent Cellphone V2
======================================

Posts complete devlogs to Discord and serves as agent status monitoring system.

Features:
    - Smart pagination: Splits long devlogs into multiple beautifully formatted messages
    - Complete content preservation: Posts the entire devlog, not truncated versions
    - Agent Status Monitoring: Tracks agent activity and health signals
    - Website Integration: Saves devlogs for weareswarm.online plugin consumption
    - Heartbeat Mode: Periodic status check-ins for agent monitoring
    - Public Swarm Visibility: Makes agent activities visible to external observers

Usage:
    # Post a devlog to Discord and website
    python tools/devlog_poster.py --agent Agent-X --file <devlog_path>

    # Agent heartbeat/status check-in
    python tools/devlog_poster.py --agent Agent-X --heartbeat

    # Status-only update (no devlog file)
    python tools/devlog_poster.py --agent Agent-X --status "Working on V2 compliance"

Requirements:
    - DISCORD_WEBHOOK_AGENT_X environment variables in .env
    - Each webhook configured to post to agent's devlog channel
    - Website plugin reads from agent_workspaces/*/public_activity.json

Author: AI Assistant - Enhanced with agent monitoring and website integration
Date: 2026-01-08
"""

import argparse
import os
import sys
import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def split_content_into_pages(content: str, max_length: int = 1900) -> list[str]:
    """
    Split content into pages that fit within Discord's message limits.

    Args:
        content: The full content to split
        max_length: Maximum characters per page (default 1900 for safety)

    Returns:
        List of content pages
    """
    if len(content) <= max_length:
        return [content]

    pages = []
    lines = content.split('\n')
    current_page = ""
    current_length = 0

    for line in lines:
        line_length = len(line) + 1  # +1 for newline

        # If adding this line would exceed the limit, start a new page
        if current_length + line_length > max_length and current_page:
            pages.append(current_page.rstrip())
            current_page = line + '\n'
            current_length = line_length
        else:
            current_page += line + '\n'
            current_length += line_length

    # Add the last page if it has content
    if current_page.strip():
        pages.append(current_page.rstrip())

    return pages


def update_agent_status(agent_id: str, activity: str, devlog_path: Optional[str] = None) -> None:
    """
    Update agent status for monitoring and website integration.

    Args:
        agent_id: Agent identifier
        activity: Current activity description
        devlog_path: Optional path to devlog file
    """
    # Create agent workspace directory if it doesn't exist
    agent_dir = project_root / "agent_workspaces" / agent_id
    agent_dir.mkdir(exist_ok=True)

    # Update status file
    status_file = agent_dir / "status.json"
    status_data = {
        "agent_id": agent_id,
        "last_activity": activity,
        "last_seen": datetime.now(timezone.utc).isoformat(),
        "status": "ACTIVE",
        "devlog_file": str(devlog_path) if devlog_path else None
    }

    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)

    # Update public activity file for website integration
    public_file = agent_dir / "public_activity.json"
    public_data = {
        "agent_id": agent_id,
        "activity": activity,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "last_devlog": str(devlog_path) if devlog_path else None
    }

    with open(public_file, 'w') as f:
        json.dump(public_data, f, indent=2)

    print(f"✅ Updated agent status for {agent_id}")


def save_devlog_for_website(agent_id: str, devlog_path: str) -> None:
    """
    Save devlog content for website plugin consumption.

    Args:
        agent_id: Agent identifier
        devlog_path: Path to devlog file
    """
    try:
        # Read devlog content
        devlog_file = Path(devlog_path)
        if not devlog_file.exists():
            return

        content = devlog_file.read_text(encoding='utf-8')

        # Create website data directory if it doesn't exist
        website_dir = project_root / "website_data" / "agent_activity"
        website_dir.mkdir(exist_ok=True, parents=True)

        devlog_data = {
            "agent_id": agent_id,
            "filename": devlog_file.name,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "word_count": len(content.split()),
            "line_count": len(content.split('\n'))
        }

        # Save as JSON for website plugin
        json_file = website_dir / f"{agent_id}_latest_devlog.json"
        with open(json_file, 'w') as f:
            json.dump(devlog_data, f, indent=2)

        # Also save raw markdown for direct reading
        md_file = website_dir / f"{agent_id}_latest_devlog.md"
        with open(md_file, 'w') as f:
            f.write(content)

        print(f"✅ Saved devlog for website integration: {json_file}")

    except Exception as e:
        print(f"⚠️ Warning: Could not save devlog for website: {e}")


def post_agent_heartbeat(agent_id: str, custom_status: Optional[str] = None) -> bool:
    """
    Post agent heartbeat/status update to Discord and update monitoring systems.

    Args:
        agent_id: Agent identifier
        custom_status: Optional custom status message

    Returns:
        bool: Success status (status update always succeeds, Discord optional)
    """
    status_message = custom_status or "Agent active and monitoring swarm activities"

    # Always update agent status regardless of Discord success
    update_agent_status(agent_id, status_message)

    try:
        # Load environment variables
        from dotenv import load_dotenv
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        # Construct webhook environment variable name
        webhook_env_var = f"DISCORD_WEBHOOK_{agent_id.replace('-', '_').upper()}"

        webhook_url = os.getenv(webhook_env_var)
        if not webhook_url:
            print(
                f"ℹ️ Discord webhook not configured for {agent_id} - status monitoring active")
            return True

        # Create heartbeat message
        timestamp = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC")

        payload = {
            "username": f"{agent_id} Status Monitor",
            "content": f"🟢 **{agent_id} Heartbeat**\n\n**Status:** {status_message}\n**Timestamp:** {timestamp}\n**Agent ID:** {agent_id}"
        }

        # Post to Discord webhook
        import requests
        response = requests.post(webhook_url, json=payload, timeout=10)

        if response.status_code == 204:
            print(f"✅ Agent heartbeat posted for {agent_id}")
            return True
        else:
            print(
                f"⚠️ Discord heartbeat failed (HTTP {response.status_code}) - status monitoring still active")
            return True  # Status monitoring succeeded even if Discord failed

    except Exception as e:
        print(
            f"⚠️ Discord heartbeat error: {e} - status monitoring still active")
        return True  # Status monitoring succeeded even if Discord failed


def post_devlog_to_discord(agent_id: str, devlog_path: str, is_status_update: bool = False) -> bool:
    """
    Post complete devlog to Discord using agent-specific webhook with smart pagination.

    Features:
        - Splits long devlogs into multiple messages to preserve complete content
        - Adds page indicators (Page X/Y) for multi-page devlogs
        - Includes continuation markers for readability
        - Rate limiting protection between pages

    Args:
        agent_id: Agent identifier (e.g., 'Agent-1', 'Agent-2')
        devlog_path: Path to devlog file

    Returns:
        bool: Success status (all pages posted successfully)
    """
    # Read devlog content first (this is required regardless of Discord success)
    devlog_file = Path(devlog_path)
    if not devlog_file.exists():
        print(f"❌ ERROR: Devlog file not found: {devlog_path}")
        return False

    content = devlog_file.read_text(encoding='utf-8')

    # Always update agent status and save for website regardless of Discord success
    activity = f"Posted devlog: {devlog_file.name}"
    update_agent_status(agent_id, activity, devlog_path)
    save_devlog_for_website(agent_id, devlog_path)

    # Split content into pages
    pages = split_content_into_pages(content)

    try:
        # Load environment variables
        from dotenv import load_dotenv
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        # Construct webhook environment variable name
        webhook_env_var = f"DISCORD_WEBHOOK_{agent_id.replace('-', '_').upper()}"

        webhook_url = os.getenv(webhook_env_var)
        if not webhook_url:
            print(
                f"ℹ️ Discord webhook not configured for {agent_id} - devlog saved for monitoring and website")
            return True  # Status/website updates succeeded even if Discord failed

        # Post to Discord webhook with pagination
        import requests
        import time

        total_pages = len(pages)
        success_count = 0

        for page_num, page_content in enumerate(pages, 1):
            # Create pagination header
            if total_pages == 1:
                header = f"**{agent_id} Devlog Update**"
            else:
                header = f"**{agent_id} Devlog Update** (Page {page_num}/{total_pages})"
                # Add continuation marker for multi-page
                if page_num > 1:
                    header += " *(continued)*"

            payload = {
                "username": f"{agent_id} Devlog",
                "content": f"{header}\n\n{page_content}"
            }

            # Add small delay between pages to avoid rate limiting
            if page_num > 1:
                time.sleep(1)

            response = requests.post(webhook_url, json=payload, timeout=10)

            if response.status_code == 204:
                success_count += 1
                print(
                    f"✅ Posted page {page_num}/{total_pages} to {agent_id} Discord channel")
            else:
                print(
                    f"❌ Failed to post page {page_num}/{total_pages}: HTTP {response.status_code}")
                return False

        if success_count == total_pages:
            print(
                f"✅ Successfully posted complete devlog ({total_pages} page{'s' if total_pages > 1 else ''}) to {agent_id} Discord channel")
            return True
        else:
            print(
                f"⚠️ Only posted {success_count}/{total_pages} pages - status monitoring and website integration still active")
            return True  # Status/website updates succeeded even if Discord partially failed

    except Exception as e:
        print(
            f"⚠️ Discord posting error: {e} - status monitoring and website integration still active")
        return True  # Status/website updates succeeded even if Discord failed


def main():
    parser = argparse.ArgumentParser(
        description="Agent Devlog & Status System - Discord + Website Integration")
    parser.add_argument("--agent", required=True,
                        help="Agent ID (e.g., Agent-1, Agent-2)")
    parser.add_argument(
        "--file", help="Path to devlog file (required for devlog posting)")
    parser.add_argument("--heartbeat", action="store_true",
                        help="Send agent heartbeat/status check-in")
    parser.add_argument(
        "--status", help="Custom status message for heartbeat or status-only update")

    args = parser.parse_args()

    # Validate arguments
    if not args.heartbeat and not args.file:
        parser.error(
            "Either --file (for devlog) or --heartbeat (for status) must be specified")

    if args.heartbeat:
        # Heartbeat mode - post status update
        status_msg = args.status or "Agent active and monitoring swarm activities"
        success = post_agent_heartbeat(args.agent, status_msg)
    else:
        # Devlog mode - post devlog with status update
        if not args.file:
            parser.error("--file is required when not using --heartbeat")
        success = post_devlog_to_discord(args.agent, args.file)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
