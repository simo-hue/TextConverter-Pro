#!/usr/bin/env python3
"""
TextConverter Pro Launcher
Main entry point that handles imports correctly for py2app
"""

import sys
import os
from pathlib import Path

def main():
    """Main launcher that sets up proper Python path and imports"""

    # Add the current directory and src directory to Python path
    current_dir = Path(__file__).parent
    src_dir = current_dir / "src"

    # Add to sys.path if not already there
    paths_to_add = [str(current_dir), str(src_dir)]
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)

    try:
        # Import and run the main menu bar app
        from src.ui.menubar_app import MenuBarApp

        # Create and run the application
        app = MenuBarApp()
        app.run()

    except ImportError as e:
        print(f"Import error: {e}")
        print("Python path:", sys.path)

        # Fallback: try to run with alternative imports
        try:
            import src.ui.menubar_app as menubar_module
            app = menubar_module.MenuBarApp()
            app.run()
        except Exception as fallback_error:
            print(f"Fallback failed: {fallback_error}")
            sys.exit(1)

    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()