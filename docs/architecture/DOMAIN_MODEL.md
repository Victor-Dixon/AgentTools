# Domain Model and Documentation Audit

**Last reviewed:** 2026-07-03  
**Status:** Canonical domain model for this repository  
**Primary execution SSOT:** `docs/root/MASTER_TASK_LOG.md`

This document maps the domain model that can be derived from the current repository. It does not infer product intent beyond the code and documentation present in this checkout. Items that cannot be verified from the repository are marked **Unknown**.

---

## 1. What this project is

This repository is a mixed workspace with three documented lanes:

| Lane | Domain | Primary paths | Current status |
|---|---|---|---|
| SWARM MCP | Multi-agent AI coordination over MCP | `swarm_mcp/`, `tests/`, `integration/` | Active and release-critical; package `swarm-mcp` is version `0.6.0`, tagged, and blocked on PyPI publish secret/configuration. |
| AgentTools/operator tooling | Local MCP servers, tool registries, automation, CI/security/docs helpers | `mcp_servers/`, `tools/`, `tools_v2/`, `_ops/` | Active but secondary to the SWARM MCP release lane. Some registry entries are disabled or require classification. |
| Family Focus Board | Kanban plus shared Pomodoro/focus room product | `apps/api/`, `apps/web/`, `packages/shared/`, `docs/mvp.md` | Separate TypeScript product lane. API and shared timer logic exist; web is scaffold-level and not CI-governed. |

Legacy, quarantine, and research material also exists under paths such as `tools/deprecated/`, `docs/quarantine/`, and `research/`. Its current operational relevance is **Unknown** unless a file explicitly marks it active.

---

## 2. Problem and domain

### Core domain

The core domain is **multi-agent coordination for AI agents**. The implemented SWARM MCP package gives agents and operators ways to:

- assign or inspect work,
- exchange file-backed messages,
- persist shared knowledge,
- vote on proposals,
- detect duplicate/conflicting work,
- learn agent capabilities from task history,
- produce and verify work proofs,
- mine coordination patterns,
- expose coordination functions through CLI and MCP server adapters.

### Why the project exists

Derived from `README.md`, `swarm_mcp/__init__.py`, and `swarm_mcp/core/`: SWARM MCP exists to help multiple AI agents coordinate work without relying only on a human operator for task routing, conflict prevention, memory, decisions, and completion verification.

### Secondary domains

| Subdomain | Problem solved | Evidence |
|---|---|---|
| AgentTools/operator tooling | Exposes local automation, repo intelligence, docs/security helpers, and standalone MCP servers for operators and agents. | `mcp_servers/`, `tools/`, `tools_v2/`, `_ops/decisions/0001-agenttools-boundary.md` |
| Family Focus Board | Models family/business work as boards/cards plus shared Pomodoro sessions and realtime focus rooms. | `docs/mvp.md`, `apps/api/migrations/*.sql`, `packages/shared/src/timer/stateMachine.ts` |

---

## 3. Bounded contexts

### 3.1 SWARM MCP coordination context

**Primary code:** `swarm_mcp/core/`, `swarm_mcp/servers/`, `swarm_mcp/cli.py`

