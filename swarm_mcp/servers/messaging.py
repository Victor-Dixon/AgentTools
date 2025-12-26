#!/usr/bin/env python3
"""
MCP Server for Swarm Messaging System (swarm_mcp)
Exposes messaging capabilities via Model Context Protocol
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from swarm_mcp.core.messaging import MessageQueue, HowlUrgency, HowlType

def get_queue(territory: str = "./swarm_messages") -> MessageQueue:
    """Get message queue instance."""
    return MessageQueue(territory)

def send_message(sender: str, recipient: str, content: str, urgency: str = "normal") -> dict:
    """Send message to an agent."""
    try:
        # Map urgency string to enum
        urgency_map = {
            "emergency": HowlUrgency.EMERGENCY,
            "urgent": HowlUrgency.URGENT,
            "normal": HowlUrgency.NORMAL,
            "low": HowlUrgency.LOW
        }
        urgency_enum = urgency_map.get(urgency.lower(), HowlUrgency.NORMAL)

        queue = get_queue()
        msg = queue.send(
            sender=sender,
            recipient=recipient,
            content=content,
            urgency=urgency_enum
        )

        return {
            "success": True,
            "id": msg.id,
            "sender": msg.sender,
            "recipient": msg.recipient,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def read_inbox(agent_id: str, unread_only: bool = False, limit: int = 50) -> dict:
    """Read messages from inbox."""
    try:
        queue = get_queue()
        messages = queue.listen(agent_id, unheard_only=unread_only, limit=limit)
        
        result_msgs = []
        for msg in messages:
            result_msgs.append({
                "id": msg.id,
                "sender": msg.sender,
                "recipient": msg.recipient,
                "content": msg.content,
                "urgency": msg.urgency.name,
                "timestamp": msg.timestamp.isoformat(),
                "heard": msg.heard,
                "type": msg.howl_type.value
            })
            
        return {
            "success": True,
            "agent": agent_id,
            "count": len(result_msgs),
            "messages": result_msgs
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def mark_as_read(agent_id: str, message_id: str) -> dict:
    """Mark a message as read."""
    try:
        queue = get_queue()
        success = queue.mark_heard(message_id, agent_id)
        
        if success:
            return {"success": True, "message_id": message_id, "status": "marked_read"}
        else:
            return {"success": False, "error": "Message not found or already read"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def broadcast_message(sender: str, content: str, pack: list[str], urgency: str = "normal") -> dict:
    """Broadcast message to multiple agents."""
    try:
        urgency_map = {
            "emergency": HowlUrgency.EMERGENCY,
            "urgent": HowlUrgency.URGENT,
            "normal": HowlUrgency.NORMAL,
            "low": HowlUrgency.LOW
        }
        urgency_enum = urgency_map.get(urgency.lower(), HowlUrgency.NORMAL)
        
        queue = get_queue()
        howls = []
        for wolf in pack:
            msg = queue.send(
                sender=sender,
                recipient=wolf,
                content=content,
                urgency=urgency_enum,
                howl_type=HowlType.PACK_HOWL
            )
            howls.append(msg.id)
            
        return {
            "success": True,
            "sender": sender,
            "recipients": pack,
            "message_count": len(howls),
            "message_ids": howls
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# MCP Server Protocol
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
                            "send_message": {
                                "description": "Send a message to another agent",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "sender": {
                                            "type": "string",
                                            "description": "ID of the sending agent",
                                        },
                                        "recipient": {
                                            "type": "string",
                                            "description": "ID of the recipient agent",
                                        },
                                        "content": {
                                            "type": "string",
                                            "description": "Message content",
                                        },
                                        "urgency": {
                                            "type": "string",
                                            "enum": ["normal", "urgent", "emergency", "low"],
                                            "default": "normal",
                                        },
                                    },
                                    "required": ["sender", "recipient", "content"],
                                },
                            },
                            "read_inbox": {
                                "description": "Check your messages",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {
                                            "type": "string",
                                            "description": "Your agent ID",
                                        },
                                        "unread_only": {
                                            "type": "boolean",
                                            "description": "Only show unread messages",
                                            "default": False,
                                        },
                                        "limit": {
                                            "type": "integer",
                                            "description": "Max messages to retrieve",
                                            "default": 50,
                                        },
                                    },
                                    "required": ["agent_id"],
                                },
                            },
                            "mark_as_read": {
                                "description": "Mark a message as read/heard",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {
                                            "type": "string",
                                            "description": "Your agent ID",
                                        },
                                        "message_id": {
                                            "type": "string",
                                            "description": "ID of the message to mark read",
                                        },
                                    },
                                    "required": ["agent_id", "message_id"],
                                },
                            },
                            "broadcast_message": {
                                "description": "Broadcast message to multiple agents",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "sender": {
                                            "type": "string",
                                            "description": "ID of the sending agent",
                                        },
                                        "pack": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "List of recipient agent IDs",
                                        },
                                        "content": {
                                            "type": "string",
                                            "description": "Message content",
                                        },
                                        "urgency": {
                                            "type": "string",
                                            "enum": ["normal", "urgent", "emergency", "low"],
                                            "default": "normal",
                                        },
                                    },
                                    "required": ["sender", "pack", "content"],
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "swarm-messaging", "version": "0.1.0"},
                },
            }
        )
    )
    sys.stdout.flush()

    # Handle tool calls
    for line in sys.stdin:
        try:
            if not line.strip():
                continue
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                result = {}
                if tool_name == "send_message":
                    result = send_message(**arguments)
                elif tool_name == "read_inbox":
                    result = read_inbox(**arguments)
                elif tool_name == "mark_as_read":
                    result = mark_as_read(**arguments)
                elif tool_name == "broadcast_message":
                    result = broadcast_message(**arguments)
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}

                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
                        }
                    )
                )
                sys.stdout.flush()
        except Exception as e:
            # Try to report error if we have an id, otherwise just log to stderr
            try:
                req_id = request.get("id") if 'request' in locals() else None
                if req_id:
                     print(
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "error": {"code": -32603, "message": str(e)},
                            }
                        )
                    )
                     sys.stdout.flush()
            except:
                pass

if __name__ == "__main__":
    main()
