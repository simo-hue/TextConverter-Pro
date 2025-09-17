"""
Professional settings management system for TextConverter Pro
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict, field
from enum import Enum

from .logger import get_logger
from .exceptions import ConfigurationError
from .error_handler import error_boundary, safe_execute

class HotkeyModifier(Enum):
    """Available hotkey modifiers"""
    CMD = "cmd"
    SHIFT = "shift"
    ALT = "alt"
    CTRL = "ctrl"

class NotificationStyle(Enum):
    """Notification display styles"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"
    NONE = "none"

class ThemeMode(Enum):
    """Application theme modes"""
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"

@dataclass
class HotkeyConfig:
    """Configuration for a single hotkey"""
    key: str
    modifiers: List[str] = field(default_factory=lambda: ["cmd", "shift"])
    enabled: bool = True
    description: str = ""

    def __post_init__(self):
        """Validate hotkey configuration"""
        if not self.key or len(self.key) != 1:
            raise ConfigurationError(f"Invalid hotkey key: {self.key}")

        valid_modifiers = [m.value for m in HotkeyModifier]
        for modifier in self.modifiers:
            if modifier not in valid_modifiers:
                raise ConfigurationError(f"Invalid modifier: {modifier}")

@dataclass
class AppearanceConfig:
    """Appearance and UI configuration"""
    theme: str = ThemeMode.SYSTEM.value
    menu_bar_icon: str = "📝"
    menu_bar_title: str = "TXT"
    show_notifications: bool = True
    notification_style: str = NotificationStyle.STANDARD.value
    notification_duration: float = 3.0
    show_conversion_preview: bool = True
    compact_menu: bool = False

@dataclass
class BehaviorConfig:
    """Application behavior configuration"""
    auto_paste: bool = True
    paste_delay: float = 0.05
    max_text_length: int = 1_000_000
    auto_start: bool = False
    check_updates: bool = True
    send_analytics: bool = False
    remember_last_conversion: bool = True
    clipboard_history_size: int = 10
    show_conversion_feedback: bool = True
    enable_rich_notifications: bool = True
    show_performance_metrics: bool = False

@dataclass
class PerformanceConfig:
    """Performance and optimization settings"""
    log_level: str = "INFO"
    max_log_files: int = 10
    log_file_size_mb: int = 10
    cleanup_logs_days: int = 30
    retry_attempts: int = 3
    retry_delay: float = 0.1
    enable_performance_monitoring: bool = False

@dataclass
class TextConverterSettings:
    """Main settings container"""
    # Hotkey configurations
    hotkeys: Dict[str, HotkeyConfig] = field(default_factory=lambda: {
        "uppercase": HotkeyConfig("u", ["cmd", "shift"], True, "Convert to UPPERCASE"),
        "lowercase": HotkeyConfig("l", ["cmd", "shift"], True, "Convert to lowercase"),
        "capitalize": HotkeyConfig("c", ["cmd", "shift"], True, "Convert to Capitalize Case"),
    })

    # Configuration sections
    appearance: AppearanceConfig = field(default_factory=AppearanceConfig)
    behavior: BehaviorConfig = field(default_factory=BehaviorConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)

    # Metadata
    version: str = "1.0.0"
    last_updated: Optional[str] = None

