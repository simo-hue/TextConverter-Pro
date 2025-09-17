"""
Terminal Application UI (legacy support)
"""

from ..core.converter import TextConverter, ConversionType
from ..core.hotkeys import HotkeyManager
from ..core.autopaste import AutoPaster

class TerminalApp:
    """Terminal-based application interface"""

    def __init__(self):
        self.converter = TextConverter(notification_callback=self.print_notification)
        self.autopaster = AutoPaster()
        self.hotkey_manager = None
        self.running = False

    def setup_hotkeys(self):
        """Initialize hotkey system for terminal app"""
        callback_map = {
            "convert_uppercase": self.handle_conversion,
            "convert_lowercase": self.handle_conversion,
            "convert_capitalize": self.handle_conversion
        }

        self.hotkey_manager = HotkeyManager(callback_map)
        self.hotkey_manager.setup_hotkeys()

    def handle_conversion(self, conversion_type: ConversionType):
        """Handle text conversion"""
        success = self.converter.convert_text(conversion_type)
        if success:
            self.autopaster.paste_converted_text()

    def print_notification(self, title: str, message: str):
        """Print notification to terminal"""
        print(f"{title}: {message}")

    def start(self):
        """Start the terminal application"""
        print("🚀 Text Converter started!")
        print("\n📋 Global Shortcuts:")
        print("   ⌘⇧U = UPPERCASE")
        print("   ⌘⇧L = lowercase")
        print("   ⌘⇧C = Capitalize")
        print("   ⌘⇧Esc = Quit")
        print("\n💡 Usage:")
        print("   1. Select text in any app")
        print("   2. Copy with ⌘C")
        print("   3. Press conversion shortcut")
        print("   4. Text automatically replaced!\n")

        self.setup_hotkeys()
        self.running = True

        try:
            if self.hotkey_manager and self.hotkey_manager.listener:
                self.hotkey_manager.listener.join()
        except KeyboardInterrupt:
            print("\n🛑 Application interrupted by user")
        finally:
            self.stop()

    def stop(self):
        """Stop the application"""
        self.running = False
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        print("👋 Text Converter stopped")