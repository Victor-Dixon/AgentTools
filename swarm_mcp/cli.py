#!/usr/bin/env python3
"""
🐺 Swarm MCP Toolbelt CLI

WE ARE SWARM - A pack of wolves, not bees.
"Alone we are strong. Together we are unstoppable."
"""

import argparse
import sys
from pathlib import Path


def cmd_status(args):
    """Show agent status."""
    from .core.coordinator import PackCoordinator
    
    pack = PackCoordinator(
        wolves=args.agents.split(",") if args.agents else ["agent-1"],
        den=args.workspace
    )
    
    print("🐺 Swarm Status")
    print("=" * 40)
    
    for agent_id in pack.wolves:
        status = pack.get_status(agent_id)
        if status.role == "alpha":
            icon = "👑"
        elif status.status == "ready":
            icon = "🟢"
        elif status.status == "hunting":
            icon = "🔵"
        else:
            icon = "💤"
        print(f"{icon} {agent_id}: {status.status}")
        if status.current_hunt:
            print(f"   └─ Task: {status.current_hunt[:50]}...")
    
    ready = pack.get_ready_wolves()
    print(f"\n📊 {len(ready)}/{len(pack.wolves)} agents ready")


def cmd_send(args):
    """Send a message."""
    from .core.messaging import MessageQueue
    
    queue = MessageQueue(args.messages)
    msg = queue.send(args.sender, args.recipient, args.message)
    
    print(f"✅ Message sent")
    print(f"   From: {msg.sender} → To: {msg.recipient}")
    print(f"   Message: {msg.content[:60]}...")


def cmd_inbox(args):
    """Check inbox for messages."""
    from .core.messaging import MessageQueue
    
    queue = MessageQueue(args.messages)
    messages = queue.listen(args.agent, unheard_only=args.unread)
    
    print(f"📬 Inbox for {args.agent}")
    print("=" * 40)
    
    if not messages:
        print("(no messages)")
        return
    
    for msg in messages:
        icon = "📩" if not msg.heard else "✓"
        urgency = "🚨 " if msg.urgency.value <= 2 else ""
        print(f"{icon} {urgency}From {msg.sender}:")
        print(f"   {msg.content[:60]}...")
        print()


def cmd_search(args):
    """Search shared knowledge."""
    from .core.memory import PackMemory
    
    memory = PackMemory(args.memory)
    results = memory.recall(args.query, limit=args.limit)
    
    print(f"🔍 Search results for '{args.query}'")
    print("=" * 40)
    
    if not results:
        print("(nothing found)")
        return
    
    for item in results:
        print(f"📚 {item.title}")
        print(f"   Category: {item.category} | By: {item.wolf_id}")
        print(f"   {item.wisdom[:100]}...")
        print()


def cmd_learn(args):
    """Save something you learned."""
    from .core.memory import PackMemory
    
    memory = PackMemory(args.memory)
    item = memory.share_lore(
        wolf_id=args.agent,
        category=args.category,
        title=args.title,
        wisdom=args.content,
        tags=args.tags.split(",") if args.tags else []
    )
    
    print(f"✅ Knowledge saved!")
    print(f"   Title: {item.title}")
    print(f"   Category: {item.category}")


def cmd_tasks(args):
    """Find tasks in the codebase."""
    from .core.coordinator import PackCoordinator
    
    pack = PackCoordinator(wolves=["scanner"], den=args.workspace)
    prey = pack.scout_territory(args.path)
    
    print(f"📋 Found {len(prey)} tasks in {args.path}")
    print("=" * 40)
    
    for p in prey[:args.limit]:
        priority = "🔴" if p.difficulty >= 4 else "🟡" if p.difficulty >= 3 else "🟢"
        print(f"{priority} [{p.prey_type.upper()}] {p.description[:50]}...")
        if p.location:
            print(f"   └─ {p.location}")
        print()


