# SWARM-002 — PyPI Account/Token Secure Storage Runbook

**Task ID:** SWARM-002  
**Last Updated:** 2026-05-17  
**Status:** Completed per `docs/root/MASTER_TASK_LOG.md`; retained as secure-storage reference

---

## Purpose

Provide a secure, reproducible process to:
1. Confirm the publishing PyPI account owner.
2. Create a scoped API token for `swarm-mcp`.
3. Store the token safely for local publishing and CI publishing.

This runbook intentionally excludes raw secrets from logs/docs.

---

## Required maintainer actions (completed 2026-03-24 per SSOT)

1. Sign in to `https://pypi.org` with the intended publisher account.
2. Confirm account identity (username + email) in account settings.
3. Create a **project-scoped token** for project `swarm-mcp`:
   - token name suggestion: `swarm-mcp-release`
   - scope: **project** (preferred) instead of account-wide.
4. Copy the token one time and place it in secure storage (local + CI).
5. Record non-secret evidence back into `docs/root/MASTER_TASK_LOG.md`.

---

## Secure storage standard

### Local publish (recommended)

Use environment variable injection at runtime (do not commit token):

```bash
export PYPI_API_TOKEN='pypi-***'
python -m twine upload -u __token__ -p "$PYPI_API_TOKEN" dist/*
```

### CI publish (GitHub Actions)

Store token as repository/org secret:
- Secret name: `PYPI_API_TOKEN`
- Usage in workflow: pass as `TWINE_PASSWORD` with `TWINE_USERNAME=__token__`

Example step:

```yaml
- name: Publish to PyPI
  env:
    TWINE_USERNAME: __token__
    TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
  run: python -m twine upload dist/*
```

### What is forbidden

- Never commit token values to git.
- Never paste token values into issue/PR comments.
- Never store token in plaintext project files (e.g., `.env` committed to repo).

---

## Evidence template (non-secret)

Use this template only if token ownership/storage is rotated in the future:

- **Execution date (UTC):** `YYYY-MM-DD`
- **PyPI account username:** `<username>`
- **Token scope:** `project: swarm-mcp`
- **Local storage method used:** `runtime env var` / `OS keychain wrapper` / equivalent
- **CI secret configured:** `yes/no` (`PYPI_API_TOKEN`)
- **Evidence note:** `token created and stored; value redacted`

---

## Ready-to-send prompt for Codex agent (SWARM-003 handoff)

```text
Proceed with SWARM-003. Use docs/root/MASTER_TASK_LOG.md as SSOT.
1) Run: python -m build
2) Run: python -m twine upload dist/*
3) Record exact command output (redact secrets) in docs/root/MASTER_TASK_LOG.md under a dated SWARM-003 evidence block.
4) Update NEXT_UP.md to mirror SSOT progress and remaining blocker state.
Do not change task ordering; SWARM-004 remains next after SWARM-003.
```
