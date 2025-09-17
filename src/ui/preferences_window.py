"""
Professional preferences window for TextConverter Pro
"""

import rumps
from typing import Dict, Any, Callable, Optional
from ..utils.settings import get_settings_manager, HotkeyModifier, NotificationStyle, ThemeMode
from ..utils.logger import get_logger
from ..utils.error_handler import safe_execute

class PreferencesManager:
    """Manages preferences UI and interactions"""

    def __init__(self, settings_change_callback: Optional[Callable] = None):
        self.settings_manager = get_settings_manager()
        self.logger = get_logger()
        self.settings_change_callback = settings_change_callback

        # Subscribe to settings changes
        self.settings_manager.add_observer(self._on_settings_changed)

    def create_preferences_menu(self) -> rumps.MenuItem:
        """Create the main preferences menu"""
        prefs_menu = rumps.MenuItem("⚙️ Preferences")

        # Hotkeys submenu
        hotkeys_menu = rumps.MenuItem("⌨️ Hotkeys")
        hotkeys_menu.add(self._create_hotkeys_submenu())

        # Appearance submenu
        appearance_menu = rumps.MenuItem("🎨 Appearance")
        appearance_menu.add(self._create_appearance_submenu())

        # Behavior submenu
        behavior_menu = rumps.MenuItem("⚡ Behavior")
        behavior_menu.add(self._create_behavior_submenu())

        # Advanced submenu
        advanced_menu = rumps.MenuItem("🔧 Advanced")
        advanced_menu.add(self._create_advanced_submenu())

        # Settings management
        settings_menu = rumps.MenuItem("💾 Settings")
        settings_menu.add([
            rumps.MenuItem("Export Settings...", callback=self._export_settings),
            rumps.MenuItem("Import Settings...", callback=self._import_settings),
            rumps.separator,
            rumps.MenuItem("Reset to Defaults", callback=self._reset_settings),
        ])

        # Add all submenus
        prefs_menu.add([
            hotkeys_menu,
            appearance_menu,
            behavior_menu,
            advanced_menu,
            rumps.separator,
            settings_menu,
        ])

        return prefs_menu

    def _create_hotkeys_submenu(self) -> list:
        """Create hotkeys configuration submenu"""
        settings = self.settings_manager.settings
        items = []

        # Current hotkey display
        items.append(rumps.MenuItem("Current Hotkeys:", callback=None))

        for conv_type, hotkey in settings.hotkeys.items():
            hotkey_str = self.settings_manager.get_hotkey_string(conv_type)
            status = "✅" if hotkey.enabled else "❌"
            display_name = conv_type.replace("_", " ").title()

            item_text = f"{status} {display_name}: {hotkey_str}"
            items.append(rumps.MenuItem(item_text, callback=None))

        items.append(rumps.separator)

        # Hotkey configuration options
        items.extend([
            rumps.MenuItem("📝 Customize Uppercase Hotkey", callback=lambda _: self._customize_hotkey("uppercase")),
            rumps.MenuItem("📝 Customize Lowercase Hotkey", callback=lambda _: self._customize_hotkey("lowercase")),
            rumps.MenuItem("📝 Customize Capitalize Hotkey", callback=lambda _: self._customize_hotkey("capitalize")),
            rumps.separator,
            rumps.MenuItem("🔄 Reset Hotkeys to Default", callback=self._reset_hotkeys),
        ])

        return items

    def _create_appearance_submenu(self) -> list:
        """Create appearance configuration submenu"""
        settings = self.settings_manager.settings.appearance
        items = []

        # Theme selection
        items.append(rumps.MenuItem("🌓 Theme:", callback=None))

        for theme in ThemeMode:
            is_current = settings.theme == theme.value
            prefix = "●" if is_current else "○"
            theme_name = theme.value.title()

            items.append(rumps.MenuItem(
                f"  {prefix} {theme_name}",
                callback=lambda sender, t=theme.value: self._set_theme(t)
            ))

        items.append(rumps.separator)

        # Menu bar customization
        items.extend([
            rumps.MenuItem("📱 Menu Bar:", callback=None),
            rumps.MenuItem(f"  Icon: {settings.menu_bar_icon}", callback=self._customize_menu_icon),
            rumps.MenuItem(f"  Title: '{settings.menu_bar_title}'", callback=self._customize_menu_title),
            rumps.MenuItem(f"  {'✅' if settings.compact_menu else '❌'} Compact Menu",
                         callback=self._toggle_compact_menu),
            rumps.separator,
        ])

        # Notifications
        items.append(rumps.MenuItem("🔔 Notifications:", callback=None))

        # Notification style
        for style in NotificationStyle:
            is_current = settings.notification_style == style.value
            prefix = "●" if is_current else "○"
            style_name = style.value.title()

            items.append(rumps.MenuItem(
                f"  {prefix} {style_name}",
                callback=lambda sender, s=style.value: self._set_notification_style(s)
            ))

        items.extend([
            rumps.separator,
            rumps.MenuItem(f"  {'✅' if settings.show_notifications else '❌'} Enable Notifications",
                         callback=self._toggle_notifications),
            rumps.MenuItem(f"  Duration: {settings.notification_duration}s",
                         callback=self._set_notification_duration),
        ])

        return items

    def _create_behavior_submenu(self) -> list:
        """Create behavior configuration submenu"""
        settings = self.settings_manager.settings.behavior
        items = []

        # Auto-paste settings
        items.extend([
            rumps.MenuItem("🔄 Auto-Paste:", callback=None),
            rumps.MenuItem(f"  {'✅' if settings.auto_paste else '❌'} Enable Auto-Paste",
                         callback=self._toggle_auto_paste),
            rumps.MenuItem(f"  Delay: {int(settings.paste_delay * 1000)}ms",
                         callback=self._set_paste_delay),
            rumps.separator,
        ])

        # Text processing
        items.extend([
            rumps.MenuItem("📝 Text Processing:", callback=None),
            rumps.MenuItem(f"  Max Length: {settings.max_text_length:,} chars",
                         callback=self._set_max_text_length),
            rumps.MenuItem(f"  {'✅' if settings.remember_last_conversion else '❌'} Remember Last Conversion",
                         callback=self._toggle_remember_conversion),
            rumps.MenuItem(f"  History Size: {settings.clipboard_history_size}",
                         callback=self._set_history_size),
            rumps.separator,
        ])

        # System integration
        items.extend([
            rumps.MenuItem("🖥️ System:", callback=None),
            rumps.MenuItem(f"  {'✅' if settings.auto_start else '❌'} Start at Login",
                         callback=self._toggle_auto_start),
            rumps.MenuItem(f"  {'✅' if settings.check_updates else '❌'} Check for Updates",
                         callback=self._toggle_check_updates),
            rumps.MenuItem(f"  {'✅' if settings.send_analytics else '❌'} Send Anonymous Analytics",
                         callback=self._toggle_analytics),
        ])

        return items

    def _create_advanced_submenu(self) -> list:
        """Create advanced configuration submenu"""
        settings = self.settings_manager.settings.performance
        items = []

        # Logging settings
        items.extend([
            rumps.MenuItem("📊 Logging:", callback=None),
            rumps.MenuItem(f"  Level: {settings.log_level}", callback=self._set_log_level),
            rumps.MenuItem(f"  Max Files: {settings.max_log_files}", callback=self._set_max_log_files),
            rumps.MenuItem(f"  File Size: {settings.log_file_size_mb}MB", callback=self._set_log_file_size),
            rumps.MenuItem(f"  Cleanup: {settings.cleanup_logs_days} days", callback=self._set_cleanup_days),
            rumps.separator,
        ])

        # Performance settings
        items.extend([
            rumps.MenuItem("⚡ Performance:", callback=None),
            rumps.MenuItem(f"  Retry Attempts: {settings.retry_attempts}", callback=self._set_retry_attempts),
            rumps.MenuItem(f"  Retry Delay: {int(settings.retry_delay * 1000)}ms", callback=self._set_retry_delay),
            rumps.MenuItem(f"  {'✅' if settings.enable_performance_monitoring else '❌'} Performance Monitoring",
                         callback=self._toggle_performance_monitoring),
            rumps.separator,
        ])

        # Diagnostics
        items.extend([
            rumps.MenuItem("🔍 Diagnostics:", callback=None),
            rumps.MenuItem("View Log Files", callback=self._view_logs),
            rumps.MenuItem("System Information", callback=self._show_system_info),
            rumps.MenuItem("Validate Settings", callback=self._validate_settings),
        ])

        return items

    # Hotkey configuration methods
    def _customize_hotkey(self, conversion_type: str):
        """Show hotkey customization dialog"""
        current_hotkey = self.settings_manager.settings.hotkeys.get(conversion_type)
        if not current_hotkey:
            return

        current_str = self.settings_manager.get_hotkey_string(conversion_type)

        # Create simple input dialog using rumps
        response = rumps.Window(
            title=f"Customize {conversion_type.title()} Hotkey",
            message=f"Current hotkey: {current_str}\n\nEnter new key (single letter):",
            default_text=current_hotkey.key,
            dimensions=(350, 100)
        ).run()

        if response.clicked and response.text:
            new_key = response.text.lower().strip()
            if len(new_key) == 1 and new_key.isalpha():
                success = self.settings_manager.update_hotkey(
                    conversion_type, new_key, current_hotkey.modifiers, current_hotkey.enabled
                )
                if success:
                    self._show_success_notification(f"Hotkey updated for {conversion_type}")
                else:
                    self._show_error_notification("Failed to update hotkey")
            else:
                self._show_error_notification("Please enter a single letter")

    def _reset_hotkeys(self, _):
        """Reset all hotkeys to defaults"""
        result = rumps.alert(
            title="Reset Hotkeys",
            message="Are you sure you want to reset all hotkeys to defaults?",
            ok="Reset",
            cancel="Cancel"
        )

        if result == 1:  # OK clicked
            # Reset to default hotkeys
            self.settings_manager.settings.hotkeys = {
                "uppercase": self.settings_manager.settings.hotkeys["uppercase"].__class__("u", ["cmd", "shift"], True, "Convert to UPPERCASE"),
                "lowercase": self.settings_manager.settings.hotkeys["lowercase"].__class__("l", ["cmd", "shift"], True, "Convert to lowercase"),
                "capitalize": self.settings_manager.settings.hotkeys["capitalize"].__class__("c", ["cmd", "shift"], True, "Convert to Capitalize Case"),
            }

            if self.settings_manager.save_settings():
                self._show_success_notification("Hotkeys reset to defaults")
            else:
                self._show_error_notification("Failed to reset hotkeys")

    # Appearance configuration methods
    def _set_theme(self, theme: str):
        """Set application theme"""
        if self.settings_manager.update_appearance(theme=theme):
            self._show_success_notification(f"Theme changed to {theme.title()}")

    def _customize_menu_icon(self, _):
        """Customize menu bar icon"""
        response = rumps.Window(
            title="Menu Bar Icon",
            message="Enter emoji or text for menu bar icon:",
            default_text=self.settings_manager.settings.appearance.menu_bar_icon,
            dimensions=(300, 100)
        ).run()

        if response.clicked and response.text:
            if self.settings_manager.update_appearance(menu_bar_icon=response.text):
                self._show_success_notification("Menu bar icon updated")

    def _customize_menu_title(self, _):
        """Customize menu bar title"""
        response = rumps.Window(
            title="Menu Bar Title",
            message="Enter title for menu bar (leave empty for icon only):",
            default_text=self.settings_manager.settings.appearance.menu_bar_title,
            dimensions=(300, 100)
        ).run()

        if response.clicked:
            if self.settings_manager.update_appearance(menu_bar_title=response.text or ""):
                self._show_success_notification("Menu bar title updated")

    def _toggle_compact_menu(self, _):
        """Toggle compact menu mode"""
        current = self.settings_manager.settings.appearance.compact_menu
        if self.settings_manager.update_appearance(compact_menu=not current):
            status = "enabled" if not current else "disabled"
            self._show_success_notification(f"Compact menu {status}")

    def _set_notification_style(self, style: str):
        """Set notification style"""
        if self.settings_manager.update_appearance(notification_style=style):
            self._show_success_notification(f"Notification style: {style.title()}")

    def _toggle_notifications(self, _):
        """Toggle notifications on/off"""
        current = self.settings_manager.settings.appearance.show_notifications
        if self.settings_manager.update_appearance(show_notifications=not current):
            status = "enabled" if not current else "disabled"
            self._show_success_notification(f"Notifications {status}")

    def _set_notification_duration(self, _):
        """Set notification duration"""
        current = self.settings_manager.settings.appearance.notification_duration
        response = rumps.Window(
            title="Notification Duration",
            message="Enter duration in seconds:",
            default_text=str(current),
            dimensions=(300, 100)
        ).run()

        if response.clicked and response.text:
            try:
                duration = float(response.text)
                if 0.5 <= duration <= 10:
                    if self.settings_manager.update_appearance(notification_duration=duration):
                        self._show_success_notification(f"Notification duration: {duration}s")
                else:
                    self._show_error_notification("Duration must be between 0.5 and 10 seconds")
            except ValueError:
                self._show_error_notification("Please enter a valid number")

    # Behavior configuration methods (implementing key methods)
    def _toggle_auto_paste(self, _):
        """Toggle auto-paste functionality"""
        current = self.settings_manager.settings.behavior.auto_paste
        if self.settings_manager.update_behavior(auto_paste=not current):
            status = "enabled" if not current else "disabled"
            self._show_success_notification(f"Auto-paste {status}")

    def _toggle_auto_start(self, _):
        """Toggle auto-start at login"""
        current = self.settings_manager.settings.behavior.auto_start
        if self.settings_manager.update_behavior(auto_start=not current):
            status = "enabled" if not current else "disabled"
            self._show_success_notification(f"Auto-start {status}")

            if not current:
                rumps.alert(
                    title="Auto-Start Enabled",
                    message="To complete setup, add TextConverter to Login Items in System Preferences → Users & Groups."
                )

    # Settings management methods
    def _export_settings(self, _):
        """Export settings to file"""
        # Simple filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"TextConverter_Settings_{timestamp}.json"

        # For now, save to Desktop (in a real app, use file dialog)
        desktop = Path.home() / "Desktop"
        export_path = desktop / filename

        if self.settings_manager.export_settings(export_path):
            rumps.alert(
                title="Settings Exported",
                message=f"Settings exported to:\n{export_path}"
            )
        else:
            self._show_error_notification("Failed to export settings")

    def _import_settings(self, _):
        """Import settings from file"""
        # In a real implementation, this would use a file dialog
        rumps.alert(
            title="Import Settings",
            message="Feature coming soon!\n\nFor now, manually place settings file in:\n~/Library/Application Support/TextConverter/"
        )

    def _reset_settings(self, _):
        """Reset all settings to defaults"""
        result = rumps.alert(
            title="Reset Settings",
            message="Are you sure you want to reset ALL settings to defaults?\n\nThis cannot be undone.",
            ok="Reset All",
            cancel="Cancel"
        )

        if result == 1:  # OK clicked
            if self.settings_manager.reset_to_defaults():
                self._show_success_notification("All settings reset to defaults")
            else:
                self._show_error_notification("Failed to reset settings")

    # Utility methods
    def _show_success_notification(self, message: str):
        """Show success notification"""
        rumps.notification("✅ Settings Updated", None, message, sound=False)

    def _show_error_notification(self, message: str):
        """Show error notification"""
        rumps.notification("❌ Settings Error", None, message, sound=False)

    def _validate_settings(self, _):
        """Validate current settings"""
        issues = self.settings_manager.validate_settings()

        if not issues:
            rumps.alert(
                title="Settings Validation",
                message="✅ All settings are valid!"
            )
        else:
            issue_text = "\n• ".join([""] + issues)
            rumps.alert(
                title="Settings Issues Found",
                message=f"The following issues were found:{issue_text}"
            )

    def _show_system_info(self, _):
        """Show system information"""
        import platform
        try:
            import psutil
            cpu_count = psutil.cpu_count()
            memory_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        except:
            cpu_count = "Unknown"
            memory_gb = "Unknown"

        info = f"""System Information:

Platform: {platform.platform()}
Python: {platform.python_version()}
CPU Cores: {cpu_count}
Memory: {memory_gb} GB

Settings File: {self.settings_manager.settings_file}
Log Directory: {self.settings_manager.settings_dir}"""

        rumps.alert(title="System Information", message=info)

    def _view_logs(self, _):
        """Open log directory in Finder"""
        log_dir = Path.home() / "Library" / "Logs" / "TextConverter"
        os.system(f'open "{log_dir}"')

    def _on_settings_changed(self, settings):
        """Handle settings changes"""
        self.logger.info("Settings changed, notifying callback")
        if self.settings_change_callback:
            safe_execute(
                self.settings_change_callback,
                settings,
                context="handling settings change"
            )