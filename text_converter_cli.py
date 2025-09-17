#!/usr/bin/env python3
"""
Text Converter - Terminal Application
Entry point for the terminal version
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.terminal_app import TerminalApp

def main():
    """Main entry point for terminal app"""
    app = TerminalApp()
    try:
        app.start()
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
        app.stop()
    except Exception as e:
        print(f"❌ Error: {e}")
        app.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()