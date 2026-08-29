# WE ARE SWARM / AgentTools

**Multi-agent AI coordination and developer tooling for inspectable, testable engineering workflows.**

This repository contains the `swarm_mcp` Python package plus supporting AgentTools/operator tooling. The core package provides coordination primitives for agent messaging, shared memory, task assignment, consensus, conflict detection, capability profiling, work verification, and MCP-oriented integration.

## Package identity

The Python **import package** remains:

```python
import swarm_mcp
```

The repository distribution metadata is now named:

```text
we-are-swarm-agenttools
```

### Important PyPI note

Do **not** use:

```bash
pip install swarm-mcp
```

The `swarm-mcp` name on PyPI belongs to an unrelated Foursquare Swarm check-in MCP project. This repository is **not currently published to PyPI under its corrected distribution identity**, so installation should use the source repository until a verified release is published.

## Install from source

```bash
git clone https://github.com/Victor-Dixon/AgentTools.git
cd AgentTools
python -m venv .venv
```

Activate the environment, then install the project:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Verify the package and CLI:

```bash
python -c "import swarm_mcp; print('swarm_mcp import: PASS')"
swarm --help
```

## Verification

The repository CI installs the package in editable mode and runs the engineering gates used for the public project:

```bash
pytest tests/ -v
python tools/swarm/tests/check_import_healer_coverage.py
python tools/cli.py --security-scan
python tools/cli.py --audit-imports
```

See [`.github/workflows/swarm_ci.yml`](.github/workflows/swarm_ci.yml) for the current CI contract.

## Core capabilities

| Capability | Purpose |
| --- | --- |
| `PackCoordinator` | Agent assignment, availability, broadcast and coordination |
| `MessageQueue` | Asynchronous agent-to-agent messaging |
| `PackMemory` | Shared knowledge and persisted coordination context |
| `ConsensusEngine` | Multi-agent proposals and voting |
| `ConflictDetector` | Detect overlapping work before agents collide |
| `AgentDNA` | Track agent capability and historical performance signals |
| `WorkProofSystem` | Capture before/after evidence and tamper-evident work proof |
| `PatternMiner` | Record coordination outcomes and surface repeated patterns |
| `VerificationHarness` | Command/file/import/page verification helpers |
| `RecoveryManager` | Backup, rollback and recovery-oriented utilities |

## Minimal example

```python
from swarm_mcp import PackCoordinator, AgentDNA, ConsensusEngine

pack = PackCoordinator(wolves=["agent-1", "agent-2", "agent-3"])
ready = pack.get_ready_wolves()
pack.assign_hunt("agent-1", "Fix the authentication bug")

dna = AgentDNA()
best_agent, confidence = dna.find_best_agent(category="debugging")

consensus = ConsensusEngine()
proposal = consensus.propose(
    "agent-1",
    "Use PostgreSQL",
    "Need ACID transactions for this workload",
)
```

## CLI

After the editable install:

```bash
swarm status --agents agent-1,agent-2,agent-3
swarm send agent-1 agent-2 "Please review my PR"
swarm inbox agent-2 --unread
swarm tasks --path ./src
```

## MCP entry points

The package exposes MCP-oriented server commands through `pyproject.toml`:

```text
swarm-messaging-server
swarm-memory-server
swarm-tasks-server
swarm-control-server
swarm-tools-server
```

The underlying Python module paths are under `swarm_mcp.servers`.

## Repository scope

This checkout contains more than one lane:

- `swarm_mcp/` — core multi-agent coordination package
- `mcp_servers/`, `tools/`, `tools_v2/` — secondary operator/developer tooling
- `apps/`, `packages/` — separate Family Focus Board TypeScript product lane

The canonical architecture and lane boundary are documented in [`docs/architecture/DOMAIN_MODEL.md`](docs/architecture/DOMAIN_MODEL.md).

## Engineering posture

This project is intentionally presented with explicit maturity boundaries:

- implemented behavior is separated from planned or reconstructed behavior;
- CI/test evidence is preferred over unsupported completion claims;
- package publication is not claimed until a clean external install is verified;
- blockers remain visible instead of being hidden behind marketing language;
- unrelated repository lanes are documented rather than blended into one product claim.

## Current status

- Package code version: `0.6.0`
- Import namespace: `swarm_mcp`
- Distribution metadata: `we-are-swarm-agenttools`
- Public source repository: `Victor-Dixon/AgentTools`
- PyPI release under corrected identity: **not yet verified/published**
- Source installation: supported through editable install
- CI: pytest + import coverage + security scan + import audit

The previous `swarm-mcp` distribution name was invalid for this project because that PyPI name is already owned by an unrelated project. Publication should remain gated until the corrected distribution identity is explicitly reserved and a clean install is verified.

## Project documentation

- [`docs/architecture/DOMAIN_MODEL.md`](docs/architecture/DOMAIN_MODEL.md) — canonical domain model and repository boundary
- [`PRD.md`](PRD.md) — product requirements and scope
- [`ROADMAP.md`](ROADMAP.md) — roadmap
- [`MASTER_TASK_LIST.md`](MASTER_TASK_LIST.md) — strategic task inventory
- [`NEXT_UP.md`](NEXT_UP.md) — bounded immediate queue
- [`PRODUCTION_READINESS.md`](PRODUCTION_READINESS.md) — readiness boundary
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contributor guidance

## License

MIT. See [`LICENSE`](LICENSE).
