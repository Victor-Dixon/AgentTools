#!/usr/bin/env python3
"""
Thea GUI Import Fix Script
Agent-4 Strategic Implementation for Thea Deployment Coordination

Fixes import issues in Thea MMORPG GUI system to enable proper deployment.
"""

import os
import sys
import re
from pathlib import Path

class TheaImportFixer:
    """Fixes import issues in Thea GUI components."""

    def __init__(self, gui_dir: Path):
        self.gui_dir = gui_dir
        self.fixed_files = []

    def fix_relative_imports(self):
        """Fix relative import statements in GUI files."""
        print("🔧 Fixing relative imports in Thea GUI...")

        # Find all Python files in GUI directory
        python_files = list(self.gui_dir.rglob("*.py"))

        for file_path in python_files:
            if self._fix_file_imports(file_path):
                self.fixed_files.append(file_path)

        print(f"✅ Fixed imports in {len(self.fixed_files)} files")

    def _fix_file_imports(self, file_path: Path) -> bool:
        """Fix imports in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Fix common relative import patterns
            # from ..module -> from gui.module
            content = re.sub(
                r'from \.\.([a-zA-Z_][a-zA-Z0-9_]*)',
                r'from gui.\1',
                content
            )

            # from ..subpackage.module -> from gui.subpackage.module
            content = re.sub(
                r'from \.\.([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)',
                r'from gui.\1.\2',
                content
            )

            # from .module -> from gui.module (for files in subdirs)
            if str(file_path.parent) != str(self.gui_dir):
                content = re.sub(
                    r'from \.([a-zA-Z_][a-zA-Z0-9_]*)',
                    r'from gui.\1',
                    content
                )

            # Fix dreamscape imports that don't exist
            content = re.sub(
                r'from dreamscape\.gui\.([a-zA-Z_][a-zA-Z0-9_]*)',
                r'from gui.\1',
                content
            )

            # If content changed, write back
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  📝 Fixed: {file_path.relative_to(self.gui_dir)}")
                return True

        except Exception as e:
            print(f"  ❌ Error fixing {file_path}: {e}")

        return False

    def create_init_files(self):
        """Ensure all __init__.py files exist and have proper imports."""
        print("📁 Creating/updating __init__.py files...")

        subdirs = [self.gui_dir] + [d for d in self.gui_dir.rglob("*") if d.is_dir()]

        for subdir in subdirs:
            init_file = subdir / "__init__.py"
            if not init_file.exists():
                # Create basic __init__.py
                init_content = '"""Thea GUI components package."""\n'
                with open(init_file, 'w') as f:
                    f.write(init_content)
                print(f"  📄 Created: {init_file.relative_to(self.gui_dir)}")

    def validate_fixes(self):
        """Validate that the fixes work."""
        print("🔍 Validating import fixes...")

        # Try importing main components
        sys.path.insert(0, str(self.gui_dir.parent))

        test_imports = [
            ('gui.main_window', 'TheaMainWindow'),
            ('gui.components', None),
            ('gui.controllers', None),
            ('gui.panels', None),
            ('gui.viewmodels', None),
        ]

        success_count = 0
        for module_name, class_name in test_imports:
            try:
                module = __import__(module_name, fromlist=[class_name] if class_name else [])
                if class_name and hasattr(module, class_name):
                    print(f"  ✅ {module_name}.{class_name}")
                    success_count += 1
                elif not class_name:
                    print(f"  ✅ {module_name}")
                    success_count += 1
                else:
                    print(f"  ⚠️  {module_name}: Missing class {class_name}")
            except ImportError as e:
                print(f"  ❌ {module_name}: {e}")

        return success_count == len(test_imports)

def main():
    """Main fix execution."""
    print("🎮 THEA GUI IMPORT FIXER")
    print("=" * 40)
    print("Agent-4 Strategic Implementation")

    # Get Thea directory
    current_dir = Path(__file__).parent
    gui_dir = current_dir / "gui"

    if not gui_dir.exists():
        print(f"❌ GUI directory not found: {gui_dir}")
        return False

    fixer = TheaImportFixer(gui_dir)

    # Execute fixes
    fixer.create_init_files()
    fixer.fix_relative_imports()

    # Validate
    if fixer.validate_fixes():
        print("\n🎉 IMPORT FIXES SUCCESSFUL!")
        print(f"📊 Fixed {len(fixer.fixed_files)} files")
        print("🚀 Thea GUI ready for deployment testing")
        return True
    else:
        print("\n❌ IMPORT FIXES INCOMPLETE")
        print("🔧 Manual review required")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)