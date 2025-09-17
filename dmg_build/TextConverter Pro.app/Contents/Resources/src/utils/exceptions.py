"""
Custom exception classes for TextConverter Pro
"""

from typing import Optional, Dict, Any

class TextConverterError(Exception):
    """Base exception class for TextConverter application"""

    def __init__(self, message: str, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}

    def __str__(self):
        base_msg = f"[{self.error_code}] {self.message}"
        if self.context:
            context_str = ", ".join([f"{k}={v}" for k, v in self.context.items()])
            return f"{base_msg} (Context: {context_str})"
        return base_msg

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context
        }

class ClipboardError(TextConverterError):
    """Raised when clipboard operations fail"""

    def __init__(self, message: str = "Clipboard operation failed", **kwargs):
        super().__init__(message, error_code="CLIPBOARD_ERROR", **kwargs)

class HotkeyError(TextConverterError):
    """Raised when hotkey system encounters issues"""

    def __init__(self, message: str = "Hotkey system error", **kwargs):
        super().__init__(message, error_code="HOTKEY_ERROR", **kwargs)

class ConversionError(TextConverterError):
    """Raised when text conversion fails"""

    def __init__(self, message: str = "Text conversion failed", **kwargs):
        super().__init__(message, error_code="CONVERSION_ERROR", **kwargs)

class PasteError(TextConverterError):
    """Raised when auto-paste operations fail"""

    def __init__(self, message: str = "Auto-paste operation failed", **kwargs):
        super().__init__(message, error_code="PASTE_ERROR", **kwargs)

class ConfigurationError(TextConverterError):
    """Raised when configuration issues occur"""

    def __init__(self, message: str = "Configuration error", **kwargs):
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)

class PermissionError(TextConverterError):
    """Raised when required permissions are missing"""

    def __init__(self, message: str = "Required permissions not granted", **kwargs):
        super().__init__(message, error_code="PERMISSION_ERROR", **kwargs)

class SystemCompatibilityError(TextConverterError):
    """Raised when system compatibility issues are detected"""

    def __init__(self, message: str = "System compatibility issue", **kwargs):
        super().__init__(message, error_code="COMPATIBILITY_ERROR", **kwargs)

class ResourceError(TextConverterError):
    """Raised when system resources are insufficient"""

    def __init__(self, message: str = "Insufficient system resources", **kwargs):
        super().__init__(message, error_code="RESOURCE_ERROR", **kwargs)

# Error code mappings for user-friendly messages
ERROR_MESSAGES = {
    "CLIPBOARD_ERROR": {
        "title": "Clipboard Issue",
        "message": "Unable to access clipboard. Please try copying the text again.",
        "solution": "Make sure the text is properly selected and copied with ⌘C."
    },
    "HOTKEY_ERROR": {
        "title": "Hotkey Problem",
        "message": "Global hotkeys are not responding properly.",
        "solution": "Check Accessibility permissions in System Preferences → Security & Privacy."
    },
    "CONVERSION_ERROR": {
        "title": "Conversion Failed",
        "message": "Text conversion could not be completed.",
        "solution": "Try selecting and copying the text again, then retry the conversion."
    },
    "PASTE_ERROR": {
        "title": "Paste Failed",
        "message": "Could not paste the converted text automatically.",
        "solution": "Use ⌘V to paste the converted text manually."
    },
    "PERMISSION_ERROR": {
        "title": "Permission Required",
        "message": "TextConverter needs Accessibility permissions to function.",
        "solution": "Go to System Preferences → Security & Privacy → Accessibility and enable TextConverter."
    },
    "CONFIG_ERROR": {
        "title": "Configuration Error",
        "message": "Application configuration is invalid or corrupted.",
        "solution": "Reset settings or contact support if the problem persists."
    },
    "COMPATIBILITY_ERROR": {
        "title": "System Compatibility",
        "message": "Your system may not be fully compatible with this feature.",
        "solution": "Update to the latest macOS version or contact support."
    },
    "RESOURCE_ERROR": {
        "title": "System Resources",
        "message": "Insufficient system resources to complete the operation.",
        "solution": "Close some applications and try again."
    }
}

def get_user_friendly_error(error_code: str) -> Dict[str, str]:
    """Get user-friendly error message for error code"""
    return ERROR_MESSAGES.get(error_code, {
        "title": "Unknown Error",
        "message": "An unexpected error occurred.",
        "solution": "Please try again or contact support if the problem persists."
    })