class SettingsManager:
    """Professional settings management with validation and persistence"""

    def __init__(self, app_name: str = "TextConverter"):
        self.app_name = app_name
        self.logger = get_logger()

        # Settings file location
        self.settings_dir = Path.home() / "Library" / "Application Support" / app_name
        self.settings_file = self.settings_dir / "settings.json"
        self.backup_file = self.settings_dir / "settings_backup.json"

        # Create directory if needed
        self.settings_dir.mkdir(parents=True, exist_ok=True)

        # Current settings
        self._settings: Optional[TextConverterSettings] = None
        self._observers: List[callable] = []

        # Load settings
        self.load_settings()

    @property
    def settings(self) -> TextConverterSettings:
        """Get current settings"""
        if self._settings is None:
            self._settings = TextConverterSettings()
        return self._settings

    @error_boundary(context="loading settings", default_return=None)
    def load_settings(self) -> bool:
        """Load settings from file with error handling"""
        try:
            if not self.settings_file.exists():
                self.logger.info("Settings file not found, creating default settings")
                self._settings = TextConverterSettings()
                self.save_settings()
                return True

            with open(self.settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate and convert to settings object
            settings = self._dict_to_settings(data)
            self._settings = settings

            self.logger.info("Settings loaded successfully",
                           file_path=str(self.settings_file))
            return True

        except Exception as e:
            self.logger.error("Failed to load settings", exception=e)

            # Try to load backup
            if self._try_load_backup():
                return True

            # Fall back to defaults
            self.logger.warning("Using default settings due to load failure")
            self._settings = TextConverterSettings()
            return False

    def _try_load_backup(self) -> bool:
        """Try to load settings from backup file"""
        try:
            if not self.backup_file.exists():
                return False

            with open(self.backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            settings = self._dict_to_settings(data)
            self._settings = settings

            self.logger.info("Settings loaded from backup file")
            return True

        except Exception as e:
            self.logger.error("Failed to load backup settings", exception=e)
            return False

    @error_boundary(context="saving settings", default_return=False)
    def save_settings(self) -> bool:
        """Save settings to file with backup"""
        try:
            # Create backup if settings file exists
            if self.settings_file.exists():
                self.settings_file.replace(self.backup_file)

            # Update timestamp
            from datetime import datetime
            self.settings.last_updated = datetime.now().isoformat()

            # Convert to dict and save
            data = self._settings_to_dict(self.settings)

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info("Settings saved successfully",
                           file_path=str(self.settings_file))

            # Notify observers
            self._notify_observers()
            return True

        except Exception as e:
            self.logger.error("Failed to save settings", exception=e)
            raise ConfigurationError(f"Could not save settings: {e}")

    def _dict_to_settings(self, data: Dict[str, Any]) -> TextConverterSettings:
        """Convert dictionary to settings object with validation"""
        try:
            # Handle hotkeys
            hotkeys = {}
            if "hotkeys" in data:
                for key, hotkey_data in data["hotkeys"].items():
                    hotkeys[key] = HotkeyConfig(**hotkey_data)

            # Handle other sections
            appearance = AppearanceConfig(**data.get("appearance", {}))
            behavior = BehaviorConfig(**data.get("behavior", {}))
            performance = PerformanceConfig(**data.get("performance", {}))

            settings = TextConverterSettings(
                hotkeys=hotkeys,
                appearance=appearance,
                behavior=behavior,
                performance=performance,
                version=data.get("version", "1.0.0"),
                last_updated=data.get("last_updated")
            )

            return settings

        except Exception as e:
            raise ConfigurationError(f"Invalid settings format: {e}")

    def _settings_to_dict(self, settings: TextConverterSettings) -> Dict[str, Any]:
        """Convert settings object to dictionary"""
        return {
            "hotkeys": {key: asdict(hotkey) for key, hotkey in settings.hotkeys.items()},
            "appearance": asdict(settings.appearance),
            "behavior": asdict(settings.behavior),
            "performance": asdict(settings.performance),
            "version": settings.version,
            "last_updated": settings.last_updated
        }

    def update_hotkey(self, conversion_type: str, key: str, modifiers: List[str], enabled: bool = True) -> bool:
        """Update hotkey configuration"""
        try:
            if conversion_type not in self.settings.hotkeys:
                raise ConfigurationError(f"Unknown conversion type: {conversion_type}")

            self.settings.hotkeys[conversion_type] = HotkeyConfig(
                key=key,
                modifiers=modifiers,
                enabled=enabled,
                description=self.settings.hotkeys[conversion_type].description
            )

            self.logger.info(f"Updated hotkey for {conversion_type}",
                           key=key, modifiers=modifiers, enabled=enabled)
            return self.save_settings()

        except Exception as e:
            self.logger.error(f"Failed to update hotkey for {conversion_type}", exception=e)
            return False

    def update_appearance(self, **kwargs) -> bool:
        """Update appearance settings"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.settings.appearance, key):
                    setattr(self.settings.appearance, key, value)
                else:
                    raise ConfigurationError(f"Unknown appearance setting: {key}")

            self.logger.info("Updated appearance settings", **kwargs)
            return self.save_settings()

        except Exception as e:
            self.logger.error("Failed to update appearance settings", exception=e)
            return False

    def update_behavior(self, **kwargs) -> bool:
        """Update behavior settings"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.settings.behavior, key):
                    setattr(self.settings.behavior, key, value)
                else:
                    raise ConfigurationError(f"Unknown behavior setting: {key}")

            self.logger.info("Updated behavior settings", **kwargs)
            return self.save_settings()

        except Exception as e:
            self.logger.error("Failed to update behavior settings", exception=e)
            return False

    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        try:
            self._settings = TextConverterSettings()
            self.logger.info("Settings reset to defaults")
            return self.save_settings()

        except Exception as e:
            self.logger.error("Failed to reset settings", exception=e)
            return False

    def export_settings(self, file_path: Union[str, Path]) -> bool:
        """Export settings to file"""
        try:
            export_path = Path(file_path)
            data = self._settings_to_dict(self.settings)

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info("Settings exported successfully",
                           export_path=str(export_path))
            return True

        except Exception as e:
            self.logger.error("Failed to export settings", exception=e)
            return False

    def import_settings(self, file_path: Union[str, Path]) -> bool:
        """Import settings from file"""
        try:
            import_path = Path(file_path)

            if not import_path.exists():
                raise ConfigurationError(f"Import file not found: {import_path}")

            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate imported settings
            settings = self._dict_to_settings(data)
            self._settings = settings

            self.logger.info("Settings imported successfully",
                           import_path=str(import_path))
            return self.save_settings()

        except Exception as e:
            self.logger.error("Failed to import settings", exception=e)
            return False

    def add_observer(self, callback: callable):
        """Add settings change observer"""
        if callback not in self._observers:
            self._observers.append(callback)

    def remove_observer(self, callback: callable):
        """Remove settings change observer"""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self):
        """Notify all observers of settings changes"""
        for callback in self._observers:
            safe_execute(callback, self.settings, context="notifying settings observer")

    def get_hotkey_string(self, conversion_type: str) -> str:
        """Get human-readable hotkey string"""
        if conversion_type not in self.settings.hotkeys:
            return "Not configured"

        hotkey = self.settings.hotkeys[conversion_type]
        if not hotkey.enabled:
            return "Disabled"

        # Convert modifiers to symbols
        modifier_symbols = {
            "cmd": "⌘",
            "shift": "⇧",
            "alt": "⌥",
            "ctrl": "⌃"
        }

        symbols = [modifier_symbols.get(mod, mod) for mod in hotkey.modifiers]
        return "".join(symbols) + hotkey.key.upper()

    def validate_settings(self) -> List[str]:
        """Validate current settings and return list of issues"""
        issues = []

        try:
            # Validate hotkeys
            for conv_type, hotkey in self.settings.hotkeys.items():
                if not hotkey.key or len(hotkey.key) != 1:
                    issues.append(f"Invalid hotkey key for {conv_type}: {hotkey.key}")

            # Validate appearance
            if self.settings.appearance.notification_duration < 0:
                issues.append("Notification duration must be positive")

            # Validate behavior
            if self.settings.behavior.max_text_length < 1:
                issues.append("Max text length must be positive")

            if self.settings.behavior.paste_delay < 0:
                issues.append("Paste delay must be non-negative")

        except Exception as e:
            issues.append(f"Validation error: {e}")

        return issues

# Global settings manager instance
_settings_manager: Optional[SettingsManager] = None

def get_settings_manager() -> SettingsManager:
    """Get or create the global settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager