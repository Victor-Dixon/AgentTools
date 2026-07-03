# 🐺 WE ARE SWARM

**Multi-Agent AI Coordination Framework** with Model Context Protocol (MCP) support.

*A pack of wolves, not bees.*

*"Alone we are strong. Together we are unstoppable."*

---

## What Is This?

A framework that enables **multiple AI agents** (Claude, GPT, Gemini, etc.) to work together autonomously - coordinating tasks, sharing knowledge, making collective decisions, and learning from each other.

Think of it as the **nervous system for an AI swarm**.

Repository scope note: this checkout also contains secondary AgentTools/operator tooling (`mcp_servers/`, `tools/`, `tools_v2/`) and a separate Family Focus Board TypeScript product lane (`apps/`, `packages/`). The canonical domain model and lane boundary live in [`docs/architecture/DOMAIN_MODEL.md`](docs/architecture/DOMAIN_MODEL.md).

```
┌─────────────────────────────────────────────────────────────┐
│                     WE ARE SWARM 🐺                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐      messages      ┌─────────┐               │
│   │ Agent-1 │◄──────────────────►│ Agent-2 │               │
│   │ Claude  │                    │  GPT-4  │               │
│   └────┬────┘                    └────┬────┘               │
│        │       shared memory          │                     │
│        │     conflict detection       │                     │
│        │       consensus voting       │                     │
│        └──────────┬───────────────────┘                     │
│                   ▼                                         │
│   ┌─────────────────────────────────────────┐              │
│   │           SWARM MCP TOOLBELT            │              │
│   │                                         │              │
│   │  Core:        IP-Level:                 │              │
│   │  • Messaging  • Consensus Engine        │              │
│   │  • Tasks      • Conflict Detector       │              │
│   │  • Memory     • Agent DNA               │              │
│   │               • Work Proof              │              │
│   │               • Pattern Miner           │              │
│   └─────────────────────────────────────────┘              │
│                   ▲                                         │
│        ┌──────────┴───────────────────┐                     │
│        │                              │                     │
│   ┌─────────┐                    ┌─────────┐               │
│   │ Agent-3 │                    │ Agent-4 │               │
│   │ Claude  │                    │ Gemini  │               │
│   └─────────┘                    └─────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

```bash
pip install swarm-mcp
```

```python
from swarm_mcp import PackCoordinator, AgentDNA, ConsensusEngine

# Coordinate your swarm
pack = PackCoordinator(wolves=["agent-1", "agent-2", "agent-3"])

# Check who's available
ready = pack.get_ready_wolves()

# Assign work
pack.assign_hunt("agent-1", "Fix the authentication bug")

# Learn which agent is best at what
dna = AgentDNA()
best_agent, confidence = dna.find_best_agent(category="debugging")

# Make collective decisions
consensus = ConsensusEngine()
proposal = consensus.propose("agent-1", "Use PostgreSQL", "Need ACID transactions...")
```

---

## 📦 What's Included

### Core Modules

| Module | Purpose |
|--------|---------|
| **PackCoordinator** | Central orchestration - assign tasks, check status, broadcast messages |
| **MessageQueue** | Agent-to-agent async messaging with priority levels |
| **PackMemory** | Shared knowledge base - learnings persist across sessions |
| **SwarmBrain** | Learning and decision records used by memory/brain MCP surfaces |
| **TaskScorer** | ROI/priority scoring helper for tasks |
| **VerificationHarness** | Command, file, import, and page-fetch verification helper |
| **RecoveryManager** | Backup, rollback, and failure recovery helper |

### IP-Level Modules (The Goldmines 💎)

| Module | Purpose | Why It's Novel |
|--------|---------|----------------|
| **ConsensusEngine** | Multi-agent voting and decisions | AI agents reach agreement without human intervention |
| **ConflictDetector** | Prevent duplicate work | Real-time intent tracking stops wasted effort |
| **AgentDNA** | Learn agent strengths over time | Capability profiling without ML models |
| **WorkProofSystem** | Cryptographic proof of completion | Verifiable work with SHA256 hashes |
| **PatternMiner** | Learn from successful coordination | Emergent pattern discovery |

---

## 🗳️ ConsensusEngine - Collective Decision Making

When the swarm needs to decide something together:

```python
from swarm_mcp import ConsensusEngine, VoteType, ConsensusRule

consensus = ConsensusEngine()

# Create a proposal
proposal = consensus.propose(
    proposer="agent-1",
    title="Use PostgreSQL for user data",
    description="We need ACID transactions for payment processing",
    rule=ConsensusRule.SUPERMAJORITY  # 66% must agree
)

# Agents vote with reasoning
consensus.vote(proposal.id, "agent-2", VoteType.APPROVE,
               "Agree - ACID is critical for money")
consensus.vote(proposal.id, "agent-3", VoteType.APPROVE,
               "Good choice, I'm familiar with Postgres")
consensus.vote(proposal.id, "agent-4", VoteType.REJECT,
               "Would prefer MongoDB for flexibility")

