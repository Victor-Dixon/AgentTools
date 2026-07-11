# Captain Governance Audit — 2026-07-07

**Agent:** Agent-4 (Captain)  
**D2A:** msg_20260707_215346  
**Verdict:** Governance is **paused**, not dead — captain coordination cadence lapsed after interim recovery closeout.

---

## Executive summary

Operator concern is valid: visible captain behavior (messaging agents, task assignment, weekly objective push, Discord status) dropped after **2026-07-06 interim recovery closeout**. Agent-4 shipped **verify/fix slices** (stop-hook SSOT, bus repair, VPS log diagnosis) but **under-indexed on fleet directives** — the core captain loop from protocol docs.

**Recommendation:** Do **not** replace Captain or spawn multiple captains. **Re-activate** the documented quad command model:

| Role | Agent | Responsibility |
|------|-------|----------------|
| Captain | Agent-4 | Weekly objective, fleet gas, verify chain, directive batches |
| Refresh Captain | Agent-1 | Stale status detection, quad all_ready trigger |
| Co-Captain | Agent-2 | Execute + directive batches when Captain idle |
| Infra | Agent-3 | VPS/Discord/deploy critical path |

---

## Sources reviewed (Swarm Brain + captain SSOT)

| Source | Path | Finding |
|--------|------|---------|
| Swarm Brain policy | `docs/governance/SWARM_BRAIN_POLICY.md` | **Advisory only** — does not override task YAML or policies |
| Captain weekly objective W27 | `data/planner/captain_weekly_objective_20260701_w27.json` | North star: Swarm Activation + Portfolio Consolidation |
| Interim captain protocol | `agent_workspaces/Agent-2/coordination/archive/.../captain_protocol.yaml` | 5-step cycle: assess → direct → execute → log → verify |
| Captain campaign log | `agent_workspaces/Agent-4/coordination/captain_campaign_log.json` | **TERMINAL_CLOSEOUT** 2026-07-06 — overnight recovery |
| Interim closeout | `data/reports/coordination/interim_recovery_captain_closeout_20260706.md` | Dual command plane caused confusion (Agent-1 JSONL vs Agent-2 batch) |
| Gas delivery doctrine | `runtime/policies/gas_delivery_doctrine_001.yaml` | Captain = heaviest PyAutoGUI user; A2A with artifact to wake partners |
| Quad lateral mode | `runtime/policies/quad_lateral_work_mode_001.yaml` | Gas on DONE; no empty ACK; no closeout between A2A |

**Swarm Brain captain log (historical):** salvage under `data/staging/portfolio_clones/Agent_Cellphone/.../swarm_brain/` — historical only. Live captain SSOT is **DreamVault** paths above.

---

## Fleet posture (now)

```
quad_group_onboard --status → 3/4 ready (Agent-1 NOT ready)
Agent-1: stop_hook 0/10, workspace 0/10, cycle 14 — DESYNC blocker
Agent-2: 10/10 cycle 8 ready — rollover pending
Agent-3: 10/10 cycle 8 ready — rollover pending  
Agent-4: 10/10 cycle 8 ready — rollover pending
fleet_brief: all 4 quiescent, cooldown_active=true
```

**Root cause of "governance dead" feeling:**
1. **Agent-1 gas desync** blocks quad 4/4 → no group onboard event
2. **VPS Discord !message** cannot PyAutoGUI to desktop (`vps_swarm_relay_001` not live)
3. **Captain post-recovery** focused on infra fixes vs daily directive batch
4. **status.json stale** on multiple agents until operator D2A refresh pings
5. **ACK loop** on closed lanes (discord_focus) consumed coordination bandwidth

---

## What captain MUST do daily (from protocol)

1. **Assess** — `quad_group_onboard_001.py --status` + `get_next_task` all 4 agents
2. **Direct** — A2A each non-ready/stale agent: TASK, ORDER, ARTIFACT, VERIFY, NEXT
3. **Execute own slice** — one shippable verify/fix per cycle
4. **Log** — append `captain_campaign_log.json` or coordination artifact per batch
5. **Verify + Discord** — `emit_agent_discord_status_001.py --live` on every D2A reply

**Forbidden:** empty ACK, closeout-as-A2A-reply, broadcast same lane to all agents, chat-only status updates.

---

## Weekly objective status (W27)

**Title:** Swarm Activation + Portfolio Consolidation  
**Agent lanes (from weekly objective):**
- Agent-1: GitHub consolidation / closeout system improvement
- Agent-2: Consolidation manifests + ML champion (operator-gated)
- Agent-3: Swarm tools live + VPS Discord fleet
- Agent-4: Coordinate quad, publish objective, unblock runtime

**Blocked operator gates:** Discord fleet tokens, MLRobotmaker repo, Weghachi Docker

---

## Actions taken this session (Captain re-activation)

1. This governance audit devlog
2. Captain directive batch A2A → Agent-1 (P0 quad unblock), Agent-2, Agent-3
3. Fleet brief refresh evidence: `agent_workspaces/Agent-4/coordination/fleet_brief_latest.json`

---

## Answer: new captain or multiple captains?

**No.** Structure exists; execution cadence lapsed.

- **One Captain** (Agent-4) for verify + weekly objective + directive batches
- **Agent-1** refresh captain when Captain is in verify slice
- **Agent-2** co-captain executes when Captain idle >30m
- Adding captains without SSOT → repeats 2026-07-06 dual command plane failure

---

## Next 24h captain priorities

| P | Owner | Action |
|---|-------|--------|
| P0 | Agent-1 | Reconcile cycle 14 gas 0/10 → execute synthesize slice → quad 4/4 |
| P0 | Operator | VPS token refresh + Windows `message_bus_queue_processor` running |
| P1 | Agent-2 | Cycle 9 rollover + `vps_swarm_relay_001` design slice |
| P1 | Agent-3 | Cycle rollover + Discord D2A reply on every intake |
| P1 | Agent-4 | Daily directive batch + refresh W27 objective publish |

**Verify:** `python runtime/scripts/quad_group_onboard_001.py --status` → 4/4 ready

---

*Artifact:* `agent_workspaces/Agent-4/coordination/d2a_msg_20260707_215346_captain_governance_audit.json`
