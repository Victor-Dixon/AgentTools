#!/usr/bin/env python3
"""Quick V2 compliance count for Agent-Tools repository."""

import sys
from pathlib import Path

# Add parent repo to path
sys.path.insert(0, str(Path(__file__).parent.parent / "Agent_Cellphone_V2_Repository"))

from tools.v2_compliance_checker import V2ComplianceChecker

checker = V2ComplianceChecker()

# Check all Python files in tools directory
tools_dir = Path("tools")
files = list(tools_dir.rglob("*.py"))
files = [f for f in files if "__pycache__" not in str(f) and f.name != "__init__.py"]

print(f"Checking {len(files)} files...")

for file in files:
    checker.check_file(file)

# Count unique files with violations
files_with_violations = set(v["file"] for v in checker.violations)
compliant_files = set(checker.compliant_files)

print(f"\n{'='*60}")
print(f"Total files checked: {len(files)}")
print(f"✅ Compliant files: {len(compliant_files)}")
print(f"❌ Files with violations: {len(files_with_violations)}")
print(f"📊 Compliance rate: {len(compliant_files)/len(files)*100:.1f}%")
print(f"{'='*60}\n")


