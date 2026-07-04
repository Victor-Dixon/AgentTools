# S2A ONBOARDING (SOFT) — v2.3 (FORCE-MULTIPLIER GATE + ONE-SCREEN LOOP)

## Evolution Summary
- **v2.2**: Rehydrate → Resume (eliminated checklists)
- **v2.3**: Force-Multiplier Gate + One-Screen Loop (eliminated cycle planning)

## Core Rule (Non-Negotiable)
> If the Force-Multiplier Gate passes, execution begins immediately.
> If it fails, exactly one blocker is produced — no partial execution.

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