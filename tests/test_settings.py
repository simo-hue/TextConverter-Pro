#!/usr/bin/env python3
"""
Unit tests for settings management system
"""

import unittest
import tempfile
import os
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.settings import (
    SettingsManager, TextConverterSettings, HotkeyConfig,
    AppearanceConfig, BehaviorConfig, PerformanceConfig,
    HotkeyModifier, NotificationStyle, ThemeMode
)
from src.utils.exceptions import ConfigurationError

class TestHotkeyConfig(unittest.TestCase):
    """Test cases for HotkeyConfig"""

    def test_valid_hotkey_config(self):
        """Test valid hotkey configuration"""
        hotkey = HotkeyConfig("u", ["cmd", "shift"], True, "Uppercase")
        self.assertEqual(hotkey.key, "u")
        self.assertEqual(hotkey.modifiers, ["cmd", "shift"])
        self.assertTrue(hotkey.enabled)
        self.assertEqual(hotkey.description, "Uppercase")

    def test_invalid_key(self):
        """Test invalid hotkey key"""
        with self.assertRaises(ConfigurationError):
            HotkeyConfig("", ["cmd", "shift"])

        with self.assertRaises(ConfigurationError):
            HotkeyConfig("ab", ["cmd", "shift"])

    def test_invalid_modifier(self):
        """Test invalid modifier"""
        with self.assertRaises(ConfigurationError):
            HotkeyConfig("u", ["invalid_modifier"])

class TestSettingsStructures(unittest.TestCase):
    """Test cases for settings data structures"""

    def test_appearance_config_defaults(self):
        """Test AppearanceConfig defaults"""
        config = AppearanceConfig()
        self.assertEqual(config.theme, ThemeMode.SYSTEM.value)
        self.assertEqual(config.menu_bar_icon, "📝")
        self.assertEqual(config.menu_bar_title, "TXT")
        self.assertTrue(config.show_notifications)
        self.assertEqual(config.notification_style, NotificationStyle.STANDARD.value)

    def test_behavior_config_defaults(self):
        """Test BehaviorConfig defaults"""
        config = BehaviorConfig()
        self.assertTrue(config.auto_paste)
        self.assertEqual(config.paste_delay, 0.05)
        self.assertEqual(config.max_text_length, 1_000_000)
        self.assertFalse(config.auto_start)
        self.assertTrue(config.check_updates)

    def test_performance_config_defaults(self):
        """Test PerformanceConfig defaults"""
        config = PerformanceConfig()
        self.assertEqual(config.log_level, "INFO")
        self.assertEqual(config.max_log_files, 10)
        self.assertEqual(config.log_file_size_mb, 10)
        self.assertEqual(config.retry_attempts, 3)

    def test_text_converter_settings_defaults(self):
        """Test TextConverterSettings default values"""
        settings = TextConverterSettings()

        # Check default hotkeys
        self.assertIn("uppercase", settings.hotkeys)
        self.assertIn("lowercase", settings.hotkeys)
        self.assertIn("capitalize", settings.hotkeys)

        # Check hotkey values
        uppercase_hotkey = settings.hotkeys["uppercase"]
        self.assertEqual(uppercase_hotkey.key, "u")
        self.assertEqual(uppercase_hotkey.modifiers, ["cmd", "shift"])
        self.assertTrue(uppercase_hotkey.enabled)

