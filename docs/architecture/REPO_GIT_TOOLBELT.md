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

## v1 Python API

```python
from agent_tools.repo import (
    compare_refs,
    list_branches,
    list_worktrees,
    remote_default_branch,
    repo_identity,
    repo_status,
)
```

### `repo_identity(path)`

Returns repository toplevel, Git dir, HEAD, current branch, origin, and worktree membership.

### `repo_status(path)`

Returns raw porcelain status facts with tracked-dirty and untracked counts. It does not classify files as runtime, generated, source, archive, or policy material.

### `list_branches(path)`

Returns local branches and one remote's tracking branches with SHA, commit timestamp, and upstream facts. The symbolic `origin/HEAD` ref is not counted as a branch.

### `remote_default_branch(path)`

Returns the configured `<remote>/HEAD` target when present. It does not guess a fallback if the remote symbolic HEAD is unavailable.

### `compare_refs(path, base=..., head=...)`

Returns ahead/behind counts and whether `head` is already an ancestor of `base`.

### `list_worktrees(path)`

Parses `git worktree list --porcelain` and records path, HEAD, branch/detached state, locked/prunable flags, existence, and raw dirty counts.

## Registered toolbelt adapters

The `tools_v2` registry exposes thin wrappers over the Python contract:

```text
repo.identity   -> repo_identity()
repo.status     -> repo_status()
repo.branches   -> list_branches()
repo.compare    -> compare_refs()
repo.worktrees  -> list_worktrees()
```

These adapters live in `tools_v2.categories.repo_tools` and contain no independent Git implementation. They validate parameters, call `agent_tools.repo`, and normalize the result into `ToolResult`.

`remote_default_branch()` remains a Python-level helper in v1 because ProjectScanner consumes it while resolving canonical branch context; it can receive a registry adapter later if another operator-facing consumer needs it.

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

ProjectScanner's `projectscanner_fleet_hygiene_snapshot.v1` is the first consumer. Its private generic Git inspection helpers have been replaced by this API while ProjectScanner-specific dirty-path classification, canonical-branch interpretation, fleet signals, and snapshot schema remain in ProjectScanner.

## Verification

Focused regression targets:

```bash
python -m pytest \
  tests/test_repo_git_tools.py \
  tests/test_repo_tool_adapters.py \
  tests/test_repo_tool_registry.py \
  -q
```

The tests use disposable Git repositories and worktrees. No production repository mutation is required.

The real VPS proof is recorded in [`REPO_GIT_TOOLBELT_VPS_PROOF.md`](REPO_GIT_TOOLBELT_VPS_PROOF.md).
