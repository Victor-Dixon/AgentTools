# Repository Git Toolbelt v1 — PR Notes

This branch is intentionally limited to deterministic, read-only Git facts.

## Included

- repository identity / Git toplevel resolution
- tracked-dirty vs untracked status facts
- local + remote branch inventory
- ahead / behind / ancestor comparison
- remote default branch fact from `<remote>/HEAD`
- worktree inventory including detached / locked / prunable / dirty facts
- disposable Git regression tests
- real VPS ProjectScanner acceptance proof

## Excluded

- branch deletion
- worktree prune/remove
- cleanup disposition
- PR/task ownership classification
- promotion/salvage policy
- ProjectScanner fleet interpretation
- DreamVault governance
- CPC mutation

## Consumer sequence

1. prove AgentTools primitives independently;
2. wire ProjectScanner hygiene prototype to `agent_tools.repo`;
3. prove schema parity / intentional deltas on the VPS;
4. merge only after explicit authorization.
