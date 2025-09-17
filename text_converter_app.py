#!/usr/bin/env python3
"""
Text Converter - macOS Menu Bar Application
Entry point for the menu bar version
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.menubar_app import MenuBarApp
from src.utils.logger import get_logger, setup_global_exception_handler
from src.utils.error_handler import get_error_handler

def main():
    """Main entry point for menu bar app with comprehensive error handling"""
    # Setup global exception handling
    setup_global_exception_handler()

    # Initialize logger
    logger = get_logger(debug_mode='--debug' in sys.argv)
    logger.log_system_info()

    # Initialize error handler
    error_handler = get_error_handler()

    try:
        logger.info("Starting TextConverter Menu Bar App")
        app = MenuBarApp()
        app.run()

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n🛑 Application interrupted")

    except Exception as e:
        logger.critical("Failed to start application", exception=e)
        error_handler.handle_error(e, "starting application", critical=True)
        print(f"❌ Critical error starting app: {e}")
        sys.exit(1)

    finally:
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main()