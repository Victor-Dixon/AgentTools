# Dream.OS Control Plane — V1 (`dream_control`)

`dream_control` is the continuity and control-plane **client** for Dream.OS.
Its human-facing entry point is one command:

    passdown

It is deliberately *not* a second orchestration system, and *not* a prompt
generator. It reconstructs a continuation packet from the systems that already
own the truth, so any new agent — on Termux, a VPS, Windows, Claude, ChatGPT, or
a local model — can continue safely.

## Where responsibility lives

Mapped from `DreamVault/governance/canonical_authority_registry.yaml` and
`DreamVault/data/registry/repo_governance.yaml`, not invented here:

| Pillar | Repository | Owns |
|---|---|---|
| Authority / governance / durable intent | `DreamVault` | canonical owners, lanes, policies, planner, preservation doctrine, CPC toolchain |
| Discovery / portfolio intelligence | `projectscanner` | what already exists: repos, branches, implementations, duplicates, salvage candidates |
| Reusable execution primitives | `AgentTools` | MCP servers, messaging, memory, control, toolbelt CLIs |
| Durable control-plane service (dreamosd) | `dreamos-brain` | FastAPI + SQLite event/task/project/closeout store, VPS deployment |
| Continuity / context projection | `AgentTools/dream_control` (this) | passdown, agent registry, lane ownership, local event log, policy gates |

`dream_control` lives in AgentTools because the governance registry names
AgentTools the canonical owner of `operator_tooling` ("operator control plane").
It **reads** DreamVault and ProjectScanner artifacts; it never forks them.

### What this explicitly does not do

- It does not scan. `dreamscan` shells out to the real `projectscanner` CLI.
- It does not re-implement AgentTools helpers. It reports which surfaces are
  reachable and directs the receiving agent to them.
- It does not own governance. Canonical ownership comes from DreamVault.
- It does not become the database. `dreamos-brain` is dreamosd; every event
  here already serialises to that service's `POST /events` shape
  (`Event.to_brain_payload`), so migration is a transport change.

## Data flow

```
        projectscanner                DreamVault
      (discovery evidence)      (intent + authority + CPC)
                \                        /
                 \                      /
   AgentTools ---> dream_control (this) <--- live GitHub (gh)
   (toolbelt)             |    |                  authority
                          |    +---------------- dreamos VPS (read-only SSH)
                          v
                 ~/.dreamos/control  --sync-->  dreamos-brain (dreamosd)
                          |
                       passdown
                          |
                     next agent
```

## V1 layout

    ~/.dreamos/control/
        config/{operator,environments,policies}.json
        state/{agents,active_lanes,capabilities,repositories}.json
        events/events.jsonl
        cache/{github,projectscanner,vps,brain_sync}.json
        handoff/{latest.md,latest.json}

Override the root with `DREAMOS_CONTROL_HOME`.

## Commands

| Command | Purpose |
|---|---|
| `passdown` | build the handoff, write it, copy it to the clipboard, record `passdown_generated` |
| `passdown show` | reprint the last handoff without recollecting |
| `passdown selftest` | prove every source is reachable or explicitly accounted for |
| `dreamstate [section]` | dump agents / lanes / capabilities / repositories / event sync |
| `dreamevent <type> …` | record an event; `--list` to read; `--sync` to push to dreamosd |
| `agentstart` / `agentstatus` / `dreamagents` | register, update, and list fleet agents |
| `dreamlane claim\|release\|complete\|list` | lane ownership, with conflict detection |
| `dreamscan [path]` | delegate to the ProjectScanner CLI |
| `dreamcap check "<capability>"` | duplication gate (exit 3 = NOT_AUTHORIZED) |
| `dreamctl policy branch\|publish\|plan` | inspect a policy decision directly |

All shims dispatch to `dream_control.cli:main`, which also reads `argv[0]`, so
`passdown` and `dreamctl passdown` are the same code path.

## Policy gates

- **Preservation.** `feat/captain-governance-mvp-001` (HOLD_SALVAGE_ARCHAEOLOGY),
  `polish/product-surface-001` (HOLD_FORENSIC), and
  `reconcile/k2-last-copy-salvage-001` (HOLD_PRESERVE) are not stale branches.
  `cleanup_allowed()` returns `False` for them and for any hold added to
  `config/policies.json`. A dirty worktree is likewise never auto-cleanable.
- **Duplication.** Before creating a capability, `dreamcap check` merges
  ProjectScanner evidence, DreamVault canonical ownership, and AgentTools
  surfaces. An existing implementation yields `DUPLICATE_IMPLEMENTATION_RISK`
  and `NOT_AUTHORIZED`. When ProjectScanner evidence is unavailable the packet
  says so — absence is never treated as proof of absence.
- **Publishing.** Internal recording (`local_capture`, `control_plane_event`,
  `cockpit_feed`) is on. `discord_publish`, `slack_publish`, and `x_publish`
  default to **off**; a CPC capture never implies a public post. Per-run opt-in
  is `DREAMOS_PUBLISH_DISCORD=1`.

## VPS

The VPS (`dreamos@2.25.64.233`) is a runtime node, not an SSH destination. The
collector is strictly read-only: hostname, runner process, runner registration
files, dreamosd process/systemd state, repo checkouts, uptime. It never
re-registers or restarts `dreamvault-vps-01`. Runner persistence is currently
reported as `temporary_nohup_or_unknown` until a systemd unit lands — that
remains a separate lane.

Once `DREAMOS_BRAIN_URL` points at the dreamos-brain deployment, `dreamevent
--sync` pushes the local log to the service and passdown reads control-plane
health over HTTP instead of SSH.

## Install

    python3 scripts/install_dream_control.py

Discovery runs first (DreamVault, ProjectScanner, AgentTools, CPC/cliprun, gh,
SSH key, VPS reachability); only missing pieces are created. Existing config is
preserved unless `--force`. Shims are installed to `~/bin` and a selftest runs
last. `--no-vps-probe` for offline installs.

## Acceptance tests

`tests/test_dream_control.py` covers the V1 criteria: cold-start passdown (1),
live-not-replayed authority (2), cross-agent visibility (3), duplication
detection (4), AgentTools redirection (5), unhealthy runner surfacing as a
blocker (6), preservation holds (7), and internal capture without Discord
publishing (8).

    python3 -m pytest tests/test_dream_control.py -q
