# Repository Git Toolbelt v1

## Purpose

`agent_tools.repo` is the small, dependency-light Git inspection surface for Dream.OS consumers.

It exists so repositories such as ProjectScanner do not grow private copies of generic Git plumbing.

## Ownership boundary

AgentTools owns **how to inspect Git state**.

ProjectScanner owns **how repository facts are combined into fleet intelligence**.

DreamVault owns **durable governance decisions and policy**.

CPC owns **authorized mutation and enforcement**.

```text
agent_tools.repo
    -> deterministic Git facts
ProjectScanner
    -> aggregation + hygiene signals
DreamVault
    -> policy / disposition
CPC
    -> mutation
```

## v1 API

```python
from agent_tools.repo import (
    compare_refs,
    list_branches,
    list_worktrees,
    repo_identity,
    repo_status,
)
```

### `repo_identity(path)`

Returns repository toplevel, Git dir, HEAD, current branch, origin, and worktree membership.

### `repo_status(path)`

Returns raw porcelain status facts with tracked-dirty and untracked counts. It does not classify files as runtime, generated, source, archive, or policy material.

### `list_branches(path)`

Returns local branches and one remote's tracking branches with SHA, commit timestamp, and upstream facts.

### `compare_refs(path, base=..., head=...)`

Returns ahead/behind counts and whether `head` is already an ancestor of `base`.

### `list_worktrees(path)`

Parses `git worktree list --porcelain` and records path, HEAD, branch/detached state, locked/prunable flags, existence, and raw dirty counts.

## Safety contract

The v1 module is read-only. It does not call:

- `git branch -D`
- `git push --delete`
- `git worktree remove`
- `git worktree prune`
- `git reset`
- `git checkout`
- `git switch`
- `git clean`

It also does not infer `DELETE_SAFE`, `SALVAGE`, `PR_OWNED`, or any other lifecycle decision. Those are downstream intelligence/governance concerns.

## First consumer

ProjectScanner's `projectscanner_fleet_hygiene_snapshot.v1` prototype is the first intended consumer. The migration should replace its private Git inspection helpers with this API while leaving ProjectScanner-specific dirty-path classification, canonical-branch interpretation, fleet signals, and snapshot schema in ProjectScanner.

## Verification

Focused regression target:

```bash
python -m pytest tests/test_repo_git_tools.py -q
```

The tests use disposable Git repositories and worktrees. No production repository mutation is required.
