#!/usr/bin/env python3
"""Check PyQt6 and GUI dependencies for Thea MMORPG restoration."""

import sys
print(f"Python version: {sys.version}")

try:
    import PyQt6
    print("✅ PyQt6: AVAILABLE")
    try:
        print(f"   PyQt6 version: {PyQt6.QtCore.PYQT_VERSION_STR}")
    except AttributeError:
        print("   PyQt6 version: Unable to determine")
except ImportError as e:
    print("❌ PyQt6: NOT AVAILABLE")
    print(f"   Error: {e}")

try:
    import PyQt6.QtWidgets
    print("✅ PyQt6.QtWidgets: AVAILABLE")
except ImportError as e:
    print("❌ PyQt6.QtWidgets: NOT AVAILABLE")

try:
    import PyQt6.QtGui
    print("✅ PyQt6.QtGui: AVAILABLE")
except ImportError as e:
    print("❌ PyQt6.QtGui: NOT AVAILABLE")

try:
    import PyQt6.QtCore
    print("✅ PyQt6.QtCore: AVAILABLE")
    print(f"   Qt version: {PyQt6.QtCore.QT_VERSION_STR}")
except ImportError as e:
    print("❌ PyQt6.QtCore: NOT AVAILABLE")
except AttributeError as e:
    print("❌ PyQt6.QtCore: AVAILABLE but incomplete")
    print(f"   Attribute error: {e}")

# Check for additional GUI dependencies
gui_deps = ['PIL', 'numpy', 'matplotlib']
for dep in gui_deps:
    try:
        __import__(dep)
        print(f"✅ {dep}: AVAILABLE")
    except ImportError:
        print(f"❌ {dep}: NOT AVAILABLE")