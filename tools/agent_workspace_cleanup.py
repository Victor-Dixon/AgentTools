#!/usr/bin/env python3
"""
Agent Workspace Cleanup Utility
==============================

Safely cleans up agent-owned workspace artifacts after session completion.

Features:
- Only touches agent-owned directories
- Moves files to archive instead of deleting
- Provides before/after verification
- Safe for shared workspace environments

Usage:
    python tools/agent_workspace_cleanup.py --agent Agent-X --cleanup

Author: Agent-3 (Infrastructure & DevOps)
Created: 2026-01-11
"""

import argparse
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

def get_agent_workspace_dirs(agent_id: str, project_root: Path) -> List[Path]:
    """Get all agent-owned workspace directories."""
    workspace_dirs = []

    # Check for agent_workspaces/Agent-X/
    agent_workspace = project_root / "agent_workspaces" / agent_id
    if agent_workspace.exists():
        workspace_dirs.append(agent_workspace)

    # Check for tools/agent_workspaces/Agent-X/
    tools_workspace = project_root / "tools" / "agent_workspaces" / agent_id
    if tools_workspace.exists():
        workspace_dirs.append(tools_workspace)

    return workspace_dirs

def identify_cleanup_candidates(workspace_dir: Path) -> List[Tuple[Path, str]]:
    """Identify files that are candidates for cleanup."""
    candidates = []

    # Define cleanup patterns (safe to remove/archive)
    cleanup_patterns = [
        # Test files created during development
        ("test_*.py", "Temporary test files"),
        ("debug_*.py", "Debug scripts"),
        ("temp_*.py", "Temporary scripts"),

        # Working files and drafts
        ("*draft*.md", "Working drafts"),
        ("*working*.md", "Working files"),
        ("*scratch*.md", "Scratch notes"),

        # Session artifacts
        ("session_*.log", "Session logs"),
        ("*screenshot*.png", "Session screenshots"),
        ("*capture*.png", "Screen captures"),

        # Cache files
        ("*.pyc", "Python cache files"),
        ("__pycache__", "Python cache directories"),
        ("*.cache", "Cache files"),
    ]

    for pattern, description in cleanup_patterns:
        if "*" in pattern:
            # Use glob pattern
            for file_path in workspace_dir.rglob(pattern):
                if file_path.is_file():
                    candidates.append((file_path, description))
                elif file_path.is_dir() and pattern == "__pycache__":
                    candidates.append((file_path, description))
        else:
            # Exact filename match
            file_path = workspace_dir / pattern
            if file_path.exists():
                candidates.append((file_path, description))

    return candidates

def create_archive_dir(project_root: Path, agent_id: str) -> Path:
    """Create archive directory for moved files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = project_root / "archive" / f"{agent_id}_cleanup_{timestamp}"
    archive_dir.mkdir(parents=True, exist_ok=True)
    return archive_dir

def safe_archive_file(file_path: Path, archive_dir: Path, relative_path: Path) -> bool:
    """Safely move file to archive directory."""
    try:
        # Create subdirectory structure in archive
        archive_subdir = archive_dir / relative_path.parent
        archive_subdir.mkdir(parents=True, exist_ok=True)

        # Move file to archive
        archive_path = archive_subdir / relative_path.name
        shutil.move(str(file_path), str(archive_path))

        print(f"✅ Archived: {relative_path} → {archive_path.relative_to(archive_dir.parent)}")
        return True
    except Exception as e:
        print(f"❌ Failed to archive {file_path}: {e}")
        return False

def perform_cleanup(agent_id: str, dry_run: bool = True) -> Tuple[int, int]:
    """Perform workspace cleanup for the specified agent."""
    project_root = Path(__file__).parent.parent

    print(f"🔍 Analyzing workspace for Agent: {agent_id}")
    print(f"📁 Project root: {project_root}")

    # Get agent workspace directories
    workspace_dirs = get_agent_workspace_dirs(agent_id, project_root)

    if not workspace_dirs:
        print(f"ℹ️ No workspace directories found for {agent_id}")
        return 0, 0

    print(f"📂 Found {len(workspace_dirs)} workspace directories:")
    for ws_dir in workspace_dirs:
        print(f"   - {ws_dir}")

    # Identify cleanup candidates
    all_candidates = []
    for workspace_dir in workspace_dirs:
        candidates = identify_cleanup_candidates(workspace_dir)
        all_candidates.extend(candidates)

    if not all_candidates:
        print("ℹ️ No cleanup candidates found")
        return 0, 0

    print(f"\n🧹 Found {len(all_candidates)} cleanup candidates:")

    # Group by type for summary
    type_counts = {}
    for file_path, description in all_candidates:
        type_counts[description] = type_counts.get(description, 0) + 1
        relative_path = file_path.relative_to(project_root)
        print(f"   - {relative_path} ({description})")

    print("
📊 Cleanup Summary:"    for desc, count in type_counts.items():
        print(f"   - {desc}: {count} files")

    if dry_run:
        print("
🔍 DRY RUN MODE - No files will be moved"        print("💡 Run with --cleanup to perform actual cleanup")
        return len(all_candidates), 0

    # Perform actual cleanup
    print("
🗂️ Creating archive directory..."    archive_dir = create_archive_dir(project_root, agent_id)
    print(f"📦 Archive location: {archive_dir}")

    print("
🧹 Performing cleanup..."    success_count = 0
    total_count = len(all_candidates)

    for file_path, description in all_candidates:
        relative_path = file_path.relative_to(project_root)
        if safe_archive_file(file_path, archive_dir, relative_path):
            success_count += 1

    print("
✅ Cleanup completed!"    print(f"   Total candidates: {total_count}")
    print(f"   Successfully archived: {success_count}")
    print(f"   Archive location: {archive_dir}")

    if success_count < total_count:
        print(f"   ⚠️ Failed to archive: {total_count - success_count} files")

    return total_count, success_count

def main():
    parser = argparse.ArgumentParser(description="Agent Workspace Cleanup Utility")
    parser.add_argument("--agent", required=True, help="Agent ID (e.g., Agent-1, Agent-2)")
    parser.add_argument("--cleanup", action="store_true", help="Perform actual cleanup (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Force dry-run mode (default)")

    args = parser.parse_args()

    # Default to dry-run unless explicitly asked to cleanup
    dry_run = not args.cleanup or args.dry_run

    if dry_run:
        print("🔍 DRY RUN MODE - Analyzing workspace (no changes will be made)")
    else:
        print("🧹 CLEANUP MODE - Files will be moved to archive")
        confirm = input(f"Are you sure you want to clean up {args.agent}'s workspace? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Cleanup cancelled by user")
            return

    try:
        total_candidates, archived_count = perform_cleanup(args.agent, dry_run)

        if dry_run:
            print("
📋 To perform actual cleanup, run:"            print(f"   python tools/agent_workspace_cleanup.py --agent {args.agent} --cleanup")
        else:
            print("
✅ Workspace cleanup completed successfully"            if archived_count > 0:
                print(f"   📦 {archived_count} files archived safely")

    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()