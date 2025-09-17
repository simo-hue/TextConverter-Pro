"""
Advanced Notification System with Rich User Feedback
"""

import rumps
import time
from enum import Enum
from typing import Optional, Dict, Callable, Any
from dataclasses import dataclass
from pathlib import Path

from ..utils.logger import get_logger
from ..utils.settings import get_settings_manager

class NotificationType(Enum):
    """Types of notifications with different priorities and styles"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    CONVERSION = "conversion"
    UPDATE = "update"
    SYSTEM = "system"

@dataclass
class NotificationConfig:
    """Configuration for different notification types"""
    icon: str
    sound: bool
    duration: float
    style: str
    priority: int

class NotificationManager:
    """Professional notification system with enhanced user feedback"""

    def __init__(self):
        self.logger = get_logger()
        self.settings_manager = get_settings_manager()

        # Notification configurations by type
        self.configs = {
            NotificationType.SUCCESS: NotificationConfig("✅", False, 2.0, "success", 3),
            NotificationType.ERROR: NotificationConfig("❌", True, 5.0, "error", 1),
            NotificationType.WARNING: NotificationConfig("⚠️", False, 3.0, "warning", 2),
            NotificationType.INFO: NotificationConfig("ℹ️", False, 2.5, "info", 4),
            NotificationType.CONVERSION: NotificationConfig("🔄", False, 1.5, "conversion", 5),
            NotificationType.UPDATE: NotificationConfig("🚀", False, 4.0, "update", 2),
            NotificationType.SYSTEM: NotificationConfig("⚙️", False, 3.0, "system", 3)
        }

        # Track recent notifications to avoid spam
        self.recent_notifications = {}
        self.notification_history = []

    def show_notification(
        self,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        force: bool = False,
        action_callback: Optional[Callable] = None
    ) -> bool:
        """
        Show enhanced notification with improved user experience

        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            force: Force show even if notifications disabled
            action_callback: Optional callback for notification actions

        Returns:
            True if notification was shown, False otherwise
        """
        try:
            settings = self.settings_manager.settings
            appearance = settings.appearance

            # Check if notifications are globally disabled
            if not appearance.show_notifications and not force:
                self.logger.debug("Notification skipped - disabled in settings", title=title)
                return False

            # Check notification style filtering
            if not self._should_show_notification(notification_type, appearance.notification_style):
                self.logger.debug("Notification filtered by style", type=notification_type.value)
                return False

            # Check for duplicate/spam prevention
            if not force and self._is_duplicate_notification(title, message):
                self.logger.debug("Duplicate notification prevented", title=title)
                return False

            # Get configuration for this notification type
            config = self.configs[notification_type]

            # Format title with icon
            formatted_title = f"{config.icon} {title}"

            # Show the notification
            self._display_notification(
                formatted_title,
                message,
                config,
                action_callback
            )

            # Track notification
            self._track_notification(title, message, notification_type)

            self.logger.debug("Notification shown", title=title, type=notification_type.value)
            return True

        except Exception as e:
            self.logger.error("Failed to show notification", exception=e, title=title)
            return False

    def show_conversion_feedback(
        self,
        conversion_type: str,
        text_length: int,
        processing_time: float = 0.0
    ):
        """Show optimized feedback for text conversion operations"""
        try:
            settings = self.settings_manager.settings.behavior

            if settings.show_conversion_feedback:
                # Create informative conversion message
                type_display = conversion_type.replace("_", " ").title()

                if text_length > 0:
                    message = f"Converted {text_length} characters to {type_display.lower()}"
                    if processing_time > 0:
                        message += f" ({processing_time:.2f}s)"
                else:
                    message = "No text found in clipboard"

                self.show_notification(
                    "Text Conversion",
                    message,
                    NotificationType.CONVERSION
                )

        except Exception as e:
            self.logger.error("Failed to show conversion feedback", exception=e)

    def show_error_with_recovery(
        self,
        error_title: str,
        error_message: str,
        recovery_actions: Optional[Dict[str, Callable]] = None
    ):
        """Show error notification with recovery suggestions"""
        try:
            # Format error message with recovery options
            full_message = error_message

            if recovery_actions:
                full_message += "\n\nSuggested actions:"
                for action_name in recovery_actions.keys():
                    full_message += f"\n• {action_name}"

            # Show error notification
            success = self.show_notification(
                error_title,
                full_message,
                NotificationType.ERROR,
                force=True  # Always show errors
            )

            # Log comprehensive error information
            if success:
                self.logger.error(
                    "Error notification shown to user",
                    error_title=error_title,
                    recovery_options=list(recovery_actions.keys()) if recovery_actions else None
                )

        except Exception as e:
            self.logger.critical("Failed to show error notification", exception=e)

    def show_update_available(
        self,
        current_version: str,
        new_version: str,
        release_notes: str
    ):
        """Show rich update notification with release information"""
        try:
            title = "Update Available"
            message = f"""Version {new_version} is now available!

