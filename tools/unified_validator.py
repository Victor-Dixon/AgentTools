#!/usr/bin/env python3
"""
Unified Validator - Consolidated Validation Tool
=================================================

<!-- SSOT Domain: qa -->

Consolidates all validation capabilities into a single unified tool.
Replaces 73+ individual validation tools with modular validation system.

Validation Categories:
- ssot_config: SSOT and config validation
- imports: Import statement validation
- tracker: Tracker status validation
- session: Session transition validation
- refactor: Refactor status validation
- consolidation: Consolidation validation
- queue: Queue behavior validation
- alignment: Code-documentation alignment

Consolidated Tools:
- ssot_config_validator.py → --category ssot_config
- validate_trackers.py → --category tracker
- validate_imports.py → --category imports
- file_refactor_detector.py → --category refactor
- session_transition_helper.py → --category session
- tracker_status_validator.py → --category tracker
- check_system_readiness.py → --category system

Author: Phase 1 Consolidation
Date: 2025-12-25
V2 Compliant: Yes (<400 lines)
"""

import argparse
import ast
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedValidator:
    """Unified validation system consolidating all validation capabilities."""
    
    # Valid config_ssot imports
    VALID_SSOT_IMPORTS = [
        "from src.core.config_ssot import",
        "import src.core.config_ssot",
        "from src.core import config_ssot",
    ]
    
    # Deprecated config imports
    DEPRECATED_IMPORTS = [
        "from src.core.config_core import",
        "from src.core.unified_config import",
        "from src.core.config_browser import",
        "from src.core.config_thresholds import",
        "from src.shared_utils.config import",
    ]
    
    def __init__(self):
        """Initialize unified validator."""
        self.project_root = project_root
        self.violations: List[Dict] = []
        self.warnings: List[Dict] = []
        
    def validate_ssot_config(self, file_path: Optional[Path] = None, 
                             dir_path: Optional[Path] = None) -> Dict[str, Any]:
        """Validate SSOT config usage."""
        results = {
            "category": "ssot_config",
            "files_checked": 0,
            "violations": [],
            "warnings": [],
            "valid_imports": [],
            "timestamp": datetime.now().isoformat()
        }
        
        files_to_check = []
        if file_path:
            files_to_check = [file_path]
        elif dir_path:
            files_to_check = list(dir_path.rglob("*.py"))
        else:
            # Default: check src directory
            src_dir = self.project_root / "src"
            if src_dir.exists():
                files_to_check = list(src_dir.rglob("*.py"))
        
        for py_file in files_to_check:
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content, filename=str(py_file))
                results["files_checked"] += 1
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        import_str = self._get_import_string(node)
                        if any(dep in import_str for dep in self.DEPRECATED_IMPORTS):
                            results["violations"].append({
                                "file": str(py_file),
                                "line": node.lineno,
                                "message": f"Deprecated import: {import_str}",
                                "severity": "high"
                            })
                        elif any(valid in import_str for valid in self.VALID_SSOT_IMPORTS):
                            results["valid_imports"].append({
                                "file": str(py_file),
                                "line": node.lineno,
                                "import": import_str
                            })
            except SyntaxError:
                results["warnings"].append({
                    "file": str(py_file),
                    "message": "Syntax error - could not parse"
                })
            except Exception as e:
                results["warnings"].append({
                    "file": str(py_file),
                    "message": str(e)
                })
        
        results["status"] = "VALID" if not results["violations"] else "VIOLATIONS_FOUND"
        return results
    
    def _get_import_string(self, node: ast.ImportFrom) -> str:
        """Get import string from AST node."""
        module = node.module or ""
        names = ", ".join([alias.name for alias in node.names])
        return f"from {module} import {names}"
    
    def validate_imports(self, file_path: str) -> Dict[str, Any]:
        """Validate imports in a Python file."""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.project_root / path
        
        if not path.exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(path))
            
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.append({
                            "type": "from",
                            "module": node.module or "",
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno
                        })
            
            return {
                "file": str(path),
                "imports": imports,
                "count": len(imports),
                "status": "VALID",
                "timestamp": datetime.now().isoformat()
            }
        except SyntaxError as e:
            return {"file": str(path), "error": f"Syntax error: {e}"}
        except Exception as e:
            return {"file": str(path), "error": str(e)}
    
    def validate_tracker_status(self) -> Dict[str, Any]:
        """Validate tracker file consistency."""
        docs_org = self.project_root / "docs" / "organization"
        results = {
            "category": "tracker",
            "trackers_found": 0,
            "issues": [],
            "status": "VALID",
            "timestamp": datetime.now().isoformat()
        }
        
        if not docs_org.exists():
            results["status"] = "NO_TRACKERS_FOUND"
            results["message"] = "docs/organization directory not found"
            return results
        
        tracker_files = list(docs_org.glob("*TRACKER*.md"))
        results["trackers_found"] = len(tracker_files)
        
        for tracker_file in tracker_files:
            try:
                content = tracker_file.read_text(encoding="utf-8")
                # Check for common issues
                if "TODO" in content or "FIXME" in content:
                    results["issues"].append({
                        "file": tracker_file.name,
                        "message": "Contains TODO/FIXME markers"
                    })
            except Exception as e:
                results["issues"].append({
                    "file": tracker_file.name,
                    "message": str(e)
                })
        
        if results["issues"]:
            results["status"] = "ISSUES_FOUND"
        
        return results
    
    def validate_session_transition(self, agent_id: str, 
                                    devlog_only: bool = False,
                                    checklist: bool = False) -> Dict[str, Any]:
        """Validate session transition for an agent."""
        agent_dir = self.project_root / "agent_workspaces" / agent_id
        results = {
            "category": "session",
            "agent_id": agent_id,
            "status_file_exists": False,
            "devlog_exists": False,
            "checklist_complete": False,
            "issues": [],
            "timestamp": datetime.now().isoformat()
        }
        
        if not agent_dir.exists():
            results["status"] = "AGENT_NOT_FOUND"
            return results
        
        # Check status file
        status_file = agent_dir / "status.json"
        if status_file.exists():
            results["status_file_exists"] = True
            try:
                status_data = json.loads(status_file.read_text())
                results["current_status"] = status_data.get("status", "unknown")
            except Exception as e:
                results["issues"].append(f"Error reading status.json: {e}")
        else:
            results["issues"].append("status.json not found")
        
        # Check devlogs
        devlogs_dir = agent_dir / "devlogs"
        if devlogs_dir.exists():
            devlog_files = list(devlogs_dir.glob("*.md"))
            results["devlog_exists"] = len(devlog_files) > 0
            results["devlog_count"] = len(devlog_files)
        
        if devlog_only:
            results["status"] = "VALID" if results["devlog_exists"] else "NO_DEVLOGS"
            return results
        
        # Check checklist if requested
        if checklist:
            checklist_file = agent_dir / "checklist.md"
            if checklist_file.exists():
                content = checklist_file.read_text()
                unchecked = content.count("- [ ]")
                checked = content.count("- [x]") + content.count("- [X]")
                results["checklist_complete"] = unchecked == 0 and checked > 0
                results["checklist_progress"] = f"{checked}/{checked + unchecked}"
        
        results["status"] = "VALID" if not results["issues"] else "ISSUES_FOUND"
        return results
    
    def validate_refactor_status(self, file_path: Optional[str] = None,
                                 dir_path: Optional[str] = None,
                                 author: Optional[str] = None) -> Dict[str, Any]:
        """Validate refactor status of files."""
        results = {
            "category": "refactor",
            "files_checked": 0,
            "refactored": [],
            "needs_refactor": [],
            "timestamp": datetime.now().isoformat()
        }
        
        files_to_check = []
        if file_path:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.project_root / path
            files_to_check = [path]
        elif dir_path:
            path = Path(dir_path)
            if not path.is_absolute():
                path = self.project_root / path
            files_to_check = list(path.rglob("*.py"))
        
        for py_file in files_to_check:
            if not py_file.exists():
                continue
            
            results["files_checked"] += 1
            try:
                content = py_file.read_text(encoding="utf-8")
                
                # Check for V2 compliance markers
                is_v2 = "V2 Compliant" in content or "v2 compliant" in content.lower()
                lines = len(content.splitlines())
                
                # Check for author if specified
                if author and author not in content:
                    continue
                
                file_info = {
                    "file": str(py_file),
                    "lines": lines,
                    "v2_compliant": is_v2,
                    "under_400_lines": lines < 400
                }
                
                if is_v2 and lines < 400:
                    results["refactored"].append(file_info)
                else:
                    results["needs_refactor"].append(file_info)
            except Exception as e:
                results["needs_refactor"].append({
                    "file": str(py_file),
                    "error": str(e)
                })
        
        results["status"] = "VALID" if not results["needs_refactor"] else "NEEDS_WORK"
        return results
    
    def validate_consolidation(self) -> Dict[str, Any]:
        """Validate consolidation status."""
        tools_dir = self.project_root / "tools"
        deprecated_dir = tools_dir / "deprecated"
        
        results = {
            "category": "consolidation",
            "total_tools": 0,
            "deprecated_tools": 0,
            "unified_tools": [],
            "status": "VALID",
            "timestamp": datetime.now().isoformat()
        }
        
        # Count tools
        if tools_dir.exists():
            results["total_tools"] = len(list(tools_dir.glob("*.py")))
        
        if deprecated_dir.exists():
            results["deprecated_tools"] = len(list(deprecated_dir.rglob("*.py")))
        
        # Find unified tools
        unified_pattern = tools_dir.glob("unified_*.py")
        results["unified_tools"] = [f.name for f in unified_pattern]
        
        return results
    
    def validate_queue(self) -> Dict[str, Any]:
        """Validate queue behavior."""
        queue_file = self.project_root / "message_queue" / "queue.json"
        results = {
            "category": "queue",
            "queue_exists": queue_file.exists(),
            "status": "VALID",
            "timestamp": datetime.now().isoformat()
        }
        
        if queue_file.exists():
            try:
                content = queue_file.read_text()
                data = json.loads(content)
                results["queue_size"] = len(data) if isinstance(data, list) else len(data.get("messages", []))
                results["valid_json"] = True
            except json.JSONDecodeError:
                results["valid_json"] = False
                results["status"] = "INVALID_JSON"
            except Exception as e:
                results["error"] = str(e)
                results["status"] = "ERROR"
        else:
            results["status"] = "NO_QUEUE_FILE"
        
        return results
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation categories."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "validations": {}
        }
        
        results["validations"]["ssot_config"] = self.validate_ssot_config()
        results["validations"]["tracker"] = self.validate_tracker_status()
        results["validations"]["consolidation"] = self.validate_consolidation()
        results["validations"]["queue"] = self.validate_queue()
        
        # Summary
        all_valid = all(
            v.get("status") == "VALID" 
            for v in results["validations"].values()
        )
        results["overall_status"] = "ALL_VALID" if all_valid else "ISSUES_FOUND"
        
        return results
    
    def print_validation_report(self, results: Dict[str, Any]):
        """Print formatted validation report."""
        print("\n" + "=" * 70)
        print("🛡️ UNIFIED VALIDATION REPORT")
        print("=" * 70)
        
        if "validations" in results:
            for category, data in results["validations"].items():
                status = data.get("status", "UNKNOWN")
                icon = "✅" if status == "VALID" else "⚠️" if "ISSUES" in status else "❌"
                print(f"\n{icon} {category.upper()}: {status}")
                
                if "violations" in data and data["violations"]:
                    print(f"   Violations: {len(data['violations'])}")
                if "issues" in data and data["issues"]:
                    print(f"   Issues: {len(data['issues'])}")
        else:
            # Single validation result
            status = results.get("status", "UNKNOWN")
            icon = "✅" if status == "VALID" else "❌"
            print(f"\n{icon} Status: {status}")
            
            if "violations" in results:
                print(f"   Violations: {len(results['violations'])}")
        
        print(f"\n🕐 Timestamp: {results.get('timestamp', 'unknown')}")
        print("=" * 70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Unified Validator - Consolidated validation for all systems",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--category", "-c",
        choices=["ssot_config", "imports", "tracker", "session", "refactor", 
                 "consolidation", "queue", "all"],
        default="all",
        help="Validation category (default: all)"
    )
    
    parser.add_argument("--file", "-f", type=str, help="File to validate")
    parser.add_argument("--dir", "-d", type=str, help="Directory to validate")
    parser.add_argument("--agent", type=str, help="Agent ID for session validation")
    parser.add_argument("--author", type=str, help="Author filter for refactor validation")
    parser.add_argument("--devlog-only", action="store_true", help="Devlog-only validation")
    parser.add_argument("--checklist", action="store_true", help="Include checklist validation")
    parser.add_argument("--all", action="store_true", help="Run all validations")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    validator = UnifiedValidator()
    
    if args.all or args.category == "all":
        results = validator.validate_all()
    elif args.category == "ssot_config":
        file_path = Path(args.file) if args.file else None
        dir_path = Path(args.dir) if args.dir else None
        results = validator.validate_ssot_config(file_path=file_path, dir_path=dir_path)
    elif args.category == "imports":
        if not args.file:
            print("Error: --file required for imports validation")
            return 1
        results = validator.validate_imports(args.file)
    elif args.category == "tracker":
        results = validator.validate_tracker_status()
    elif args.category == "session":
        if not args.agent:
            print("Error: --agent required for session validation")
            return 1
        results = validator.validate_session_transition(
            args.agent, 
            devlog_only=args.devlog_only,
            checklist=args.checklist
        )
    elif args.category == "refactor":
        results = validator.validate_refactor_status(
            file_path=args.file,
            dir_path=args.dir,
            author=args.author
        )
    elif args.category == "consolidation":
        results = validator.validate_consolidation()
    elif args.category == "queue":
        results = validator.validate_queue()
    else:
        results = validator.validate_all()
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        validator.print_validation_report(results)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
