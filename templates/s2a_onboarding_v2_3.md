# S2A ONBOARDING (SOFT) — v2.3 (FORCE-MULTIPLIER GATE + ONE-SCREEN LOOP)

## Evolution Summary
- **v2.2**: Rehydrate → Resume (eliminated checklists)
- **v2.3**: Force-Multiplier Gate + One-Screen Loop (eliminated cycle planning)

## Core Rule (Non-Negotiable)
> If the Force-Multiplier Gate passes, execution begins immediately.
> If it fails, exactly one blocker is produced — no partial execution.

## 1. Force-Multiplier Gate (Single Deterministic Decision)

### Gate Command
```bash
python tools/force_multiplier_gate.py --agent {AGENT_ID}
```

### Gate Questions (Evaluated Automatically)
```yaml
force_multiplier_gate:
  task_scope:
    single_cycle: true
    cross_domain: false
  ownership:
    files_owned: true
    no_shared_conflict: true
  execution:
    next_action_executable: true
    tools_available: true
  alignment:
    git_sha_valid: true
    cycle_valid: true
```

### Outcomes
- **Exit Code 0**: `GATE PASS — EXECUTE` → proceed to execution loop
- **Exit Code 1**: `GATE FAIL — BLOCKER: <reason>` → record blocker, escalate, stop

### Gate Inputs (Auto-Derived)
Pulled from `rehydration.json`, `status.json`, git HEAD, inbox (only if referenced).

## 2. One-Screen Execution Loop (Replaces All Cycle Checklists)

### Execution Loop (Canonical)
```
RUN next_action.command
↓
VALIDATE expected_outcome
↓
UPDATE rehydration.json
↓
IF next_action exists → LOOP
ELSE → TRANSITION TO CLOSURE
```

### Loop Rules
- **No planning phase**: Execute immediately
- **Single validation**: Check expected_output pattern
- **Atomic updates**: Update rehydration.json after each step
- **Auto-termination**: When no next_action remains, enter closure
- **No user intervention**: Fully automated until completion or blocker

### Success Criteria
- Each command produces expected output
- Rehydration snapshot stays synchronized
- No external dependencies violated

## 3. S2A Onboarding v2.3 Message Format

### Ultra-Compressed Message Structure
```md
# [HEADER] S2A ONBOARDING (SOFT) — v2.3 SSOT (FORCE-MULTIPLIER GATE + ONE-SCREEN LOOP)
# 🟢 SINGLE SOURCE OF TRUTH - Current canonical onboarding template

## 1. LOAD STATE
cat agent_workspaces/{AGENT_ID}/rehydration.json

## 2. EVALUATE GATE
python tools/force_multiplier_gate.py --agent {AGENT_ID}

## 3. AI COORDINATION ANALYSIS (MANDATORY)
```bash
# Analyze task for coordination requirements
mcp --server ai-orchestration analyze_task --task-description "[task from rehydration.json]"
```

## 4. EXECUTE OR BLOCK
IF gate_pass AND ai_analysis_recommends_execution:
  RUN next_action.command (from rehydration.json)
  VALIDATE expected_output
  UPDATE rehydration.json
  LOOP until no next_action
ELSE:
  RECORD blocker (gate failure or AI coordination recommendation)
  ESCALATE with AI analysis results
  STOP
```

### Message Rules
- **Maximum 15 lines** total
- **Zero checklists** - everything derived from rehydration.json
- **Binary outcomes** - execute immediately or block with one reason
- **No re-planning** - state is pre-determined and validated

## 4. Execution Automation Tool

### `tools/one_screen_execution_loop.py`
```bash
python tools/one_screen_execution_loop.py --agent {AGENT_ID}
```

**Behavior:**
1. Load rehydration.json
2. Run force_multiplier_gate.py
3. If pass: execute loop until completion
4. If fail: emit blocker and exit
5. Update closure template on completion

**Exit Codes:**
- `0`: Loop completed successfully → ready for closure
- `1`: Blocker encountered → escalation needed
- `2`: Execution failed → manual intervention required

## 5. Closure Template Enforcement

### Next Action Singularity Rule
> Closure MUST end with exactly one executable next_action OR `"terminal": true`

This guarantees onboarding never needs to "decide what's next" - the decision is pre-made in closure.

