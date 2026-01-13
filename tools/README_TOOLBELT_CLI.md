# Toolbelt CLI Documentation

## Overview

The Toolbelt CLI (`toolbelt_cli.py`) provides a unified command-line interface for agent onboarding and management operations. It serves as the primary entry point for toolbelt operations, routing commands to specialized handlers while maintaining consistent CLI patterns.

## Installation & Setup

```bash
cd /path/to/agent-tools
# No additional setup required - runs as standalone Python script
```

## Command Structure

```bash
python tools/toolbelt_cli.py <command> [options...]
```

## Available Commands

### Agent Onboarding Commands

#### `onboard:soft`
Performs soft onboarding for new agents with validation and dry-run capabilities.

**Usage:**
```bash
python tools/toolbelt_cli.py onboard:soft --agent Agent-X [--dry-run]
```

**Parameters:**
- `--agent Agent-X`: Target agent identifier (required)
- `--dry-run`: Preview changes without executing (optional)

**Exit Codes:**
- `0`: Success - Agent successfully soft-onboarded
- `1`: Blocked - Agent already onboarded or validation failed
- `2`: Invalid arguments

**Example:**
```bash
python tools/toolbelt_cli.py onboard:soft --agent Agent-5
# Output: Agent-5 soft onboarded successfully
```

#### `onboard:status`
Checks the current onboarding status of an agent.

**Usage:**
```bash
python tools/toolbelt_cli.py onboard:status --agent Agent-X
```

**Parameters:**
- `--agent Agent-X`: Target agent identifier (required)

**Output:**
- Displays current onboarding state
- Shows completion percentage if in progress
- Lists any blockers or next steps

**Example:**
```bash
python tools/toolbelt_cli.py onboard:status --agent Agent-5
# Output: Agent-5: Onboarded (100% complete)
```

#### `onboard:hard`
Performs complete agent onboarding including workspace creation and configuration.

**Usage:**
```bash
python tools/toolbelt_cli.py onboard:hard --agent Agent-X --yes
```

**Parameters:**
- `--agent Agent-X`: Target agent identifier (required)
- `--yes`: Required confirmation flag (safety measure)

**Exit Codes:**
- `0`: Success - Complete onboarding finished
- `1`: Failed - Critical errors during onboarding
- `2`: Invalid arguments or missing --yes flag

**Example:**
```bash
python tools/toolbelt_cli.py onboard:hard --agent Agent-5 --yes
# Output: Agent-5 hard onboarded successfully
```

## Error Handling

### Common Exit Codes
- `0`: Success
- `1`: Operation blocked/failed (check error messages)
- `2`: Invalid arguments or command not found

### Error Messages
All error messages are written to stderr and include:
- Clear description of the issue
- Suggested next steps or fixes
- Usage examples for incorrect syntax

## Integration Examples

### Batch Processing
```bash
# Check status before onboarding
python tools/toolbelt_cli.py onboard:status --agent Agent-5
python tools/toolbelt_cli.py onboard:soft --agent Agent-5
python tools/toolbelt_cli.py onboard:hard --agent Agent-5 --yes
```

### Scripting Integration
```bash
#!/bin/bash
AGENT="Agent-5"
python tools/toolbelt_cli.py onboard:status --agent $AGENT
if [ $? -eq 1 ]; then
    python tools/toolbelt_cli.py onboard:soft --agent $AGENT
    python tools/toolbelt_cli.py onboard:hard --agent $AGENT --yes
fi
```

## Architecture

### Command Routing
- Commands are routed as subprocess calls to avoid import conflicts
- Each command maps to a specific handler script
- Consistent argument passing and error handling

### Safety Features
- `--yes` flag required for destructive operations
- Dry-run capabilities where applicable
- Clear error messages and exit codes

## Troubleshooting

### Command Not Found
```bash
# Check available commands
python tools/toolbelt_cli.py
# Output: Missing command. Try: onboard:soft | onboard:status | onboard:hard
```

### Import Errors
If you encounter import errors, the CLI automatically routes to subprocess execution to avoid dependency conflicts.

### Permission Issues
Ensure you have read/write access to agent workspace directories and configuration files.

## Development

### Adding New Commands
1. Add command mapping to `COMMANDS` dictionary
2. Create corresponding handler script
3. Update this documentation
4. Test with all parameter combinations

### Testing
```bash
# Test all commands
python tools/toolbelt_cli.py onboard:soft --agent TestAgent --dry-run
python tools/toolbelt_cli.py onboard:status --agent TestAgent
python tools/toolbelt_cli.py onboard:hard --agent TestAgent --yes  # Will fail safely
```