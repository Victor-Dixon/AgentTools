#!/usr/bin/env python3
"""
Basic Agent Example
===================

Demonstrates how to:
1. Initialize the messaging system
2. Send a message to another agent (or Captain)
3. Check the inbox for replies

This represents the "Hello World" of the Swarm.
"""

import sys
import time
from pathlib import Path

# Ensure we can import swarm_mcp
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarm_mcp.core.messaging import get_queue, HowlUrgency

def main():
    print("🐺 Initializing Basic Agent...")
    
    # 1. Get the message queue (The "Howl" system)
    queue = get_queue()
    print(f"✅ Connected to message territory: {queue.territory}")

    # 2. Send a message
    sender = "Agent-Basic"
    recipient = "Captain"
    content = "Reporting for duty! Ready to receive tasks."
    
    print(f"\n📤 Sending message from {sender} to {recipient}...")
    msg = queue.send(
        sender=sender,
        recipient=recipient,
        content=content,
        urgency=HowlUrgency.NORMAL
    )
    print(f"   Message sent! ID: {msg.id}")

    # 3. Simulate the Captain replying (normally done by another process)
    print("\n🤖 Simulating Captain's reply...")
    time.sleep(1)
    queue.send(
        sender=recipient,
        recipient=sender,
        content="Welcome to the pack. Check the task log.",
        urgency=HowlUrgency.NORMAL
    )

    # 4. Check Inbox
    print(f"\n📥 Checking inbox for {sender}...")
    messages = queue.listen(sender)
    
    if messages:
        for m in messages:
            print(f"   [{m.timestamp.strftime('%H:%M:%S')}] From {m.sender}: {m.content}")
            # Mark as heard so we don't process it again
            queue.mark_heard(m.id, sender)
    else:
        print("   No messages found.")

    print("\n✅ Basic Agent workflow complete.")

if __name__ == "__main__":
    main()
