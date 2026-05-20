# Dependencies

## Runtime

AgentTools is primarily Python-based and uses standard-library-first tooling where possible.

## Development / Verification

Expected local verification tools:

- Python 3
- pytest
- git

## Optional Integration Dependencies

Some tools may require external credentials or services depending on the lane:

- Discord webhook/API credentials
- GitHub CLI or GitHub token
- MCP-compatible clients/servers

## Dependency Policy

- Keep core governance and verification scripts lightweight.
- Prefer standard library for repo audits and operator checkpoints.
- Isolate optional service integrations behind explicit tools, tests, and redacted config.