| Entity or value object | Type(s) | Responsibility | Persistence |
|---|---|---|---|
| Agent / Wolf | `WolfStatus`, `AgentProfile`, `TaskRecord` | Agent identity, status, capabilities, and task history. | `./wolf_den/`, `./swarm_dna/` |
| Task / Prey | `Prey`, `ScoredTask` | Work item representation, task assignment, and ROI/priority scoring. | Coordinator files and task server state; exact canonical task store is mixed with markdown task logs. |
| Message / Howl | `Howl`, `HowlUrgency`, `HowlType` | Agent-to-agent communication and broadcast messages. | `./pack_messages/{recipient}/incoming/*.json` |
| Message template | `MessageTemplateInput`, `MessageTemplateCategory` | Structured message rendering for system-to-agent, developer-to-agent, captain-to-agent, and agent-to-agent messages. | None; pure rendering. |
| Pack memory | `HuntingLore`, `HuntRecord` | Shared learnings and hunt records. | `./pack_memory/` |
| Swarm brain | `Learning`, `Decision` | Knowledge and decision records for MCP memory/brain surfaces. | `./swarm_brain/` and repository `swarm_brain/knowledge_base.json` |
| Proposal / Vote | `Proposal`, `Vote`, `VoteType`, `ConsensusRule` | Collective decision-making. | `./swarm_consensus/*.json` |
| Work intent / Conflict | `WorkIntent`, `Conflict`, `ConflictSeverity` | Duplicate-work and overlap detection. | `./swarm_conflicts/` |
| Work proof | `FileSnapshot`, `WorkCommitment`, `WorkProof` | Tamper-evident completion evidence from file hashes and git history. | `./swarm_proofs/` plus git state |
| Verification result | `VerificationType`, `VerificationResult` | Command, file, import, and page-fetch verification results. | Ephemeral unless caller persists output. |
| Coordination pattern | `CoordinationEvent`, `Pattern`, `Suggestion` | Pattern discovery and future coordination suggestions. | `./swarm_patterns/` |
| Failure event | `FailureEvent` | Recovery inputs and rollback/snapshot operations. | Ephemeral plus git/file side effects |

### 3.2 AgentTools/operator tooling context

**Primary code:** `mcp_servers/`, `tools/`, `tools_v2/`

| Entity or service | Type(s) or files | Responsibility | Current status |
|---|---|---|---|
| Standalone MCP server | `mcp_servers/*_server.py`, `mcp_servers/all_mcp_servers.json` | Local/operator MCP endpoints for git, docs, security, CI/CD, dependencies, observability, task manager, game/community tooling, and other automation. | 23 catalog entries; missing targets were fixed in SWARM-016. |
| Tool adapter | `IToolAdapter`, `ToolSpec`, `ToolRegistry` | In-process tool abstraction and registry for `tools_v2`. | Active but still in migration. |
| Disabled tool registry entry | `docs/TOOLS_V2_DISABLED_REGISTRY_ENTRIES.md` | Records adapters removed from active registry because they do not instantiate cleanly. | Active documentation for disabled entries. |
| Legacy toolbelt command | `tools/toolbelt_registry.py`, `tools/cli.py` | CLI and script dispatch used by CI and `swarm_mcp/servers/tools.py`. | Active/mixed; needs classification and false-positive cleanup. |
| Task-log mutation surface | `swarm_mcp/servers/tasks.py`, `mcp_servers/task_manager_server.py` | Reads or writes markdown task artifacts. | Contract is still risky: repo policy says `docs/root/MASTER_TASK_LOG.md` is SSOT; some code paths historically targeted root files or expected sections not present in the canonical SSOT. |

### 3.3 Family Focus Board context

**Primary code:** `apps/api/`, `apps/web/`, `packages/shared/`

| Entity or value object | Evidence | Responsibility |
|---|---|---|
| Org | `apps/api/migrations/0001_init.sql` | Workspace/account boundary. |
| User | `apps/api/migrations/0001_init.sql` | Member/owner within an org. |
| Board | `apps/api/migrations/0001_init.sql`, `apps/api/src/routes.ts` | Kanban board. |
| List | `apps/api/migrations/0001_init.sql`, `apps/api/src/routes.ts` | Ordered board column/list. |
| Card | `apps/api/migrations/0001_init.sql`, `apps/api/src/routes.ts` | Work item with title, description, due date, status, priority, links, assignees, tags, and checklist support. |
| FocusRoom | `apps/api/migrations/0001_init.sql`, `apps/api/src/routes.ts` | Board-scoped shared timer room with active card and timer state JSON. |
| PomodoroSession | `apps/api/migrations/0001_init.sql`, `packages/shared/src/timer/stateMachine.ts` | Timed focus/break session linked to org, board, card, user, and optionally a focus room. |
| ActivityLog | `apps/api/migrations/0001_init.sql`, `apps/api/src/activity.ts` | Audit trail for org/board/list/card/timer changes. |
| InventoryCategory / InventoryItem | `apps/api/migrations/0002_inventory.sql` | Inventory records in the same org boundary. |
| RoomTimerState | `packages/shared/src/timer/stateMachine.ts` | Timer state, transitions, derived remaining time, and session start/end effects. |

