# Broken Python Quarantine

These files were moved out of active runtime surfaces because syntax-load tests proved they are not currently executable.

Quarantined files:

- `migrate_managers.py` — `from __future__` import placement error
- `migrate_orchestrators.py` — `from __future__` import placement error
- `discord_web_test_automation.py` — indentation error

Policy:

- Do not import from this directory.
- Restore only after syntax/load tests pass.
- Prefer replacing codemod behavior with tested `tools_v2` or `swarm_mcp` flows.
