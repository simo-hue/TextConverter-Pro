"""
Centralized error handling system for TextConverter Pro
"""

import functools
import time
from typing import Callable, Any, Optional, Type, Tuple
from .logger import get_logger
from .exceptions import TextConverterError, get_user_friendly_error

class ErrorHandler:
    """Centralized error handling with retry logic and user notification"""

    def __init__(self, notification_callback: Optional[Callable] = None):
        self.logger = get_logger()
        self.notification_callback = notification_callback

    def handle_error(self,
                    error: Exception,
                    context: str = "",
                    notify_user: bool = True,
                    critical: bool = False) -> bool:
        """
        Handle an error with logging and optional user notification

        Args:
            error: The exception that occurred
            context: Additional context about when/where the error occurred
            notify_user: Whether to show notification to user
            critical: Whether this is a critical error requiring app restart

        Returns:
            bool: True if error was handled gracefully, False if critical
        """

        # Log the error with context
        error_msg = f"{context}: {str(error)}" if context else str(error)

        if critical:
            self.logger.critical(error_msg, exception=error)
            if isinstance(error, TextConverterError):
                self.logger.create_crash_report(error, {"context": context, "critical": True})
        else:
            self.logger.error(error_msg, exception=error)

        # Notify user if requested
        if notify_user and self.notification_callback:
            self._notify_user_of_error(error, critical)

        return not critical

    def _notify_user_of_error(self, error: Exception, critical: bool = False):
        """Send user-friendly error notification"""
        if isinstance(error, TextConverterError):
            error_info = get_user_friendly_error(error.error_code)
            title = f"❌ {error_info['title']}"
            message = error_info['message']

            if critical:
                title = f"🚨 Critical Error: {error_info['title']}"
                message = f"{error_info['message']}\n\nRestart may be required."

        else:
            title = "❌ Unexpected Error"
            message = "An unexpected error occurred. Please try again."

            if critical:
                title = "🚨 Critical Error"
                message = "A critical error occurred. Please restart the application."

        self.notification_callback(title, message)

def retry_on_error(max_retries: int = 3,
                  delay: float = 0.1,
                  backoff_multiplier: float = 2.0,
                  exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    """
    Decorator that retries a function on specified exceptions

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_multiplier: Multiplier for delay after each retry
        exceptions: Tuple of exception types to retry on
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger()
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"Function {func.__name__} succeeded after {attempt} retries")
                    return result

                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries", exception=e)
                        raise

                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {current_delay}s", exception=e)
                    time.sleep(current_delay)
                    current_delay *= backoff_multiplier

        return wrapper
    return decorator

def safe_execute(func: Callable,
                *args,
                default_return: Any = None,
                context: str = "",
                notify_user: bool = True,
                error_handler: Optional[ErrorHandler] = None,
                **kwargs) -> Any:
    """
    Safely execute a function with error handling

    Args:
        func: Function to execute
        *args: Arguments for the function
        default_return: Value to return if function fails
        context: Context description for error logging
        notify_user: Whether to notify user of errors
        error_handler: Custom error handler instance
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or default_return if error occurred
    """
    if error_handler is None:
        error_handler = ErrorHandler()

    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler.handle_error(
            e,
            context=context or f"executing {func.__name__}",
            notify_user=notify_user
        )
        return default_return

def error_boundary(context: str = "",
                  notify_user: bool = True,
                  default_return: Any = None):
    """
    Decorator that provides error boundary for functions

    Args:
        context: Context description for error logging
        notify_user: Whether to notify user of errors
        default_return: Value to return if function fails
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return safe_execute(
                func,
                *args,
                default_return=default_return,
                context=context or f"in {func.__name__}",
                notify_user=notify_user,
                **kwargs
            )
        return wrapper
    return decorator

def log_performance(operation_name: str = ""):
    """
    Decorator that logs function execution time

    Args:
        operation_name: Custom name for the operation (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger()
            start_time = time.time()
            operation = operation_name or func.__name__

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.log_performance(operation, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.log_performance(f"{operation} (FAILED)", duration)
                raise

        return wrapper
    return decorator

# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None

def get_error_handler(notification_callback: Optional[Callable] = None) -> ErrorHandler:
    """Get or create the global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None or notification_callback:
        _global_error_handler = ErrorHandler(notification_callback)
    return _global_error_handler