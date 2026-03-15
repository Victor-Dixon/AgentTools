#!/usr/bin/env python3
"""
MCP Server for Swarm Messaging System
Exposes messaging capabilities via Model Context Protocol
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from swarm_mcp.core.messaging import get_queue, HowlUrgency, HowlType
    from swarm_mcp.core.messaging_templates import render_message_template, MessageTemplateCategory
    HAS_CORE = True
except ImportError:
    HAS_CORE = False

def send_agent_message(
    agent_id: str,
    message: str,
    priority: str = "regular",
    category: str = "C2A",
    sender: str = "CAPTAIN",
) -> Dict[str, Any]:
    """Send message to an agent."""
    if not HAS_CORE:
        return {"success": False, "error": "Swarm Core not available"}

    try:
        urgency = HowlUrgency.URGENT if priority.lower() == "urgent" else HowlUrgency.NORMAL
        
        queue = get_queue()
        formatted = render_message_template(
            category=MessageTemplateCategory[category.upper()],
            sender=sender,
            recipient=agent_id,
            body=message,
            priority=priority,
        )
        howl = queue.send(
            sender=sender,
            recipient=agent_id,
            content=formatted,
            urgency=urgency,
            howl_type=HowlType.WOLF_TO_WOLF
        )

        return {
            "success": True,
            "agent": agent_id,
            "message_sent": formatted,
            "priority": priority,
            "id": howl.id
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def broadcast_message(
    message: str,
    priority: str = "regular",
    category: str = "C2A",
    sender: str = "CAPTAIN",
) -> Dict[str, Any]:
    """Broadcast message to all agents."""
    if not HAS_CORE:
        return {"success": False, "error": "Swarm Core not available"}

    try:
        urgency = HowlUrgency.URGENT if priority.lower() == "urgent" else HowlUrgency.NORMAL
        queue = get_queue()
        
        # We need a list of agents. For now, we'll just broadcast to a known set or use a specific howl type
        # But `broadcast` in core takes a list of wolves.
        # We can try to discover wolves or just use a generic "pack" recipient if supported,
        # but the core `broadcast` function iterates over the list.
        # Let's see if we can get the pack list. 
        # Ideally we'd use PackCoordinator, but we don't want to couple heavily here.
        # For now, we'll scan the 'pack_messages' directory or just support a few default agents if we can't find them.
        
        # A simple way is to check who has an inbox in pack_messages
        inboxes = [d.name for d in queue.territory.iterdir() if d.is_dir()]
        if not inboxes:
            # Fallback
            inboxes = ["Agent-1", "Agent-2", "Agent-8"] # Common agents seen in workspace
            
        howls = []
        for wolf in inboxes:
            formatted = render_message_template(
                category=MessageTemplateCategory[category.upper()],
                sender=sender,
                recipient=wolf,
                body=message,
                priority=priority,
            )
            howl = queue.send(
                sender=sender,
                recipient=wolf,
                content=formatted,
                urgency=urgency,
                howl_type=HowlType.PACK_HOWL
            )
            howls.append(howl)

        return {
            "success": True,
            "total_agents": len(inboxes),
            "message_sent": message,
            "category": category.upper(),
            "results": {h.recipient: True for h in howls}
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def read_messages(agent_id: str, unread_only: bool = True, limit: int = 10) -> Dict[str, Any]:
    """Read messages for an agent."""
    if not HAS_CORE:
        return {"success": False, "error": "Swarm Core not available"}
        
    try:
        queue = get_queue()
        howls = queue.listen(agent_id, unheard_only=unread_only, limit=limit)
        
        # Mark as heard if we read them? The tool definition should specify.
        # Usually reading implies consuming.
        for howl in howls:
            if not howl.heard:
                queue.mark_heard(howl.id, agent_id)
                
        return {
            "success": True,
            "agent_id": agent_id,
            "count": len(howls),
            "messages": [
                {
                    "id": h.id,
                    "sender": h.sender,
                    "content": h.content,
                    "urgency": h.urgency.name,
                    "timestamp": h.timestamp.isoformat()
                }
                for h in howls
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """MCP server main loop."""
    print(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "initialize",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "send_agent_message": {
                                "description": "Send message to a specific agent",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {"type": "string"},
                                        "message": {"type": "string"},
                                        "priority": {
                                            "type": "string",
                                            "enum": ["regular", "urgent"],
                                            "default": "regular",
                                        },
                                        "category": {
                                            "type": "string",
                                            "enum": ["S2A", "D2A", "C2A", "A2A"],
                                            "default": "C2A",
                                        },
                                        "sender": {"type": "string", "default": "CAPTAIN"},
                                    },
                                    "required": ["agent_id", "message"],
                                },
                            },
                            "broadcast_message": {
                                "description": "Broadcast message to all known agents",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"},
                                        "priority": {
                                            "type": "string",
                                            "enum": ["regular", "urgent"],
                                            "default": "regular",
                                        },
                                        "category": {
                                            "type": "string",
                                            "enum": ["S2A", "D2A", "C2A", "A2A"],
                                            "default": "C2A",
                                        },
                                        "sender": {"type": "string", "default": "CAPTAIN"},
                                    },
                                    "required": ["message"],
                                },
                            },
                            "read_messages": {
                                "description": "Read messages for an agent (and mark as read)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {"type": "string"},
                                        "unread_only": {"type": "boolean", "default": True},
                                        "limit": {"type": "integer", "default": 10},
                                    },
                                    "required": ["agent_id"],
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "swarm-messaging", "version": "1.0.0"},
                },
            }
        )
    )
    sys.stdout.flush()

    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "send_agent_message":
                    result = send_agent_message(**arguments)
                elif tool_name == "broadcast_message":
                    result = broadcast_message(**arguments)
                elif tool_name == "read_messages":
                    result = read_messages(**arguments)
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}

                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
                }))
                sys.stdout.flush()
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": str(e)}
            }))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