class TestSettingsManager(unittest.TestCase):
    """Test cases for SettingsManager"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test settings
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = Path(self.temp_dir) / "settings.json"

        # Mock the settings directory
        self.settings_manager = SettingsManager("TestApp")
        self.settings_manager.settings_dir = Path(self.temp_dir)
        self.settings_manager.settings_file = self.settings_file
        self.settings_manager.backup_file = Path(self.temp_dir) / "settings_backup.json"

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_nonexistent_settings(self):
        """Test loading settings when file doesn't exist"""
        # Clear any existing settings
        self.settings_manager._settings = None

        result = self.settings_manager.load_settings()
        self.assertTrue(result)
        self.assertIsNotNone(self.settings_manager.settings)
        self.assertTrue(self.settings_file.exists())

    def test_save_and_load_settings(self):
        """Test saving and loading settings"""
        # Modify settings
        self.settings_manager.settings.appearance.theme = ThemeMode.DARK.value
        self.settings_manager.settings.behavior.auto_paste = False

        # Save settings
        result = self.settings_manager.save_settings()
        self.assertTrue(result)
        self.assertTrue(self.settings_file.exists())

        # Create new manager and load
        new_manager = SettingsManager("TestApp")
        new_manager.settings_dir = Path(self.temp_dir)
        new_manager.settings_file = self.settings_file
        new_manager.backup_file = Path(self.temp_dir) / "settings_backup.json"

        result = new_manager.load_settings()
        self.assertTrue(result)
        self.assertEqual(new_manager.settings.appearance.theme, ThemeMode.DARK.value)
        self.assertFalse(new_manager.settings.behavior.auto_paste)

    def test_update_hotkey(self):
        """Test updating hotkey configuration"""
        result = self.settings_manager.update_hotkey("uppercase", "y", ["cmd", "alt"], True)
        self.assertTrue(result)

        hotkey = self.settings_manager.settings.hotkeys["uppercase"]
        self.assertEqual(hotkey.key, "y")
        self.assertEqual(hotkey.modifiers, ["cmd", "alt"])
        self.assertTrue(hotkey.enabled)

    def test_update_appearance(self):
        """Test updating appearance settings"""
        result = self.settings_manager.update_appearance(
            theme=ThemeMode.LIGHT.value,
            menu_bar_icon="🔧",
            show_notifications=False
        )
        self.assertTrue(result)

        appearance = self.settings_manager.settings.appearance
        self.assertEqual(appearance.theme, ThemeMode.LIGHT.value)
        self.assertEqual(appearance.menu_bar_icon, "🔧")
        self.assertFalse(appearance.show_notifications)

    def test_update_behavior(self):
        """Test updating behavior settings"""
        result = self.settings_manager.update_behavior(
            auto_paste=False,
            paste_delay=0.1,
            max_text_length=500_000
        )
        self.assertTrue(result)

        behavior = self.settings_manager.settings.behavior
        self.assertFalse(behavior.auto_paste)
        self.assertEqual(behavior.paste_delay, 0.1)
        self.assertEqual(behavior.max_text_length, 500_000)

    def test_reset_to_defaults(self):
        """Test resetting settings to defaults"""
        # Modify settings
        self.settings_manager.settings.appearance.theme = ThemeMode.DARK.value
        self.settings_manager.settings.behavior.auto_paste = False

        # Reset to defaults
        result = self.settings_manager.reset_to_defaults()
        self.assertTrue(result)

        # Check that settings are back to defaults
        self.assertEqual(self.settings_manager.settings.appearance.theme, ThemeMode.SYSTEM.value)
        self.assertTrue(self.settings_manager.settings.behavior.auto_paste)

    def test_get_hotkey_string(self):
        """Test getting human-readable hotkey string"""
        # Test enabled hotkey
        hotkey_str = self.settings_manager.get_hotkey_string("uppercase")
        self.assertEqual(hotkey_str, "⌘⇧U")

        # Test disabled hotkey
        self.settings_manager.settings.hotkeys["uppercase"].enabled = False
        hotkey_str = self.settings_manager.get_hotkey_string("uppercase")
        self.assertEqual(hotkey_str, "Disabled")

        # Test non-existent hotkey
        hotkey_str = self.settings_manager.get_hotkey_string("nonexistent")
        self.assertEqual(hotkey_str, "Not configured")

    def test_validate_settings(self):
        """Test settings validation"""
        # Valid settings should return no issues
        issues = self.settings_manager.validate_settings()
        self.assertEqual(len(issues), 0)

        # Invalid settings should return issues
        self.settings_manager.settings.hotkeys["uppercase"].key = ""
        self.settings_manager.settings.behavior.max_text_length = -1

        issues = self.settings_manager.validate_settings()
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("Invalid hotkey key" in issue for issue in issues))
        self.assertTrue(any("Max text length must be positive" in issue for issue in issues))

    def test_export_import_settings(self):
        """Test exporting and importing settings"""
        # Modify settings
        self.settings_manager.settings.appearance.theme = ThemeMode.DARK.value
        self.settings_manager.settings.behavior.auto_paste = False

        # Export settings
        export_file = Path(self.temp_dir) / "export.json"
        result = self.settings_manager.export_settings(export_file)
        self.assertTrue(result)
        self.assertTrue(export_file.exists())

        # Reset settings
        self.settings_manager.reset_to_defaults()

        # Import settings
        result = self.settings_manager.import_settings(export_file)
        self.assertTrue(result)

        # Check imported values
        self.assertEqual(self.settings_manager.settings.appearance.theme, ThemeMode.DARK.value)
        self.assertFalse(self.settings_manager.settings.behavior.auto_paste)

    def test_settings_observer(self):
        """Test settings change observer"""
        observer_called = False
        observer_settings = None

        def test_observer(settings):
            nonlocal observer_called, observer_settings
            observer_called = True
            observer_settings = settings

        # Add observer
        self.settings_manager.add_observer(test_observer)

        # Trigger settings change
        self.settings_manager.save_settings()

        # Check observer was called
        self.assertTrue(observer_called)
        self.assertIsNotNone(observer_settings)

        # Remove observer
        self.settings_manager.remove_observer(test_observer)
        observer_called = False

        # Trigger settings change again
        self.settings_manager.save_settings()

        # Observer should not be called
        self.assertFalse(observer_called)

    def test_corrupted_settings_file(self):
        """Test handling of corrupted settings file"""
        # Create corrupted settings file
        with open(self.settings_file, 'w') as f:
            f.write("invalid json content")

        # Should fall back to defaults
        self.settings_manager._settings = None
        result = self.settings_manager.load_settings()

        # Should handle gracefully
        self.assertIsNotNone(self.settings_manager.settings)

    def test_dict_conversion(self):
        """Test conversion between settings object and dictionary"""
        # Get original settings
        original_settings = self.settings_manager.settings

        # Convert to dict and back
        settings_dict = self.settings_manager._settings_to_dict(original_settings)
        restored_settings = self.settings_manager._dict_to_settings(settings_dict)

        # Check that all values are preserved
        self.assertEqual(restored_settings.appearance.theme, original_settings.appearance.theme)
        self.assertEqual(restored_settings.behavior.auto_paste, original_settings.behavior.auto_paste)
        self.assertEqual(len(restored_settings.hotkeys), len(original_settings.hotkeys))

        for key in original_settings.hotkeys:
            original_hotkey = original_settings.hotkeys[key]
            restored_hotkey = restored_settings.hotkeys[key]
            self.assertEqual(original_hotkey.key, restored_hotkey.key)
            self.assertEqual(original_hotkey.modifiers, restored_hotkey.modifiers)
            self.assertEqual(original_hotkey.enabled, restored_hotkey.enabled)

if __name__ == "__main__":
    unittest.main()