# Check the result
result = consensus.resolve(proposal.id)
print(result)
# {"passed": True, "reason": "3/4 approved (>66% required)"}
```

**Voting Rules:**
- `UNANIMOUS` - Everyone must agree
- `MAJORITY` - >50% must agree
- `SUPERMAJORITY` - >66% must agree
- `QUORUM` - Specific agents must vote
- `WEIGHTED` - Votes weighted by expertise

---

## 🚫 ConflictDetector - No Duplicate Work

Stop two agents from working on the same thing:

```python
from swarm_mcp import ConflictDetector

detector = ConflictDetector()

# Agent-1 declares what they're working on
intent, conflicts = detector.declare_intent(
    agent_id="agent-1",
    description="Fixing authentication bug",
    files=["src/auth.py", "src/login.py"],
    keywords=["auth", "login", "token"]
)

# Later, Agent-2 wants to work on the same area
conflicts = detector.check_conflicts(
    agent_id="agent-2",
    files=["src/auth.py"]
)

if conflicts:
    print(f"⚠️ Conflict: {conflicts[0].reason}")
    # "Same file(s): {'src/auth.py'}"
    # Agent-2 should pick different work!

# When done, free up the area
detector.complete_work("agent-1")
```

**Conflict Severity:**
- `BLOCKING` - Same file AND function (stop immediately)
- `HIGH` - Same file
- `MEDIUM` - Same module
- `LOW` - Similar keywords
- `INFO` - Just FYI

---

## 🧬 AgentDNA - Learn Agent Strengths

Track what each agent is good at:

```python
from swarm_mcp import AgentDNA

dna = AgentDNA()

# Record completed work
dna.record_task(
    agent_id="agent-1",
    category="debugging",
    description="Fixed auth token expiry bug",
    files=["src/auth.py", "src/tokens.py"],
    duration_minutes=45,
    success=True,
    quality_score=0.95
)

# Over time, patterns emerge...

# Find the best agent for a new task
best_agent, confidence = dna.find_best_agent(
    category="debugging",
    files=["src/auth.py"]
)
print(f"Best agent: {best_agent} (confidence: {confidence:.0%})")
# "Best agent: agent-1 (confidence: 92%)"

# Get an agent's full profile
profile = dna.get_profile("agent-1")
print(f"Strengths: {profile.strengths}")
# ["debugging", "auth", "python"]

# Estimate how long a task will take
estimate = dna.get_task_estimate("agent-1", "debugging")
print(f"Estimated time: {estimate:.0f} minutes")

# Get leaderboard
leaderboard = dna.get_leaderboard(category="debugging")
# [("agent-1", 0.95, 12), ("agent-3", 0.88, 8), ...]
```

---

## ✅ WorkProofSystem - Verifiable Completion

Cryptographic proof that work was actually done:

```python
from swarm_mcp import WorkProofSystem

proofs = WorkProofSystem()

# BEFORE work: Commit to the task
commitment = proofs.commit(
    agent_id="agent-1",
    task="Fix authentication bug",
    files=["src/auth.py", "src/login.py"]
)
# Snapshots file hashes, timestamps, etc.

# ... agent does the work ...

# AFTER work: Generate proof
proof = proofs.prove(commitment.id)

print(f"Files modified: {proof.files_modified}")
print(f"Git commits: {proof.git_commits}")
print(f"Duration: {proof.duration_seconds / 60:.1f} minutes")
print(f"Proof hash: {proof.proof_hash[:16]}...")
print(f"Valid: {proof.valid}")

# Anyone can verify the proof
is_valid, issues = proofs.verify(proof)
if not is_valid:
    print(f"Problems: {issues}")
```

**What It Tracks:**
- Before/after file hashes (SHA256)
- Git commits during the work period
- Time spent
- Files created, modified, deleted
- Tamper-evident proof hash

---

## 📊 PatternMiner - Learn What Works

Automatically discover successful coordination patterns:

```python
from swarm_mcp import PatternMiner

miner = PatternMiner()

# Record events as they happen
miner.record_event(
    event_type="task_complete",
    agents=["agent-1", "agent-3"],
    context={"category": "debugging", "file": "auth.py"},
    outcome="success",
    duration_minutes=30,
    quality_score=0.95
)

# Over time, patterns emerge automatically...

# Get suggestions for a new situation
suggestions = miner.suggest(
    context={"category": "debugging", "file": "auth.py"}
)

for suggestion in suggestions:
    print(f"💡 {suggestion.pattern_name}")
    print(f"   Confidence: {suggestion.confidence:.0%}")
    print(f"   Suggested: {suggestion.suggested_actions}")
    print(f"   Expected: {suggestion.expected_outcome}")

# Example output:
# 💡 Successful pairing: agent-1 + agent-3
#    Confidence: 85%
#    Suggested: ['Pair agent-1 with agent-3']
#    Expected: 95% success rate based on 8 past events

