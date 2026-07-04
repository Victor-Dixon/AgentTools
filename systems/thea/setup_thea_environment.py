#!/usr/bin/env python3
"""
Thea MMORPG Environment Setup Script
Infrastructure support provided by Agent-3 (Infrastructure & DevOps)
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Python 3.8+ required for Thea MMORPG")
        return False

    print("✅ Python version compatible")
    return True

def check_pyqt6_installation():
    """Check PyQt6 installation and components."""
    print("\n🔍 Checking PyQt6 installation...")

    components = [
        ('PyQt6', 'PyQt6'),
        ('QtWidgets', 'PyQt6.QtWidgets'),
        ('QtGui', 'PyQt6.QtGui'),
        ('QtCore', 'PyQt6.QtCore'),
        ('QtNetwork', 'PyQt6.QtNetwork'),
    ]

    all_good = True
    for name, module in components:
        try:
            __import__(module)
            print(f"✅ {name}: Available")
        except ImportError:
            print(f"❌ {name}: NOT FOUND")
            all_good = False

    if all_good:
        try:
            import PyQt6.QtCore
            qt_version = PyQt6.QtCore.QT_VERSION_STR
            print(f"🎯 Qt Version: {qt_version}")
        except:
            print("⚠️  Qt version check failed")

    return all_good

def install_dependencies():
    """Install Thea dependencies."""
    print("\n📦 Installing Thea dependencies...")

    requirements_file = Path(__file__).parent / "requirements.txt"

    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directory_structure():
    """Ensure directory structure exists."""
    print("\n🏗️  Verifying directory structure...")

    base_dir = Path(__file__).parent
    directories = [
        "gui/components",
        "gui/controllers",
        "gui/panels",
        "gui/viewmodels",
        "core",
        "models",
        "network",
        "database",
        "assets",
        "config",
        "logs",
        "tests"
    ]

    for dir_path in directories:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ {dir_path}/")

def create_basic_config():
    """Create basic configuration files."""
    print("\n⚙️  Creating basic configuration...")

    config_dir = Path(__file__).parent / "config"
    config_dir.mkdir(exist_ok=True)

    # Create basic config file
    config_content = '''# Thea MMORPG Configuration
[gui]
window_title = Thea MMORPG
window_width = 1200
window_height = 800
theme = dark

[network]
host = localhost
port = 8080
protocol = websocket

[database]
type = sqlite
path = thea.db

[logging]
level = INFO
file = logs/thea.log
'''

    config_file = config_dir / "thea.ini"
    with open(config_file, 'w') as f:
        f.write(config_content)

    print(f"✅ Configuration created: {config_file}")

def main():
    """Main setup function."""
    print("🎮 THEA MMORPG ENVIRONMENT SETUP")
    print("=" * 40)
    print("Infrastructure support by Agent-3 (DevOps)")
    print("=" * 40)

    # Change to script directory
    os.chdir(Path(__file__).parent)

    success = True

    # Check Python version
    if not check_python_version():
        success = False

    # Check PyQt6
    if not check_pyqt6_installation():
        print("\n🔧 Installing missing PyQt6 components...")
        install_dependencies()

        # Re-check after installation
        if not check_pyqt6_installation():
            print("❌ PyQt6 installation failed")
            success = False

    # Create directory structure
    create_directory_structure()

    # Create basic config
    create_basic_config()

    # Final status
    print("\n" + "=" * 40)
    if success:
        print("🎉 THEA ENVIRONMENT SETUP COMPLETE!")
        print("🚀 Ready for GUI system restoration")
        print("\nNext steps:")
        print("1. Run: python systems/thea/gui/main_window.py")
        print("2. Begin GUI component integration")
        print("3. Test basic window functionality")
    else:
        print("❌ SETUP INCOMPLETE - Check errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()