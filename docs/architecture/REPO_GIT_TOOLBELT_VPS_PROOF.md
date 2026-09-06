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

Three-way parity then proved raw Git, AgentTools, and ProjectScanner agree on the managed checkout:

```text
RAW_REMOTE_REFS_TOTAL=8
RAW_REAL_REMOTE_BRANCHES=7
RAW_ORIGIN_HEAD_PRESENT=TRUE
AGENTTOOLS_REMOTE_BRANCHES=7
PROJECTSCANNER_REMOTE_BRANCHES=7
RAW_TO_AGENTTOOLS_PARITY=PASS
AGENTTOOLS_TO_PROJECTSCANNER_PARITY=PASS
WORKTREE_PARITY=PASS
HEAD_PARITY=PASS
READ_ONLY_ASSERTION=PASS
ORIGIN_HEAD_EXCLUSION=CONFIRMED
```

The raw ref count of 8 includes symbolic `origin/HEAD`; the real remote branch count is 7.

## Registry dependency-isolation finding

The first VPS ToolRegistry probe exposed a real packaging boundary defect:

```text
ModuleNotFoundError: No module named 'requests'
```

The failure occurred before repository tool resolution because importing `tools_v2.tool_registry` eagerly imported unrelated advisor/category modules, and `tools_v2.categories` eagerly imported `communication_tools`, which requires optional `requests`.

The fix makes `tools_v2` and `tools_v2.categories` lazy namespaces. Registry-only consumers no longer import unrelated optional tool categories. A regression test deliberately blocks `requests` while resolving all five repository tools.

```text
AgentTools Swarm CI #47=PASS
AgentTools Swarm CI #48=PASS
```

The final VPS registry execution probe remains the acceptance gate for the registered adapter surface.

## Interpretation

The managed ProjectScanner checkout is a clean exact-SHA detached runtime checkout, not an abandoned development worktree. `agent_tools.repo` reports the detached state as a fact and leaves its meaning to ProjectScanner/DreamVault.

The nested-authority proof is important: a path named `projectscanner` inside another Git worktree resolves to that worktree's real Git toplevel rather than being miscounted as a separate repository.

## Boundary

This proof authorizes the ProjectScanner consumer relationship and the registered read-only repo toolbelt surface. It does not authorize branch deletion, worktree pruning, promotion, merging, or any other repository mutation.