### Updated Closure Template Addition
```md
## CLOSURE VALIDATION (MANDATORY)
python tools/validate_closure_next_action.py --agent {AGENT_ID}

## RESULT
✅ Valid next_action set - onboarding can resume seamlessly
OR
❌ Closure invalid - next_action missing or malformed
```

## 6. Resulting System State

### After v2.3 Implementation:
- **Onboarding** = resume (not restart)
- **Planning** = pre-done in closure
- **Execution** = automated loop
- **Safety** = single deterministic gate
- **Drift** = structurally impossible

### Agent Experience:
1. **Receive message** (15 lines max)
2. **Run gate check** (1 second)
3. **Execute immediately** or **block with one reason**
4. **No decisions** - system handles everything

### System Benefits:
- **Zero re-interpretation** of tasks
- **Zero re-reading** of long messages
- **Zero re-planning** of solved work
- **100% deterministic** outcomes
- **Structural impossibility** of drift

## Template Usage
```bash
# Generate for specific agent
python -c "
import json
from datetime import datetime
from pathlib import Path

agent_id = 'Agent-X'  # Replace with actual agent
template = Path('templates/s2a_onboarding_v2_2.md').read_text()
message = template.replace('{AGENT_ID}', agent_id)
message = message.replace('{UUID}', 'generated-uuid-here')
message = message.replace('{UTC}', datetime.utcnow().isoformat())

# Write to agent's inbox
inbox_path = Path(f'agent_workspaces/{agent_id}/inbox/s2a_onboarding_soft_v2_2.md')
inbox_path.parent.mkdir(parents=True, exist_ok=True)
inbox_path.write_text(message)
print(f'Generated: {inbox_path}')
"
```

## Rehydration Snapshot Schema

**File:** `agent_workspaces/{AGENT_ID}/rehydration.json`

```json
{
  "agent_id": "Agent-X",
  "last_updated": "2026-01-12T07:12:33Z",
  "git_sha": "abc123def456",
  "cycle_id": "CYCLE-2026-01-12",
  "current_task": {
    "id": "TASK-123",
    "description": "Implement feature X",
    "status": "in_progress",
    "next_action": {
      "command": "python tools/feature_x.py --implement",
      "description": "Run the implementation script",
      "expected_output": "Feature implemented successfully"
    }
  },
  "validation_gates": {
    "git_sha_matches": true,
    "cycle_id_matches": true,
    "task_still_valid": true
  },
  "blockers": [],
  "resume_ready": true
}
```

## Resume Gate Validation Logic

```python
def validate_resume_gates(agent_id: str) -> dict:
    """Validate all gates for safe resume."""
    snapshot = load_rehydration_snapshot(agent_id)
    current_state = get_current_agent_state(agent_id)

    gates = {
        "git_sha_matches": snapshot['git_sha'] == current_state['git_sha'],
        "cycle_id_matches": snapshot.get('cycle_id') == current_state.get('cycle_id'),
        "task_still_valid": not is_task_completed(snapshot['current_task']['id'])
    }

    all_passed = all(gates.values())

    return {
        "gates": gates,
        "all_passed": all_passed,
        "snapshot_fresh": all_passed,
        "blockers": [] if all_passed else ["Resume gates failed - manual intervention required"]
    }
```

## Idempotent Resume Behavior

**Rules:**
- Same `rehydration.json` state = identical execution
- Task claiming is gated (no duplicate claims)
- Devlog posting is idempotent (same content = no duplicate posts)
- Status updates are atomic (no partial writes)

## Next Action Execution Contract

**Format:**
```json
{
  "command": "single executable command",
  "description": "what this achieves",
  "expected_output": "success indicators",
  "timeout_seconds": 300,
  "failure_modes": ["error message patterns"]
}
```

**Execution Rules:**
- Execute immediately (no planning phase)
- Capture stdout/stderr
- Validate against expected_output
- Update rehydration snapshot on completion/failure

## Compression Benefits

**Before (v2.1):** 200+ line checklist with redundant safety checks
**After (v2.2):** 50 lines focused on "load → validate → execute"

**Space Saved:** 150+ lines moved to referenced docs
**Focus:** Pure execution, zero drift
**Reliability:** Single source of truth (`rehydration.json`)