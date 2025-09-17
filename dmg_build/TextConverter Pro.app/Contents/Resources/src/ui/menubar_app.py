"""
macOS Menu Bar Application UI with Professional Preferences
"""

import rumps
from typing import Optional
from pathlib import Path

from ..core.converter import TextConverter, ConversionType
from ..core.hotkeys import HotkeyManager
from ..core.autopaste import AutoPaster
from ..utils.settings import get_settings_manager
from ..utils.logger import get_logger
from ..utils.error_handler import get_error_handler, safe_execute
from ..utils.feedback_system import get_feedback_system
from .preferences_window import PreferencesManager
from .update_manager import UpdateManager
from .notification_manager import get_notification_manager, NotificationType
from .feedback_dialog import get_feedback_dialog

class MenuBarApp(rumps.App):
    """Professional menu bar application with comprehensive settings"""

    def __init__(self):
        # Initialize settings first
        self.settings_manager = get_settings_manager()
        self.logger = get_logger()
        self.feedback_system = get_feedback_system()
        self.notification_manager = get_notification_manager()
        self.feedback_dialog = get_feedback_dialog()
        self.error_handler = get_error_handler(self.show_notification)

        # Get current appearance settings
        appearance = self.settings_manager.settings.appearance

        # Initialize rumps with settings
        super().__init__(
            name="TextConverter",
            title=appearance.menu_bar_title,
            icon=appearance.menu_bar_icon,
            template=True
        )

        # Initialize core components
        self.converter = TextConverter(notification_callback=self.show_notification)
        self.autopaster = AutoPaster()
        self.hotkey_manager = None
        self.preferences_manager = PreferencesManager(self.on_settings_changed)
        self.update_manager = UpdateManager(self.show_notification)

        # Setup
        self.logger.info("Initializing MenuBar App")
        self.setup_menu()
        self.setup_hotkeys()

        # Apply current settings
        self.apply_settings()

    def setup_menu(self):
        """Configure the menu bar dropdown with preferences"""
        appearance = self.settings_manager.settings.appearance
        version = self.settings_manager.settings.version

        # Build menu based on compact mode setting
        if appearance.compact_menu:
            self.menu = self._create_compact_menu()
        else:
            self.menu = self._create_full_menu()

    def _create_full_menu(self) -> list:
        """Create full menu with all options"""
        settings = self.settings_manager.settings
        version = settings.version

        menu_items = [
            rumps.MenuItem(f"TextConverter Pro v{version}", callback=None),
            rumps.separator,
        ]

        # Current hotkeys display
        menu_items.append(rumps.MenuItem("⌨️ Active Hotkeys:", callback=None))
        for conv_type, hotkey in settings.hotkeys.items():
            if hotkey.enabled:
                hotkey_str = self.settings_manager.get_hotkey_string(conv_type)
                display_name = conv_type.replace("_", " ").title()
                menu_items.append(rumps.MenuItem(f"  {display_name}: {hotkey_str}", callback=None))

        menu_items.extend([
            rumps.separator,
            # Quick actions
            rumps.MenuItem("⚡ Quick Actions", callback=None),
            rumps.MenuItem("  🔄 Test Clipboard", callback=self.test_clipboard),
            rumps.MenuItem("  📊 Show Statistics", callback=self.show_statistics),
            rumps.MenuItem("  💡 User Insights", callback=self.show_user_insights),
            rumps.MenuItem("  📈 Detailed Analytics", callback=self.show_detailed_analytics),
            rumps.MenuItem("  ⚡ Performance Metrics", callback=self.show_performance_metrics),
            rumps.MenuItem("  🔧 Restart Hotkeys", callback=self.restart_hotkeys),
            rumps.separator,
            # Preferences and Updates
            self.preferences_manager.create_preferences_menu(),
            self.update_manager.create_update_menu(),
            rumps.separator,
            # Information
            rumps.MenuItem("📊 Status", callback=self.show_status),
            rumps.MenuItem("ℹ️ About", callback=self.show_about),
            rumps.MenuItem("📋 Help", callback=self.show_help),
            rumps.separator,
            # Exit
            rumps.MenuItem("🚪 Quit TextConverter", callback=self.quit_application)
        ])

        return menu_items

    def _create_compact_menu(self) -> list:
        """Create compact menu with essential options only"""
        return [
            rumps.MenuItem("TextConverter Pro", callback=None),
            rumps.separator,
            self.preferences_manager.create_preferences_menu(),
            self.update_manager.create_update_menu(),
            rumps.MenuItem("📊 Status", callback=self.show_status),
            rumps.separator,
            rumps.MenuItem("Quit", callback=self.quit_application)
        ]

    def setup_hotkeys(self):
        """Initialize global hotkey system with settings"""
        try:
            callback_map = {
                "convert_uppercase": self.handle_conversion,
                "convert_lowercase": self.handle_conversion,
                "convert_capitalize": self.handle_conversion
            }

            self.hotkey_manager = HotkeyManager(callback_map)
            self.hotkey_manager.setup_hotkeys()

            self.logger.info("Hotkey system initialized successfully")

        except Exception as e:
            self.logger.error("Failed to setup hotkeys", exception=e)
            self.show_notification("❌ Hotkey Error", "Failed to initialize global hotkeys")

    def handle_conversion(self, conversion_type: ConversionType):
        """Handle text conversion with settings-based behavior"""
        try:
            behavior = self.settings_manager.settings.behavior

            # Check if auto-paste is enabled
            success = self.converter.convert_text(conversion_type)

            if success and behavior.auto_paste:
                self.autopaster.paste_converted_text()

            # Log user action
            self.logger.log_user_action(f"conversion_{conversion_type.value}")

        except Exception as e:
            self.error_handler.handle_error(e, f"handling {conversion_type.value} conversion")

    def show_notification(self, title: str, message: str):
        """Display notification using enhanced notification manager"""
        try:
            # Delegate to enhanced notification manager
            self.notification_manager.show_notification(
                title,
                message,
                NotificationType.INFO
            )

        except Exception as e:
            self.logger.error("Failed to show notification", exception=e)
            # Fallback to basic rumps notification
            rumps.notification(title, None, message, sound=False)

    def apply_settings(self):
        """Apply current settings to the application"""
        try:
            appearance = self.settings_manager.settings.appearance

            # Update menu bar appearance
            if hasattr(self, 'title'):
                self.title = appearance.menu_bar_title
            if hasattr(self, 'icon'):
                self.icon = appearance.menu_bar_icon

            # Refresh menu if needed
            self.setup_menu()

            self.logger.info("Settings applied successfully")

        except Exception as e:
            self.logger.error("Failed to apply settings", exception=e)

    def on_settings_changed(self, settings):
        """Handle settings changes"""
        safe_execute(
            self.apply_settings,
            context="applying settings changes"
        )

        # Restart hotkeys if hotkey settings changed
        safe_execute(
            self.restart_hotkeys,
            None,
            context="restarting hotkeys after settings change"
        )

    # Menu action methods
    def test_clipboard(self, _):
        """Test clipboard functionality"""
        try:
            import pyperclip
            text = pyperclip.paste()

            if text:
                length = len(text)
                preview = text[:50] + "..." if length > 50 else text
                self.show_notification(
                    "📋 Clipboard Test",
                    f"✅ Found {length} characters\nPreview: {preview}"
                )
            else:
                self.show_notification(
                    "📋 Clipboard Test",
                    "❌ No text found in clipboard"
                )

        except Exception as e:
            self.error_handler.handle_error(e, "testing clipboard")

    def show_statistics(self, _):
        """Show comprehensive usage statistics"""
        try:
            # Get usage summary from feedback system
            usage_summary = self.feedback_system.get_usage_summary(30)

            stats_text = f"""📊 TextConverter Statistics (Last 30 Days)

🔄 Conversions:
• Total: {usage_summary['conversions']['total']}
• Successful: {usage_summary['conversions']['successful']}
• Success Rate: {usage_summary['conversions']['success_rate']}%
• Most Used: {usage_summary['conversions']['most_used_type'].title()}
• Avg Speed: {usage_summary['conversions']['avg_processing_time']}s

⌨️ Activity:
• Hotkey Activations: {usage_summary['hotkey_activations']}
• Errors: {usage_summary['errors']['total']}

⚙️ Settings:
• Auto-paste: {'✅' if self.settings_manager.settings.behavior.auto_paste else '❌'}
• Notifications: {'✅' if self.settings_manager.settings.appearance.show_notifications else '❌'}
• Theme: {self.settings_manager.settings.appearance.theme.title()}"""

            rumps.alert("Usage Statistics", stats_text)

        except Exception as e:
            self.error_handler.handle_error(e, "showing statistics")

    def show_user_insights(self, _):
        """Show personalized user experience insights"""
        try:
            insights = self.feedback_system.get_user_experience_insights()

            insights_text = "💡 Personalized Insights\n\n"
            for insight in insights:
                insights_text += f"• {insight}\n"

            if not insights:
                insights_text += "Start using TextConverter to get personalized insights!"

            rumps.alert("User Experience Insights", insights_text)

        except Exception as e:
            self.error_handler.handle_error(e, "showing user insights")

    def show_detailed_analytics(self, _):
        """Show comprehensive analytics with export options"""
        try:
            self.feedback_dialog.show_detailed_statistics()
        except Exception as e:
            self.error_handler.handle_error(e, "showing detailed analytics")

    def show_performance_metrics(self, _):
        """Show performance analysis and optimization tips"""
        try:
            self.feedback_dialog.show_performance_metrics()
        except Exception as e:
            self.error_handler.handle_error(e, "showing performance metrics")

    def restart_hotkeys(self, _):
        """Restart the global hotkey system"""
        try:
            if self.hotkey_manager:
                self.hotkey_manager.restart()

            self.logger.info("Hotkeys restarted by user")
            self.show_notification("🔄 Hotkeys Restarted", "Global hotkeys reloaded successfully")

        except Exception as e:
            self.error_handler.handle_error(e, "restarting hotkeys")

    def show_status(self, _):
        """Show comprehensive application status"""
        try:
            hotkey_status = "✅ Active" if (self.hotkey_manager and self.hotkey_manager.listener) else "❌ Inactive"
            settings_valid = len(self.settings_manager.validate_settings()) == 0
            settings_status = "✅ Valid" if settings_valid else "⚠️ Issues Found"

            status_text = f"""📊 TextConverter Status

🔑 Hotkey System: {hotkey_status}
⚙️ Settings: {settings_status}
🔔 Notifications: {'✅ Enabled' if self.settings_manager.settings.appearance.show_notifications else '❌ Disabled'}
🔄 Auto-paste: {'✅ Enabled' if self.settings_manager.settings.behavior.auto_paste else '❌ Disabled'}

📁 Settings File: {self.settings_manager.settings_file}
📊 Log Directory: ~/Library/Logs/TextConverter"""

            rumps.alert("System Status", status_text)

        except Exception as e:
            self.error_handler.handle_error(e, "showing status")

    def show_about(self, _):
        """Show about dialog with current settings"""
        settings = self.settings_manager.settings
        about_text = f"""TextConverter Pro v{settings.version}

🚀 Professional macOS text transformation tool

✨ Features:
• Customizable global hotkeys
• Multiple notification styles
• Comprehensive preferences
• Professional error handling
• Performance monitoring

⌨️ Active Hotkeys:"""

        for conv_type, hotkey in settings.hotkeys.items():
            if hotkey.enabled:
                key_str = self.settings_manager.get_hotkey_string(conv_type)
                about_text += f"\n• {conv_type.title()}: {key_str}"

        about_text += f"""

📋 Usage:
1. Select text in any application
2. Copy with ⌘C
3. Press conversion hotkey
4. Text automatically transformed!

👨‍💻 Developed by Simone Mattioli
🔧 Built with professional architecture"""

        rumps.alert("About TextConverter Pro", about_text)

    def show_help(self, _):
        """Show help information"""
        help_text = """📋 TextConverter Pro Help

🎯 Quick Start:
1. Select text anywhere on your Mac
2. Copy it with ⌘C
3. Press a conversion hotkey
4. Text is automatically replaced!

⚙️ Customization:
• Go to Preferences to customize hotkeys
• Change notification styles and themes
• Adjust auto-paste behavior
• Configure advanced settings

🔧 Troubleshooting:
• If hotkeys don't work: Check Accessibility permissions
• If auto-paste fails: Adjust paste delay in Preferences
• For other issues: Check Status for diagnostics

🆘 Need Help?
• View log files from Advanced → Diagnostics
• Check system information for compatibility
• Validate settings to find configuration issues"""

        rumps.alert("Help & Support", help_text)

    def quit_application(self, _):
        """Safely quit the application"""
        try:
            self.logger.info("Application quit requested by user")

            # Cleanup resources
            if self.hotkey_manager:
                self.hotkey_manager.stop()

            # Save any pending settings
            self.settings_manager.save_settings()

            self.logger.info("Application cleanup completed")
            rumps.quit_application()

        except Exception as e:
            self.logger.critical("Error during application quit", exception=e)
            rumps.quit_application()

    def cleanup(self):
        """Cleanup resources before quit"""
        safe_execute(
            lambda: self.hotkey_manager.stop() if self.hotkey_manager else None,
            context="cleaning up hotkey manager"
        )

        safe_execute(
            self.settings_manager.save_settings,
            context="saving settings during cleanup"
        )