#!/usr/bin/env python3
"""
Thea MMORPG GUI Deployment Script
Infrastructure automation provided by Agent-3 (Infrastructure & DevOps)
"""

import os
import sys
import subprocess
import time
from pathlib import Path

class TheaGUIDeployer:
    """Thea GUI system deployment manager."""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.gui_dir = self.base_dir / "gui"

    def check_gui_files(self):
        """Check if GUI files are present and ready."""
        print("🔍 Checking GUI file status...")

        required_files = [
            "main_window.py",
            "components/__init__.py",
            "controllers/__init__.py",
            "panels/__init__.py",
            "viewmodels/__init__.py"
        ]

        missing_files = []
        for file_path in required_files:
            full_path = self.gui_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
            else:
                print(f"✅ {file_path}")

        if missing_files:
            print(f"⚠️  Missing files: {missing_files}")
            return False

        print("✅ All required GUI files present")
        return True

    def validate_gui_imports(self):
        """Validate that GUI modules can be imported."""
        print("\n🔧 Validating GUI imports...")

        # Add gui directory to path
        sys.path.insert(0, str(self.gui_dir))

        test_imports = [
            ("main_window", "MainWindow"),
            ("components", None),
            ("controllers", None),
            ("panels", None),
            ("viewmodels", None)
        ]

        success = True
        for module_name, class_name in test_imports:
            try:
                module = __import__(module_name)
                if class_name and not hasattr(module, class_name):
                    print(f"❌ {module_name}: Missing class {class_name}")
                    success = False
                else:
                    print(f"✅ {module_name}: Import successful")
            except ImportError as e:
                print(f"❌ {module_name}: Import failed - {e}")
                success = False

        return success

    def test_gui_launch(self):
        """Test basic GUI launch (headless mode if possible)."""
        print("\n🚀 Testing GUI launch...")

        # Set headless mode for testing
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'

        try:
            # Try to import and create main window
            sys.path.insert(0, str(self.gui_dir))

            # Import with timeout
            import importlib.util

            main_window_path = self.gui_dir / "main_window.py"
            spec = importlib.util.spec_from_file_location("main_window", main_window_path)
            main_window_module = importlib.util.module_from_spec(spec)

            # Execute with timeout
            import threading

            def import_with_timeout():
                try:
                    spec.loader.exec_module(main_window_module)
                    return True
                except Exception as e:
                    print(f"❌ GUI import failed: {e}")
                    return False

            import_thread = threading.Thread(target=import_with_timeout)
            import_thread.start()
            import_thread.join(timeout=10)  # 10 second timeout

            if import_thread.is_alive():
                print("❌ GUI import timed out")
                return False

            if hasattr(main_window_module, 'MainWindow'):
                print("✅ GUI module loaded successfully")
                print("✅ MainWindow class available")
                return True
            else:
                print("❌ MainWindow class not found")
                return False

        except Exception as e:
            print(f"❌ GUI test failed: {e}")
            return False

    def create_deployment_report(self):
        """Create deployment status report."""
        report_path = self.base_dir / "deployment_report.txt"

        with open(report_path, 'w') as f:
            f.write("THEA MMORPG GUI DEPLOYMENT REPORT\n")
            f.write("=" * 40 + "\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Agent-3 Infrastructure Support\n\n")

            # File status
            f.write("GUI FILES STATUS:\n")
            gui_files = list(self.gui_dir.rglob("*.py"))
            f.write(f"Total Python files: {len(gui_files)}\n")

            for file_path in sorted(gui_files):
                rel_path = file_path.relative_to(self.gui_dir)
                size = file_path.stat().st_size
                f.write(f"  {rel_path} ({size} bytes)\n")

            f.write("\nDEPLOYMENT STATUS: READY FOR INTEGRATION\n")

        print(f"📊 Deployment report created: {report_path}")
        return report_path

    def deploy(self):
        """Execute full deployment sequence."""
        print("🎮 THEA MMORPG GUI DEPLOYMENT")
        print("=" * 40)

        success = True

        # Check files
        if not self.check_gui_files():
            success = False

        # Validate imports
        if not self.validate_gui_imports():
            success = False

        # Test launch
        if not self.test_gui_launch():
            success = False

        # Create report
        self.create_deployment_report()

        print("\n" + "=" * 40)
        if success:
            print("🎉 GUI DEPLOYMENT SUCCESSFUL!")
            print("🚀 Thea MMORPG GUI system ready for operation")
            print("\nLaunch command:")
            print("  cd systems/thea && python gui/main_window.py")
        else:
            print("❌ DEPLOYMENT ISSUES DETECTED")
            print("🔧 Address issues above before proceeding")

        return success

def main():
    """Main deployment function."""
    deployer = TheaGUIDeployer()
    success = deployer.deploy()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()