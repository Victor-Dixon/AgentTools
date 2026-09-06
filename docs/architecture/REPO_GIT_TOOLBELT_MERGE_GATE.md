# Merge gate

```text
MERGE_AUTHORIZED=NO
```

Required before merge:

1. AgentTools CI green on the feature branch/PR.
2. ProjectScanner consumer refactor green against the pinned AgentTools commit.
3. VPS parity proof records any intentional branch-count semantic change.
4. Explicit merge authorization.
