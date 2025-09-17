"""
Application configuration and constants
"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class AppConfig:
    """Application configuration"""
    app_name: str = "Text Converter"
    app_version: str = "1.0.0"
    bundle_id: str = "com.textconverter.app"
    menu_bar_title: str = "TXT"
    menu_bar_icon: str = "📝"

@dataclass
class HotkeyConfig:
    """Hotkey configuration"""
    uppercase_key: str = "u"
    lowercase_key: str = "l"
    capitalize_key: str = "c"
    modifier_keys: tuple = ("cmd", "shift")

@dataclass
class TimingConfig:
    """Timing configuration for operations"""
    paste_delay: float = 0.05
    key_release_delay: float = 0.02
    notification_duration: int = 3

# Global configuration instances
APP_CONFIG = AppConfig()
HOTKEY_CONFIG = HotkeyConfig()
TIMING_CONFIG = TimingConfig()

# Hotkey descriptions for UI
HOTKEY_DESCRIPTIONS: Dict[str, str] = {
    "uppercase": "⌘⇧U = UPPERCASE",
    "lowercase": "⌘⇧L = lowercase",
    "capitalize": "⌘⇧C = Capitalize"
}