Current: v{current_version}
New: v{new_version}

{release_notes[:200]}{'...' if len(release_notes) > 200 else ''}

Click to download from GitHub"""

            self.show_notification(
                title,
                message,
                NotificationType.UPDATE,
                force=True
            )

        except Exception as e:
            self.logger.error("Failed to show update notification", exception=e)

    def show_system_status(
        self,
        status_title: str,
        components: Dict[str, bool],
        details: Optional[str] = None
    ):
        """Show system status with component health"""
        try:
            # Create status overview
            healthy = sum(1 for status in components.values() if status)
            total = len(components)

            status_icon = "✅" if healthy == total else "⚠️" if healthy > 0 else "❌"
            message = f"System Health: {healthy}/{total} components OK"

            if details:
                message += f"\n\n{details}"

            # Add component details
            message += "\n\nComponents:"
            for component, status in components.items():
                icon = "✅" if status else "❌"
                message += f"\n{icon} {component}"

            self.show_notification(
                f"{status_icon} {status_title}",
                message,
                NotificationType.SYSTEM
            )

        except Exception as e:
            self.logger.error("Failed to show system status", exception=e)

    def get_notification_history(self, limit: int = 50) -> list:
        """Get recent notification history for diagnostics"""
        try:
            return self.notification_history[-limit:] if self.notification_history else []
        except Exception as e:
            self.logger.error("Failed to get notification history", exception=e)
            return []

    def clear_notification_history(self):
        """Clear notification history"""
        try:
            self.notification_history.clear()
            self.recent_notifications.clear()
            self.logger.info("Notification history cleared")
        except Exception as e:
            self.logger.error("Failed to clear notification history", exception=e)

    # Private methods

    def _should_show_notification(self, notification_type: NotificationType, style: str) -> bool:
        """Determine if notification should be shown based on style settings"""
        if style == "none":
            return False
        elif style == "minimal":
            # Only show high priority notifications
            return notification_type in [NotificationType.ERROR, NotificationType.WARNING]
        elif style == "standard":
            # Show most notifications except verbose conversion feedback
            return notification_type != NotificationType.CONVERSION
        else:  # detailed
            return True

    def _is_duplicate_notification(self, title: str, message: str) -> bool:
        """Check if this is a duplicate notification within recent timeframe"""
        current_time = time.time()
        key = f"{title}:{message}"

        # Check if we've shown this notification recently (within 5 seconds)
        if key in self.recent_notifications:
            last_time = self.recent_notifications[key]
            if current_time - last_time < 5.0:
                return True

        # Update tracking
        self.recent_notifications[key] = current_time

        # Clean old entries (older than 60 seconds)
        self.recent_notifications = {
            k: v for k, v in self.recent_notifications.items()
            if current_time - v < 60.0
        }

        return False

    def _display_notification(
        self,
        title: str,
        message: str,
        config: NotificationConfig,
        action_callback: Optional[Callable] = None
    ):
        """Display the actual notification using rumps"""
        try:
            # Use rumps notification system
            rumps.notification(
                title=title,
                subtitle=None,
                message=message,
                sound=config.sound,
                data=None  # Could be used for action callbacks in future
            )

        except Exception as e:
            self.logger.error("Failed to display notification", exception=e)
            # Fallback to console output for debugging
            print(f"NOTIFICATION: {title} - {message}")

    def _track_notification(self, title: str, message: str, notification_type: NotificationType):
        """Track notification for history and analytics"""
        try:
            notification_record = {
                'timestamp': time.time(),
                'title': title,
                'message': message,
                'type': notification_type.value
            }

            self.notification_history.append(notification_record)

            # Keep only last 100 notifications
            if len(self.notification_history) > 100:
                self.notification_history = self.notification_history[-100:]

        except Exception as e:
            self.logger.error("Failed to track notification", exception=e)

# Global notification manager instance
_notification_manager = None

def get_notification_manager() -> NotificationManager:
    """Get global notification manager instance"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager