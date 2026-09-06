# Toolbelt adapter follow-up

`agent_tools.repo` is the first consumer-facing Python API. The same primitives are intended to be exposed through the active AgentTools registry after the Python contract and ProjectScanner integration are verified.

That registry exposure is deliberately deferred from the first extraction so the foundational Git facts can be proven without coupling the ProjectScanner dependency lane to the legacy/v2 registry migration surface.

Planned registry names:

```text
repo.identity
repo.status
repo.branches
repo.compare
repo.worktrees
```

The adapters should remain thin wrappers over `agent_tools.repo`; they must not duplicate Git subprocess logic or add cleanup policy.
