# PyPI First-Release Gate

Canonical distribution name: `we-are-swarm-agenttools`

Canonical import namespace: `swarm_mcp`

Public repository: `Victor-Dixon/AgentTools`

## Current truth

The corrected distribution name has no publicly discoverable PyPI project or release as of the 2026-08-29 verification pass. That is an availability signal, not proof of ownership.

PyPI can have a project name registered without any releases, so absence from search/results is not enough to prove that a name is reserved to this account. PyPI also no longer supports the old explicit pre-registration flow before upload.

A pending Trusted Publisher is useful for first publication, but PyPI's own documentation states that a pending publisher does not create the project or reserve the name until it is actually used to publish.

Therefore this repository must not claim that the PyPI name is reserved until an authenticated PyPI account action or successful first publication establishes ownership.

## Required technical preflight before first publication

The release candidate must pass all of the following from a clean GitHub-hosted environment:

1. build wheel and source distribution;
2. `twine check` on all artifacts;
3. install the built wheel into a fresh virtual environment, not the source checkout;
4. import `swarm_mcp` and `agent_tools` from that clean environment;
5. verify installed distribution metadata reports `we-are-swarm-agenttools`;
6. verify expected console entry points are present;
7. run `swarm --help` from the clean wheel install;
8. run `pip check`;
9. probe PyPI's public project endpoints and fail closed if a project/release already exists unexpectedly.

## Human/account gate

Before any production PyPI upload:

- log into the intended PyPI account;
- confirm the project identity is still usable from that authenticated account context;
- prefer a PyPI Trusted Publisher bound to `Victor-Dixon/AgentTools` and a dedicated GitHub `pypi` environment;
- require deliberate release authorization rather than treating an ordinary branch/tag push as permission to publish;
- publish only after the clean-wheel preflight is green on the exact release commit.

## External references

- PyPI help: https://pypi.org/help/
- Creating a PyPI project with a Trusted Publisher: https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/
- PyPI JSON API: https://docs.pypi.org/api/json/
- Python Packaging User Guide — PyPI migration/name registration: https://packaging.python.org/en/latest/guides/migrating-to-pypi-org/

## Non-claims

Until the account gate above is completed, the repository does **not** claim:

- PyPI ownership of `we-are-swarm-agenttools`;
- a published PyPI release;
- a verified `pip install we-are-swarm-agenttools` path from PyPI.

Source installation remains the supported public path.