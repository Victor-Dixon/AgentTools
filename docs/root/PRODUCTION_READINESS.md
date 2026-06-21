
## Current Security Audit Exception

As of the current Termux production-hardening pass:

- `npm audit --audit-level=high` has no high or critical blockers after upgrading `apps/web` to Next 16.
- `npm audit` reports 2 moderate advisories through Next's bundled PostCSS dependency.
- `npm audit fix --force` is intentionally not used because npm proposes a breaking/downgrade-style framework change.
- This exception is acceptable for baseline hardening but must be rechecked before public deployment.