The Family Focus Board web UI wiring is **Unknown/Incomplete** from this repository. `apps/web` is currently scaffold-level.

---

## 4. Services

| Service | Code | Domain responsibility |
|---|---|---|
| `PackCoordinator` | `swarm_mcp/core/coordinator.py` | Orchestrates wolves/agents, readiness, task assignment, and broadcast coordination. |
| `MessageQueue` | `swarm_mcp/core/messaging.py` | Stores and retrieves messages for agents. |
| `PackMemory` | `swarm_mcp/core/memory.py` | Stores and searches shared lore/hunt records. |
| `SwarmBrain` | `swarm_mcp/core/brain.py` | Stores learnings and decisions for brain/memory surfaces. |
| `ConsensusEngine` | `swarm_mcp/core/consensus.py` | Creates proposals, records votes, and resolves decisions. |
| `ConflictDetector` | `swarm_mcp/core/conflict.py` | Tracks work intents and detects overlap. |
| `AgentDNA` | `swarm_mcp/core/agent_dna.py` | Records performance and recommends agents by category/files. |
| `WorkProofSystem` | `swarm_mcp/core/work_proof.py` | Captures file snapshots, commitments, proofs, and verification. |
| `VerificationHarness` | `swarm_mcp/core/verification.py` | Runs verification checks such as commands, imports, file existence, and page fetches. |
| `PatternMiner` | `swarm_mcp/core/pattern_miner.py` | Records coordination events and generates suggestions. |
| `RecoveryManager` | `swarm_mcp/core/recovery.py` | Supports backup, rollback, and failure recovery flows. |
| Fastify API routes | `apps/api/src/routes.ts` | Exposes FFB org, board, list, card, timer, session, activity, and inventory workflows. |
| Realtime events | `apps/api/src/realtime.ts` | Socket.IO room joins and board/timer event emission. |

---

## 5. Relationships

### SWARM MCP

```text
Agent/Wolf
  -> has AgentProfile and TaskRecord entries through AgentDNA
  -> receives Howl messages through MessageQueue
  -> may declare WorkIntent through ConflictDetector
  -> may be assigned Prey/Task through PackCoordinator
  -> may vote on Proposal through ConsensusEngine
  -> may produce WorkCommitment and WorkProof through WorkProofSystem
  -> contributes HuntingLore, HuntRecord, Learning, Decision, and CoordinationEvent records
```

### Family Focus Board

```text
Org
  -> has Users
  -> has Boards
Board
  -> has Lists
  -> has Cards
  -> has one FocusRoom per org/board pair
Card
  -> belongs to Board and List
  -> may have assignees, tags, checklists, links
  -> may have PomodoroSessions
FocusRoom
  -> points to active Card
  -> stores RoomTimerState
PomodoroSession
  -> belongs to Org, Board, Card, User, and optionally FocusRoom
ActivityLog
  -> records actions against entities
```

---

## 6. Data flow

### SWARM MCP package

```text
Human operator or AI agent
  -> `swarm` CLI or packaged MCP server
  -> `swarm_mcp.core` service
  -> file-backed JSON state, markdown task artifacts, and/or git state
  -> CLI/MCP response
```

### Standalone MCP/tooling

