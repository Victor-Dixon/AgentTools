# NEXT UP - AgentTools

**Updated:** 2026-07-14
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`
**Scope:** Control-plane/toolbelt documentation and release-readiness execution

## Focus Queue

| Task ID | Objective | Target files | Dependency | Verification command | Completion evidence |
|---|---|---|---|---|---|
| SWARM-003 | Build and publish `swarm-mcp`, then record exact non-secret command output in the SSOT. | `pyproject.toml`, `dist/`, `docs/root/MASTER_TASK_LOG.md` | PyPI token availability from SWARM-002 | `python -m build`; `twine upload dist/*` | Output logged in `docs/root/MASTER_TASK_LOG.md` |
| SWARM-004 | Verify clean install/import/CLI smoke after publish. | clean environment, `docs/root/MASTER_TASK_LOG.md`, `NEXT_UP.md` | SWARM-003 complete | `pip install swarm-mcp`; `python -c "import swarm_mcp"`; `swarm --help` | Exact smoke output logged |
| AGENTTOOLS-MCP-001 | Classify active vs legacy MCP server surfaces. | `swarm_mcp/servers/`, `mcp_servers/`, `docs/architecture/DOMAIN_MODEL_DISCOVERY.md` | Current code inventory | `pytest -q tests/test_mcp_servers.py` | Classification table with keep/merge/archive/delete decisions |
| AGENTTOOLS-TV2-001 | Inventory `tools_v2` migration status and choose next adapter seam. | `tools_v2/`, `tools/`, `docs/architecture/CODE_INVENTORY.md` | Characterization tests first | `pytest -q tools_v2/tests tests/test_tools_v2_registry_contract.py` | Updated migration note and passing focused gate |
| AGENTTOOLS-DOCSYNC-001 | Keep root docs aligned with the SSOT and current implementation evidence. | `PRD.md`, `PROJECT_STRUCTURE.md`, `MASTER_TASK_LIST.md`, `NEXT_UP.md`, `docs/root/MASTER_TASK_LOG.md` | Live repo + ProjectScanner evidence | `git diff --check` | Documentation-only diff; no source/runtime behavior changes |

## Not Next

- Do not mark PyPI publish or clean install complete without command output.
- Do not delete or promote legacy tool/MCP surfaces without classification evidence.
- Do not modify existing dirty source/test/dependency paths during documentation-only repair.
