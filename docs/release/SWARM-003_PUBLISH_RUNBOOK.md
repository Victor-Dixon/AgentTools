# SWARM-003 — PyPI Publish Runbook

**Task ID:** SWARM-003
**Last Updated:** 2026-06-29
**Status:** Blocked pending `PYPI_API_TOKEN` GitHub secret

---

## Current state

- Package version: `0.6.0`
- Release tag: `v0.6.0` (pushed)
- CI build/test: **passed** on tag `v0.6.0` (run `28408184056`)
- CI publish: **failed** — `TWINE_PASSWORD` empty (`PYPI_API_TOKEN` secret not configured in `Victor-Dixon/AgentTools`)

---

## Maintainer unblock (one-time)

1. Create or confirm PyPI project-scoped token for `swarm-mcp` (see `SWARM-002_PYPI_TOKEN_RUNBOOK.md`).
2. Add GitHub repository secret:
   - Name: `PYPI_API_TOKEN`
   - Value: PyPI token (starts with `pypi-`)
3. Re-run publish by pushing the tag again or re-running the failed workflow job:

```bash
git fetch --tags
git push origin v0.6.0 --force  # only if tag exists; otherwise create tag on master HEAD
```

Or in GitHub UI: Actions → failed `v0.6.0` run → Re-run failed jobs.

---

## Local publish (alternative)

```bash
export PYPI_API_TOKEN='pypi-***'  # never commit
python -m pip install 'build>=1.0' 'twine>=6.0'
python -m build
python -m twine check dist/*
python -m twine upload -u __token__ -p "$PYPI_API_TOKEN" dist/*
```

Record redacted output in `docs/root/MASTER_TASK_LOG.md`.

---

## SWARM-004 verification (after upload)

```bash
rm -rf /tmp/swarm-verify
python3 -m pip install --target /tmp/swarm-verify --no-cache-dir swarm-mcp==0.6.0
cd /tmp
PYTHONPATH=/tmp/swarm-verify python3 -c "from swarm_mcp.cli import main; print('import_ok')"
PYTHONPATH=/tmp/swarm-verify python3 -m swarm_mcp.cli status
```

Expected: `swarm` / `swarm_mcp.cli` entry points present (not `swarm_mcp.server` only).
