# Agent Cellphone Tool

Curated Agent Cellphone tooling for AgentTools.

## Decision

Agent_Cellphone and Agent_Cellphone_V2_Repository are not merged directly into AgentTools root.

This path is the canonical destination for reusable operator/device-control functions extracted from those repositories.

## Policy

- No raw root merge.
- No destructive pruning.
- No public release until secret scan passes.
- Preserve source repo SHAs and file manifests.
- Extract small, testable CLI surfaces only.