def cmd_assign(args):
    """Assign a task to an agent."""
    from .core.coordinator import PackCoordinator
    
    pack = PackCoordinator(
        wolves=[args.agent],
        den=args.workspace
    )
    
    pack.assign_hunt(args.agent, args.task, difficulty=args.priority)
    
    print(f"✅ Task assigned to {args.agent}")
    print(f"   Task: {args.task[:60]}...")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="swarm",
        description="🐺 Swarm MCP - Multi-Agent AI Coordination"
    )
    parser.add_argument("--workspace", default="./swarm_workspace", help="Workspace directory")
    parser.add_argument("--messages", default="./swarm_messages", help="Messages directory")
    parser.add_argument("--memory", default="./swarm_memory", help="Shared memory directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # status - Check who's available
    status_parser = subparsers.add_parser("status", help="Check which agents are available")
    status_parser.add_argument("--agents", help="Comma-separated agent names")
    status_parser.set_defaults(func=cmd_status)
    
    # send - Send a message
    send_parser = subparsers.add_parser("send", help="Send a message to an agent")
    send_parser.add_argument("sender", help="Your agent name")
    send_parser.add_argument("recipient", help="Recipient agent name")
    send_parser.add_argument("message", help="Message to send")
    send_parser.set_defaults(func=cmd_send)
    
    # inbox - Check messages
    inbox_parser = subparsers.add_parser("inbox", help="Check your messages")
    inbox_parser.add_argument("agent", help="Your agent name")
    inbox_parser.add_argument("--unread", action="store_true", help="Only show unread")
    inbox_parser.set_defaults(func=cmd_inbox)
    
    # search - Search shared knowledge
    search_parser = subparsers.add_parser("search", help="Search shared knowledge")
    search_parser.add_argument("query", help="What to search for")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")
    search_parser.set_defaults(func=cmd_search)
    
    # learn - Save something learned
    learn_parser = subparsers.add_parser("learn", help="Save something you learned")
    learn_parser.add_argument("--agent", required=True, help="Your agent name")
    learn_parser.add_argument("--category", required=True, help="Category (e.g., debugging, api)")
    learn_parser.add_argument("--title", required=True, help="Short title")
    learn_parser.add_argument("--content", required=True, help="What you learned")
    learn_parser.add_argument("--tags", help="Comma-separated tags")
    learn_parser.set_defaults(func=cmd_learn)
    
    # tasks - Find tasks in codebase
    tasks_parser = subparsers.add_parser("tasks", help="Find tasks in the codebase")
    tasks_parser.add_argument("--path", default=".", help="Path to scan")
    tasks_parser.add_argument("--limit", type=int, default=20, help="Max results")
    tasks_parser.set_defaults(func=cmd_tasks)
    
    # assign - Assign a task
    assign_parser = subparsers.add_parser("assign", help="Assign a task to an agent")
    assign_parser.add_argument("agent", help="Agent to assign to")
    assign_parser.add_argument("task", help="Task description")
    assign_parser.add_argument("--priority", type=int, default=3, help="Priority 1-5 (1=highest)")
    assign_parser.set_defaults(func=cmd_assign)
    
    args = parser.parse_args()
    
    if not args.command:
        print("🐺 WE ARE SWARM")
        print("=" * 40)
        print()
        print("Commands:")
        print("  status   - Check which agents are available")
        print("  send     - Send a message to an agent")
        print("  inbox    - Check your messages")
        print("  search   - Search shared knowledge")
        print("  learn    - Save something you learned")
        print("  tasks    - Find tasks in the codebase")
        print("  assign   - Assign a task to an agent")
        print()
        print("Examples:")
        print("  swarm status --agents agent-1,agent-2,agent-3")
        print("  swarm send agent-1 agent-2 \"Please review my PR\"")
        print("  swarm inbox agent-2 --unread")
        print("  swarm search \"auth bug\"")
        print("  swarm learn --agent agent-1 --category bugs --title \"Auth fix\" --content \"...\"")
        print("  swarm tasks --path ./src")
        print("  swarm assign agent-2 \"Fix the login bug\"")
        print()
        return 1
    
    try:
        args.func(args)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
