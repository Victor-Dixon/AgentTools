# Repository Git Toolbelt v1 — VPS Proof

## Acceptance target

Validate the read-only `agent_tools.repo` primitives and their ProjectScanner consumer against the real managed ProjectScanner checkout on the Dream.OS VPS without mutating the checkout, installing packages, or relying on a development virtual environment.

## Managed authority

```text
APP=/home/dreamos/dreamos-fleet/apps/projectscanner
HEAD=979c903d9288130c5e21ccad67988aaf2da0d671
CURRENT_BRANCH=DETACHED
DIRTY=0
UNTRACKED=0
WORKTREES=1
DETACHED_WORKTREES=1
DIRTY_WORKTREES=0
```

The managed ProjectScanner checkout is a clean exact-SHA detached runtime checkout, not an abandoned development worktree.

## Primitive acceptance

The disposable functional gate proved:

```text
NESTED_REPO_AUTHORITY=PASS
BRANCH_INVENTORY=PASS
BRANCH_COMPARE=PASS
WORKTREE_INVENTORY=PASS
REPO_STATUS=PASS
DISPOSABLE_FUNCTIONAL_GATE=PASS
```

The real managed checkout probe proved:

```text
NESTED_AUTHORITY_COLLAPSE=PASS
REAL_REPO_PROBE=PASS
AGENTTOOLS_REPO_TOOLBELT=PASS
PROJECTSCANNER_CONSUMER_READY=YES
```

## Final three-way parity

The final gate compared raw Git output, AgentTools facts, and ProjectScanner's hygiene snapshot using the same real checkout.

```text
RAW_REMOTE_REFS_TOTAL=8
RAW_REAL_REMOTE_BRANCHES=7
RAW_ORIGIN_HEAD_PRESENT=TRUE

AGENTTOOLS_REMOTE_BRANCHES=7
PROJECTSCANNER_REMOTE_BRANCHES=7

RAW_WORKTREES=1
AGENTTOOLS_WORKTREES=1
PROJECTSCANNER_WORKTREES=1

RAW_DETACHED_WORKTREES=1
AGENTTOOLS_DETACHED_WORKTREES=1
PROJECTSCANNER_DETACHED_WORKTREES=1

AGENTTOOLS_DIRTY_WORKTREES=0
PROJECTSCANNER_DIRTY_WORKTREES=0

RAW_TO_AGENTTOOLS_PARITY=PASS
AGENTTOOLS_TO_PROJECTSCANNER_PARITY=PASS
WORKTREE_PARITY=PASS
HEAD_PARITY=PASS
READ_ONLY_ASSERTION=PASS
ORIGIN_HEAD_EXCLUSION=CONFIRMED
```

## Semantic correction

The original ProjectScanner prototype reported eight remote refs because the raw inventory included the symbolic `refs/remotes/origin/HEAD` entry. The shared AgentTools contract excludes that symbolic signpost from the branch count while exposing the default-branch fact separately.

```text
old prototype remote count = 8 refs
real remote branch count   = 7 branches
origin/HEAD                 = metadata, not a branch
```

This is an intentional evidence correction, not a loss of repository data.

## Authority-collapse proof

A nested path named `projectscanner` inside another repository resolves to the actual Git toplevel before inspection. This prevents directory-name matches from being misreported as separate repository authorities.

## Safety closeout

```text
PRODUCTION_MUTATIONS=NO
INSTALLS_PERFORMED=NO
TEMP_SOURCES_REMOVED_ON_EXIT=YES
MERGE_AUTHORIZED=NO
```

This proof authorizes the shared read-only contract and its thin registry adapters. It does not authorize branch deletion, worktree pruning, promotion, or any other repository mutation.
