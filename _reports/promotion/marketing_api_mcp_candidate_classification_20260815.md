# AgentTools marketing/API/MCP promotion candidate classification

Date: 2026-08-15
Lane: `verify-marketing-api-mcp-promotion-candidates`
Scope: bounded classification only; no capability movement, credentials, external posting, or planner rewrite.

## Evidence reviewed

- `NEXT_UP.md` and `MASTER_TASK_LIST.md` require provenance, auth/risk review, deduplication, narrow verification, and a promotion manifest before any capability is promoted.
- `integration/swarm_mcp_server.py` is an existing generic AgentTools MCP surface for consensus, conflict checks, agent profiles, work commitments/proofs, and pattern suggestions. It is not a social publishing implementation.
- Indexed AgentTools search found no direct Twitter, Instagram, LinkedIn, Facebook, TikTok, or generic social-publishing implementation matching the promotion lane.
- `Victor-Dixon/socialmediamanager/NEXT_UP.md` explicitly keeps operator approval mandatory, preview-first behavior default, and social execution in that repository. Its active lane is currently verifying those boundaries and deciding which proven capabilities may later be proposed for reusable promotion.

## Candidate classifications

| Candidate | Classification | Ownership | Provenance | Auth / risk | Deduplication decision | Narrow verification required before promotion |
|---|---|---|---|---|---|---|
| Direct social publishing / platform posting | `REJECTED` for AgentTools ownership | `socialmediamanager` | Current social repo planning contract | Platform credentials + external side effects; approval required | Do not duplicate in AgentTools | social repo must independently prove preview/approval and posting boundaries |
| Approval / preview / queue state machine | `DUPLICATE` if copied into AgentTools | `socialmediamanager` | Current social repo planning contract | Consequential-action gate | Keep implementation in owning repo; expose only a proven reusable contract later | deterministic no-live-post tests + approval refusal tests |
| Generic MCP transport / tool registration pattern | `EXISTING` | AgentTools | `integration/swarm_mcp_server.py` and MCP planning assets | Local tool invocation; each promoted tool still needs its own auth/risk model | Reuse transport pattern; do not import social executor | local initialize + one non-consequential tool-call smoke test |
| Generic capability descriptor / promotion manifest schema | `PROMOTION_CANDIDATE` | AgentTools | Required by AgentTools planning contract; no social executor required | Must record auth model, side effects, owner, provenance, tests | Canonical reusable metadata layer; references owning implementation instead of copying it | schema/fixture validation before use by another repo |
| Social analytics/content-generation interfaces | `UNKNOWN` | likely socialmediamanager unless proven otherwise | Current evidence does not establish a stable reusable interface | May require platform data credentials and terms review | No promotion until interface and consumer are evidenced | identify concrete source path + consumer + credential boundary + deterministic fixture |
| SWARM consensus/work-proof MCP functions | `EXISTING`, not a marketing candidate | AgentTools | `integration/swarm_mcp_server.py` | No marketing-platform auth evidenced | Keep separate from social execution | existing/local MCP verification only; no marketing promotion claim |

## Promotion decision

No social executor should be promoted into AgentTools in this lane.

The only bounded reusable candidate supported by current evidence is a **capability-descriptor / promotion-manifest contract** that records provenance, owner, authentication model, side effects, approval requirement, tests, and consumer references while leaving execution code in its canonical repository.

## Required follow-up before any code promotion

1. Wait for `socialmediamanager` to finish its current preview/approval boundary verification.
2. Require the social repo to nominate a specific proven reusable interface; do not infer one from file names or historical claims.
3. For each nominated interface, record source commit/path, owning repo, consumers, credential model, external side effects, approval/rate-limit requirements, and deterministic test evidence.
4. Only then implement or adopt a small manifest schema in AgentTools and validate it with a non-consequential fixture.

## Closure

This report closes the **classification** portion of the current AgentTools promotion-candidate audit without changing execution ownership. It deliberately leaves promotion itself open until the owning social repository provides verified reusable evidence.
