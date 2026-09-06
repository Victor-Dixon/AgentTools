# Repository Git Toolbelt v1 — VPS Proof

## Acceptance target

Validate the read-only `agent_tools.repo` primitives against the real managed ProjectScanner checkout on the Dream.OS VPS without mutating the checkout, installing packages, or relying on a development virtual environment.

## Proof captured 2026-09-06

```text
AGENTTOOLS_REPO_TOOLBELT=PASS
PROJECTSCANNER_CONSUMER_READY=YES
PRODUCTION_MUTATIONS=NO
INSTALLS_PERFORMED=NO
TEMP_SOURCE_REMOVED_ON_EXIT=YES
```

The disposable functional gate also proved:

```text
NESTED_REPO_AUTHORITY=PASS
BRANCH_INVENTORY=PASS
BRANCH_COMPARE=PASS
WORKTREE_INVENTORY=PASS
REPO_STATUS=PASS
DISPOSABLE_FUNCTIONAL_GATE=PASS
```

The real managed ProjectScanner checkout probe proved:

```text
NESTED_AUTHORITY_COLLAPSE=PASS
APP=/home/dreamos/dreamos-fleet/apps/projectscanner
HEAD=979c903d9288130c5e21ccad67988aaf2da0d671
CURRENT_BRANCH=DETACHED
DIRTY=0
UNTRACKED=0
LOCAL_BRANCHES=1
REMOTE_BRANCHES=7
WORKTREES=1
DETACHED_WORKTREES=1
DIRTY_WORKTREES=0
REAL_REPO_PROBE=PASS
```

## Interpretation

The managed ProjectScanner checkout is a clean exact-SHA detached runtime checkout, not an abandoned development worktree. `agent_tools.repo` reports the detached state as a fact and leaves its meaning to ProjectScanner/DreamVault.

The nested-authority proof is important: a path named `projectscanner` inside another Git worktree resolves to that worktree's real Git toplevel rather than being miscounted as a separate repository.

## Boundary

This proof authorizes the next integration step only: ProjectScanner may consume `agent_tools.repo` for generic Git facts. It does not authorize branch deletion, worktree pruning, promotion, or any other repository mutation.