```text
MCP host or local operator
  -> `mcp_servers/*_server.py`
  -> `swarm_mcp.core`, `tools_v2`, `tools`, subprocesses, or local files
  -> filesystem, git, HTTP, CI/security/docs artifacts
  -> MCP response
```

### Family Focus Board

```text
Browser / API caller
  -> Fastify routes in `apps/api`
  -> PostgreSQL migrations/schema through `pg`
  -> Socket.IO realtime board/timer events
  -> shared timer transition code in `packages/shared`
```

The deployed runtime topology for any lane is **Unknown** from this repository.

---

## 7. User interactions

| Actor | Surface | Interactions evidenced in repo |
|---|---|---|
| AI agent | MCP servers | Send messages, search/store memory, inspect/control coordination, manage tasks, call tooling. |
| Human operator | `swarm` CLI | `status`, `send`, `inbox`, `search`, `learn`, `tasks`, `assign`, `vote`, `conflict`, `profile`, `prove`, `patterns`. |
| Maintainer/operator | `tools/cli.py`, `tools_v2`, standalone scripts | Security scan, import audit, docs generation, CI/CD helper, git operations, task and mission tooling. |
| Family Focus Board user | `apps/web` and `apps/api` | Intended board/card/timer flows are documented and partially implemented in API/shared code; web integration is incomplete. |

---

## 8. External integrations

| Integration | Evidence | Status |
|---|---|---|
| MCP protocol | `swarm_mcp/servers/`, `mcp_servers/`, `integration/` | Active. |
| PyPI | `pyproject.toml`, `.github/workflows/swarm_ci.yml`, release docs | Blocked for `0.6.0` because publish job lacks/does not receive `PYPI_API_TOKEN`. |
| GitHub Actions | `.github/workflows/swarm_ci.yml` | Active for Python tests, security/import scans, and tag publish. |
| Git | `work_proof.py`, `recovery.py`, git MCP servers | Active for work proof/recovery/tooling. |
| PostgreSQL | `apps/api/migrations/`, `apps/api/src/db/` | Required by Family Focus Board API. Deployment status unknown. |
| Socket.IO | `apps/api/src/realtime.ts` | Active in API code. |
| Discord | `tools/discord/`, Discord MCP/tool docs | Operational path is unclear; current live status Unknown. |
| WordPress/game-server tooling | `mcp_servers/website_manager_server.py`, `mod_deployment_server.py`, `server_monitoring_server.py`, `player_analytics_server.py` | Present but active production use Unknown. |
| DreamOS/DreamVault | `_ops/decisions/0001-agenttools-boundary.md`, `docs/repo_role_20260613.md` | External canonical owners referenced; runtime integration details Unknown. |

---

## 9. Feature-to-domain mapping

| Feature | Domain entity/service | Surface |
|---|---|---|
| Agent status and assignment | `PackCoordinator`, `WolfStatus`, `Prey` | `swarm` CLI, `swarm_mcp/servers/control.py`, task/control MCP surfaces |
| Agent messaging | `MessageQueue`, `Howl`, templates | CLI `send`/`inbox`, packaged and standalone messaging servers |
| Shared knowledge | `PackMemory`, `SwarmBrain`, `Learning`, `HuntingLore` | CLI `learn`/`search`, memory/brain MCP servers |
| Consensus voting | `ConsensusEngine`, `Proposal`, `Vote` | CLI `vote`, integration MCP bridge |
| Conflict prevention | `ConflictDetector`, `WorkIntent`, `Conflict` | CLI `conflict`, integration MCP bridge |
| Agent capability learning | `AgentDNA`, `AgentProfile`, `TaskRecord` | CLI `profile`, integration MCP bridge |
| Work verification | `WorkProofSystem`, `VerificationHarness` | CLI `prove`, task/git MCP tooling |
| Pattern suggestions | `PatternMiner`, `CoordinationEvent`, `Pattern`, `Suggestion` | CLI `patterns`, integration MCP bridge |
| Task ROI/scoring | `TaskScorer`, `ScoredTask` | Task server and internal scoring helpers |
| Recovery | `RecoveryManager`, `FailureEvent` | Task/recovery helper code; user-facing workflow partially documented |
| Tool execution | `ToolRegistry`, `ToolSpec`, legacy registries | `swarm_mcp/servers/tools.py`, `tools_v2`, `tools/cli.py` |
| Family board CRUD | Org, Board, List, Card, ActivityLog | `apps/api/src/routes.ts` |
| Pomodoro/focus room | FocusRoom, PomodoroSession, RoomTimerState | `apps/api`, `packages/shared` |
| Inventory records | InventoryCategory, InventoryItem | `apps/api/migrations/0002_inventory.sql`, API routes |

---

## 10. Architecture and folder audit

| Path | Role | Documentation state |
|---|---|---|
| `swarm_mcp/core/` | Coordination domain/application logic | Active; now reflected in this model. |
| `swarm_mcp/servers/` | Packaged MCP adapters | Active; 5 public package server modules. |
| `swarm_mcp/cli.py` | Operator CLI | Active; 12 subcommands. |
| `mcp_servers/` | Standalone/operator MCP scripts | Active/secondary; classification still needed for some domains. |
| `tools/` | Legacy and active automation scripts | Mixed; needs active/deprecated classification beyond explicit `tools/deprecated/`. |
| `tools_v2/` | Adapter registry migration | Active/in-progress; disabled entries documented. |
| `apps/api/` | FFB Fastify/Postgres API | Active product lane; needs tests/deployment docs. |
| `apps/web/` | FFB Next.js web app | Scaffold-level. |
| `packages/shared/` | FFB shared timer/types | Active and tested. |
| `docs/root/MASTER_TASK_LOG.md` | Execution status SSOT | Active canonical status. |
| `NEXT_UP.md` | Dashboard mirror | Active companion. |
| `MASTER_TASK_LIST.md` | Actionable task list | Active root deliverable; synchronized on 2026-07-03. |
| Historical planning/audit docs | `PROJECT_AUDIT_REPORT.md`, `PROJECT_STRUCTURE.md`, `docs/root/*`, older plans | Must be read with freshness banners and SSOT links. |

### Missing or incomplete documentation

- Clean deploy/runtime topology for the SWARM MCP MCP servers.
- Clean install proof for `swarm-mcp==0.6.0` after PyPI publish.
- Family Focus Board `.env.example`, deployment guide, API integration tests, and web/API wiring docs.
- Comprehensive classification of standalone MCP servers and legacy tool scripts.
- Canonical decision for `PackMemory` vs `SwarmBrain` precedence.
- Canonical operational status for Discord, WordPress, game-server, and external DreamOS/DreamVault integrations.

### Naming inconsistencies

| Area | Names observed | Current interpretation |
|---|---|---|
| Repository/product | SWARM MCP, AgentTools, Family Focus Board | Three lanes in one repository, not one product name. |
| Agent domain | agent, wolf, pack | Wolf/pack/prey/howl are SWARM MCP metaphors for agents/tasks/messages. |
| Task domain | task, prey, hunt, card | SWARM tasks and FFB cards are different domains. |
| Memory domain | PackMemory, SwarmBrain, knowledge base | Parallel memory surfaces; canonical precedence Unknown. |
| MCP surfaces | packaged servers vs standalone servers | Packaged servers ship with `swarm-mcp`; standalone servers are operator/local surfaces. |

---

## 11. Unknowns and constraints

The following are not determinable from the repository alone:

1. Which MCP servers are configured in live Cursor, Claude Desktop, or production hosts.
2. Whether Discord, WordPress, game-server, and mod-deployment surfaces are actively operated.
3. Whether Family Focus Board is intended to become release-critical or remain a separate scaffolded product lane.
4. Which memory system (`PackMemory`, `SwarmBrain`, or `swarm_brain/knowledge_base.json`) is canonical when records conflict.
5. Whether external DreamOS/DreamVault repositories currently consume these contracts.
6. Whether the actual GitHub repository description has been updated outside this branch. This repository can store the intended description in `docs/governance/github_description.md`; changing GitHub metadata requires a write-capable repository metadata operation.

---

## 12. Repository description

Recommended repository description:

> SWARM MCP / AgentTools is a mixed AI-agent coordination workspace: a Python `swarm-mcp` package for multi-agent coordination over MCP, plus local operator MCP/tooling surfaces and a separate Family Focus Board TypeScript product lane. It is for AI-agent operators and maintainers who need task coordination, messaging, shared memory, consensus, conflict detection, work proof, and repo automation.

If the hosted GitHub description must be updated, use the sentence above or the shorter form in `docs/governance/github_description.md`.
