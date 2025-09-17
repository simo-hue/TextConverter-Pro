"""
Core text conversion functionality
"""

import pyperclip
from typing import Optional, Callable
from enum import Enum

from ..utils.logger import get_logger
from ..utils.exceptions import ClipboardError, ConversionError
from ..utils.error_handler import error_boundary, retry_on_error, log_performance
from ..utils.feedback_system import get_feedback_system
from ..ui.notification_manager import get_notification_manager, NotificationType

class ConversionType(Enum):
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    CAPITALIZE = "capitalize"

class TextConverter:
    """Core text conversion engine with robust error handling"""

    def __init__(self, notification_callback: Optional[Callable] = None):
        self.original_text = ""
        self.notification_callback = notification_callback
        self.logger = get_logger()
        self.feedback_system = get_feedback_system()
        self.notification_manager = get_notification_manager()

        # Initialize component
        self.logger.info("TextConverter initialized")

    @error_boundary(context="converting text", notify_user=True, default_return=False)
    @log_performance("text_conversion")
    def convert_text(self, conversion_type: ConversionType) -> bool:
        """
        Convert clipboard text based on type with comprehensive error handling

        Args:
            conversion_type: Type of conversion to perform

        Returns:
            bool: Success status
        """
        self.logger.debug(f"Starting text conversion", conversion_type=conversion_type.value)
        import time
        self._start_time = time.time()

        # Get text from clipboard with retry logic
        text = self._get_clipboard_text()
        if not text:
            # Record failed attempt
            self.feedback_system.record_conversion_attempt(
                conversion_type.value, 0, 0.0, False, "No text in clipboard"
            )
            return False

        # Store original for undo operations
        self.original_text = text
        self.logger.debug(f"Original text length: {len(text)}")

        # Apply conversion with error handling
        converted = self._apply_conversion(text, conversion_type)

        # Copy back to clipboard with retry
        self._set_clipboard_text(converted)

        # Record feedback and performance metrics
        import time
        processing_time = time.time() - self._start_time if hasattr(self, '_start_time') else 0.0

        self.feedback_system.record_conversion_attempt(
            conversion_type.value,
            len(text),
            processing_time,
            True
        )

        # Show enhanced conversion feedback
        self.notification_manager.show_conversion_feedback(
            conversion_type.value,
            len(text),
            processing_time
        )

        # Log success
        self.logger.info(f"Text converted successfully",
                        conversion_type=conversion_type.value,
                        original_length=len(text),
                        converted_length=len(converted))

        self.logger.log_user_action(f"text_conversion_{conversion_type.value}",
                                   text_length=len(text))

        return True

    @retry_on_error(max_retries=3, delay=0.1, exceptions=(Exception,))
    def _get_clipboard_text(self) -> str:
        """Get text from clipboard with retry logic and validation"""
        try:
            text = pyperclip.paste()

            if text is None:
                raise ClipboardError("Clipboard returned None")

            if not isinstance(text, str):
                raise ClipboardError(f"Clipboard contains non-text data: {type(text)}")

            if not text.strip():
                self.logger.warning("Clipboard contains only whitespace")
                self._notify("⚠️ Warning", "No text in clipboard")
                return ""

            # Validate text length (prevent memory issues)
            if len(text) > 1_000_000:  # 1MB limit
                raise ClipboardError(f"Text too large: {len(text)} characters")

            self.logger.debug(f"Successfully retrieved clipboard text", length=len(text))
            return text

        except Exception as e:
            self.logger.error(f"Failed to get clipboard text", exception=e)
            if not isinstance(e, ClipboardError):
                raise ClipboardError(f"Clipboard access failed: {str(e)}")
            raise

    @retry_on_error(max_retries=3, delay=0.1, exceptions=(Exception,))
    def _set_clipboard_text(self, text: str):
        """Set text to clipboard with retry logic"""
        try:
            if not isinstance(text, str):
                raise ConversionError(f"Cannot copy non-string to clipboard: {type(text)}")

            pyperclip.copy(text)
            self.logger.debug(f"Successfully set clipboard text", length=len(text))

        except Exception as e:
            self.logger.error(f"Failed to set clipboard text", exception=e)
            raise ClipboardError(f"Could not copy converted text: {str(e)}")

    def _apply_conversion(self, text: str, conversion_type: ConversionType) -> str:
        """Apply the specified conversion to text with error handling"""
        try:
            conversion_map = {
                ConversionType.UPPERCASE: text.upper,
                ConversionType.LOWERCASE: text.lower,
                ConversionType.CAPITALIZE: text.title
            }

            if conversion_type not in conversion_map:
                raise ConversionError(f"Unknown conversion type: {conversion_type}")

            converted = conversion_map[conversion_type]()

            # Validate conversion result
            if not isinstance(converted, str):
                raise ConversionError(f"Conversion returned non-string: {type(converted)}")

            self.logger.debug(f"Applied conversion successfully",
                            conversion_type=conversion_type.value,
                            original_length=len(text),
                            converted_length=len(converted))

            return converted

        except Exception as e:
            self.logger.error(f"Text conversion failed",
                            conversion_type=conversion_type.value,
                            exception=e)
            if not isinstance(e, ConversionError):
                raise ConversionError(f"Conversion failed: {str(e)}")
            raise

    def _notify(self, title: str, message: str):
        """Send notification through callback if available"""
        try:
            if self.notification_callback:
                self.notification_callback(title, message)
                self.logger.debug(f"Notification sent", title=title)
        except Exception as e:
            self.logger.error(f"Failed to send notification",
                            title=title,
                            exception=e)

    def get_original_text_length(self) -> int:
        """Get length of original text for backspace operations"""
        return len(self.original_text)

    def get_conversion_history(self) -> dict:
        """Get basic statistics about conversions (for future features)"""
        # Placeholder for future history feature
        return {
            "last_conversion_length": len(self.original_text) if self.original_text else 0
        }