# See all discovered patterns
patterns = miner.get_patterns()
for p in patterns:
    print(f"{p.name}: {p.success_rate:.0%} success ({p.occurrence_count} times)")
```

**Pattern Types Discovered:**
- **Pairing** - Which agents work well together
- **Sequence** - Task order that leads to success
- **Timing** - Peak productivity hours
- **Context** - Who's best for what category

---

## 🖥️ CLI Commands

```bash
# Check which agents are available
swarm status --agents agent-1,agent-2,agent-3

# Send a message
swarm send agent-1 agent-2 "Please review my PR"

# Check inbox
swarm inbox agent-2 --unread

# Search shared knowledge
swarm search "authentication bug"

# Save something learned
swarm learn --agent agent-1 --category debugging \
  --title "Auth fix pattern" --content "Always check token expiry first..."

# Find tasks in codebase
swarm tasks --path ./src

# Assign a task
swarm assign agent-2 "Fix the login bug"
```

---

## 🔌 MCP Integration

Add to your Claude Desktop or Cursor config:

```json
{
  "mcpServers": {
    "swarm-messaging": {
      "command": "python",
      "args": ["-m", "swarm_mcp.servers.messaging"]
    },
    "swarm-memory": {
      "command": "python",
      "args": ["-m", "swarm_mcp.servers.memory"]
    },
    "swarm-tasks": {
      "command": "python",
      "args": ["-m", "swarm_mcp.servers.tasks"]
    },
    "swarm-control": {
      "command": "python",
      "args": ["-m", "swarm_mcp.servers.control"]
    },
    "swarm-tools": {
      "command": "python",
      "args": ["-m", "swarm_mcp.servers.tools"]
    }
  }
}
```

---

## 📌 Current Project Status

The canonical execution status lives in [`docs/root/MASTER_TASK_LOG.md`](docs/root/MASTER_TASK_LOG.md), with a human-readable dashboard in [`NEXT_UP.md`](NEXT_UP.md).

Current status as of 2026-07-03:

- SWARM MCP package version is `0.6.0`.
- M0 Python gates and M2 MCP catalog integrity are complete per SSOT evidence.
- PyPI publish for `v0.6.0` is blocked because the tag publish job did not receive `PYPI_API_TOKEN`.
- Clean install proof for `swarm-mcp==0.6.0` remains blocked until publish succeeds.
- AgentTools/operator tooling and Family Focus Board remain secondary lanes documented in the domain model.

Current documentation entry points:

- [`docs/architecture/DOMAIN_MODEL.md`](docs/architecture/DOMAIN_MODEL.md) — canonical domain model and repository audit
- [`MASTER_TASK_LIST.md`](MASTER_TASK_LIST.md) — current actionable task list and blockers
- [`ROADMAP.md`](ROADMAP.md) — current sequencing and milestones
- [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) — repository structure and service relationships
- [`PROJECT_AUDIT_REPORT.md`](PROJECT_AUDIT_REPORT.md) — comprehensive health review

---

## 🏗️ Architecture

```
swarm_mcp/
├── __init__.py              # Main exports
├── cli.py                   # Command-line interface
├── core/
│   ├── coordinator.py       # PackCoordinator
│   ├── messaging.py         # MessageQueue
│   ├── memory.py            # PackMemory
│   ├── brain.py             # SwarmBrain
│   ├── consensus.py         # ConsensusEngine 💎
│   ├── conflict.py          # ConflictDetector 💎
│   ├── agent_dna.py         # AgentDNA 💎
│   ├── work_proof.py        # WorkProofSystem 💎
│   ├── verification.py      # VerificationHarness
│   ├── recovery.py          # RecoveryManager
│   ├── task_scoring.py      # TaskScorer
│   ├── messaging_templates.py # Structured message templates
│   └── pattern_miner.py     # PatternMiner 💎
├── servers/                 # MCP server implementations
└── tools/                   # Additional utilities
```

---

## 📈 Why This Matters

| Problem | Traditional Approach | Swarm Approach |
|---------|---------------------|----------------|
| Task assignment | Human decides | AgentDNA finds best match |
| Duplicate work | Hope it doesn't happen | ConflictDetector prevents it |
| Decisions | Human makes them | ConsensusEngine - agents vote |
| Trust | Assume work is done | WorkProofSystem verifies |
| Learning | Start fresh each time | PatternMiner remembers what works |

---

## 🤝 Contributing

We welcome new members to the swarm! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

MIT License - see [LICENSE](LICENSE).

---

## 🐺 WE ARE SWARM

*"The strength of the pack is the wolf, and the strength of the wolf is the pack."*

**Alone we are strong. Together we are unstoppable.**

---

### Stats

- **5 packaged MCP server modules** exposed by `pyproject.toml`
- **12 CLI subcommands** for coordination workflows
- **Zero required runtime dependencies** in the Python package metadata
- **File-backed** coordination state
- **MCP-ready** integration surface for Claude, Cursor, and other MCP clients
