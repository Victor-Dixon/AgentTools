"""Dream.OS distributed-agent continuity and control-plane client.

`dream_control` is an early *client/projection* of `dreamosd` (the Dream.OS
control plane currently materialising as the `dreamos-brain` service).  It is
deliberately NOT a second orchestration system:

    DreamVault      -> authority / governance / durable intent
    projectscanner  -> discovery / portfolio intelligence
    AgentTools      -> reusable execution primitives (this repo)
    dreamos-brain   -> dreamosd: durable event/state service (VPS)
    dream_control   -> continuity / context projection ("passdown")

V1 stores state on the filesystem under ``~/.dreamos/control`` using record
shapes that map 1:1 onto the ``dreamos-brain`` HTTP API so migration is a
transport change, not a schema change.
"""

__version__ = "0.1.0"
SCHEMA_VERSION = "dream_control.v1"
