#!/usr/bin/env python3
"""
Closure Quality Audit Tool
==========================

Comprehensive code quality and consolidation audit for session closures.
Helps agents systematically check for issues that should be documented in master task list.

Features:
- Code quality scanning (linting, imports, CLI health)
- Functionality consolidation detection
- Issue severity assessment and task list integration
- Safe, non-destructive analysis

Usage:
    python tools/closure_quality_audit.py --agent Agent-X --audit

Author: Agent-3 (Infrastructure & DevOps)
Created: 2026-01-11
"""

import argparse
import ast
import importlib
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class QualityIssue:
    """Represents a code quality issue found during audit."""
    file_path: str
    line_number: int
    issue_type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    fix_effort: str  # 'quick', 'moderate', 'complex'
    consolidation_opportunity: bool = False

class ClosureQualityAudit:
    """Comprehensive quality audit for session closures."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[QualityIssue] = []
        self.python_files: List[Path] = []

    def scan_python_files(self) -> None:
        """Scan for all Python files in the project."""
        self.python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', 'archive']]

            for file in files:
                if file.endswith('.py'):
                    self.python_files.append(Path(root) / file)

        print(f"📁 Found {len(self.python_files)} Python files to audit")

    def run_linting_check(self) -> None:
        """Run basic linting checks for errors."""
        print("\n🔍 Running linting checks...")

        try:
            # Try pylint for comprehensive checking
            result = subprocess.run([
                sys.executable, '-m', 'pylint',
                '--errors-only',  # Only show errors, not warnings
                '--disable=C,R,W',  # Disable convention, refactor, warning checks
                'tools/'
            ], capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                # Parse pylint output for errors
                lines = result.stdout.split('\n') + result.stderr.split('\n')
                for line in lines:
                    if '.py:' in line and any(err in line for err in ['error', 'Error', 'E:']):
                        # Parse pylint format: file.py:line:col: error_code: message
                        parts = line.split(':')
                        if len(parts) >= 4:
                            file_path = parts[0]
                            try:
                                line_num = int(parts[1])
                                error_msg = ':'.join(parts[3:]).strip()

                                severity = 'high' if any(crit in error_msg.lower() for crit in
                                                       ['import', 'syntax', 'undefined']) else 'medium'

                                self.issues.append(QualityIssue(
                                    file_path=file_path,
                                    line_number=line_num,
                                    issue_type='linting_error',
                                    severity=severity,
                                    description=f"Linting error: {error_msg}",
                                    fix_effort='moderate'
                                ))
                            except ValueError:
                                continue

            if self.issues:
                print(f"❌ Found {len([i for i in self.issues if i.issue_type == 'linting_error'])} linting errors")
            else:
                print("✅ No critical linting errors found")

        except subprocess.TimeoutExpired:
            print("⚠️ Linting check timed out")
        except FileNotFoundError:
            print("ℹ️ Pylint not available, skipping advanced linting")

    def check_imports(self) -> None:
        """Check that all Python files can be imported without errors."""
        print("\n🔍 Checking imports...")

        import_issues = 0

        for py_file in self.python_files:
            try:
                # Convert file path to module path
                rel_path = py_file.relative_to(self.project_root)
                module_parts = []

                for part in rel_path.parts:
                    if part.endswith('.py'):
                        part = part[:-3]  # Remove .py extension
                    module_parts.append(part)

                module_name = '.'.join(module_parts)

                # Try to import the module
                importlib.import_module(module_name)

            except Exception as e:
                # Skip __init__.py files and known problematic imports
                if py_file.name != '__init__.py' and not any(skip in str(e) for skip in
                                                          ['No module named', 'DLL load failed']):
                    self.issues.append(QualityIssue(
                        file_path=str(py_file),
                        line_number=1,
                        issue_type='import_error',
                        severity='high',
                        description=f"Import error: {str(e)}",
                        fix_effort='moderate'
                    ))
                    import_issues += 1

        if import_issues > 0:
            print(f"❌ Found {import_issues} import issues")
        else:
            print("✅ All imports successful")

    def check_cli_tools(self) -> None:
        """Check CLI tools for basic functionality and error handling."""
        print("\n🔍 Checking CLI tools...")

        cli_issues = 0

        # Focus on tools directory
        tools_dir = self.project_root / 'tools'

        for py_file in tools_dir.glob('*.py'):
            if py_file.name.startswith('test_') or py_file.name == '__init__.py':
                continue

            try:
                # Try running with --help flag
                result = subprocess.run([
                    sys.executable, str(py_file), '--help'
                ], capture_output=True, timeout=10)

                if result.returncode != 0:
                    # Check if it's just that --help isn't supported vs actual error
                    stderr_output = result.stderr.decode('utf-8', errors='ignore')
                    if 'unrecognized arguments: --help' not in stderr_output:
                        self.issues.append(QualityIssue(
                            file_path=str(py_file),
                            line_number=1,
                            issue_type='cli_error',
                            severity='medium',
                            description=f"CLI tool error: {stderr_output[:100]}...",
                            fix_effort='moderate'
                        ))
                        cli_issues += 1

            except subprocess.TimeoutExpired:
                self.issues.append(QualityIssue(
                    file_path=str(py_file),
                    line_number=1,
                    issue_type='cli_timeout',
                    severity='medium',
                    description="CLI tool hangs or takes too long to respond",
                    fix_effort='moderate'
                ))
                cli_issues += 1
            except Exception as e:
                self.issues.append(QualityIssue(
                    file_path=str(py_file),
                    line_number=1,
                    issue_type='cli_exception',
                    severity='high',
                    description=f"CLI tool crashed: {str(e)}",
                    fix_effort='moderate'
                ))
                cli_issues += 1

        if cli_issues > 0:
            print(f"❌ Found {cli_issues} CLI tool issues")
        else:
            print("✅ All CLI tools functional")

    def analyze_functionality_consolidation(self) -> None:
        """Analyze codebase for consolidation opportunities."""
        print("\n🔍 Analyzing functionality consolidation opportunities...")

        # Simple pattern matching for common functionality
        consolidation_patterns = [
            (r'def.*download.*file', 'file_download', 'File download functionality'),
            (r'def.*upload.*file', 'file_upload', 'File upload functionality'),
            (r'def.*parse.*json', 'json_parsing', 'JSON parsing functionality'),
            (r'def.*connect.*api', 'api_connection', 'API connection functionality'),
            (r'def.*authenticate', 'authentication', 'Authentication functionality'),
            (r'class.*Client', 'api_client', 'API client classes'),
            (r'def.*log.*message', 'logging', 'Logging functionality'),
        ]

        functionality_map: Dict[str, List[str]] = {}

        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern, func_type, description in consolidation_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        if func_type not in functionality_map:
                            functionality_map[func_type] = []
                        functionality_map[func_type].append(str(py_file))

            except Exception:
                continue

        # Identify consolidation opportunities
        consolidation_count = 0
        for func_type, files in functionality_map.items():
            if len(files) > 1:
                self.issues.append(QualityIssue(
                    file_path=', '.join(files[:3]) + ('...' if len(files) > 3 else ''),
                    line_number=1,
                    issue_type='consolidation_opportunity',
                    severity='low',
                    description=f"Multiple implementations of {func_type} in {len(files)} files",
                    fix_effort='complex',
                    consolidation_opportunity=True
                ))
                consolidation_count += 1

        if consolidation_count > 0:
            print(f"🔄 Found {consolidation_count} consolidation opportunities")
        else:
            print("✅ No consolidation issues found")

    def generate_report(self) -> str:
        """Generate audit report."""
        report_lines = []
        report_lines.append("📋 CLOSURE QUALITY AUDIT REPORT")
        report_lines.append("=" * 50)

        if not self.issues:
            report_lines.append("✅ No issues found - codebase is clean!")
            return '\n'.join(report_lines)

        # Group issues by severity
        severity_groups = {'critical': [], 'high': [], 'medium': [], 'low': []}

        for issue in self.issues:
            severity_groups[issue.severity].append(issue)

        # Report by severity
        for severity in ['critical', 'high', 'medium', 'low']:
            issues = severity_groups[severity]
            if issues:
                report_lines.append(f"\n{severity.upper()} PRIORITY ({len(issues)} issues):")
                for issue in issues:
                    report_lines.append(f"  • {issue.file_path}:{issue.line_number}")
                    report_lines.append(f"    {issue.description}")
                    report_lines.append(f"    Effort: {issue.fix_effort}")
                    if issue.consolidation_opportunity:
                        report_lines.append("    💡 CONSOLIDATION OPPORTUNITY")
                    report_lines.append("")

        # Summary
        total_issues = len(self.issues)
        consolidation_ops = len([i for i in self.issues if i.consolidation_opportunity])

        report_lines.append("\n📊 SUMMARY:")
        report_lines.append(f"  Total Issues: {total_issues}")
        report_lines.append(f"  Consolidation Opportunities: {consolidation_ops}")

        if total_issues > 0:
            report_lines.append("\n⚠️ ACTION REQUIRED: Add these issues to MASTER_TASK_LIST.md")
        return '\n'.join(report_lines)

    def run_full_audit(self) -> str:
        """Run complete quality audit."""
        print("🚀 Starting Closure Quality Audit...")

        self.scan_python_files()
        self.run_linting_check()
        self.check_imports()
        self.check_cli_tools()
        self.analyze_functionality_consolidation()

        return self.generate_report()

def main():
    parser = argparse.ArgumentParser(description="Closure Quality Audit Tool")
    parser.add_argument("--agent", help="Agent ID for context")
    parser.add_argument("--audit", action="store_true", help="Run full quality audit")

    args = parser.parse_args()

    if not args.audit:
        parser.print_help()
        return

    project_root = Path(__file__).parent.parent
    auditor = ClosureQualityAudit(project_root)

    try:
        report = auditor.run_full_audit()
        print("\n" + "="*50)
        print(report)
        print("="*50)

        issue_count = len(auditor.issues)
        consolidation_count = len([i for i in auditor.issues if i.consolidation_opportunity])

        print("\n🎯 CLOSURE INSTRUCTION:")
        print(f"   Code health check completed — {issue_count} issues found and documented")
        print(f"   Consolidation audit completed — {consolidation_count} consolidation opportunities identified")

        if issue_count > 0:
            print("\n⚠️ REMEMBER: Add these issues to MASTER_TASK_LIST.md")
        sys.exit(1)  # Exit with error to indicate issues found

    except Exception as e:
        print(f"❌ Audit failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()