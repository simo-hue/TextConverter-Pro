"""
Professional logging system for TextConverter Pro
"""

import logging
import logging.handlers
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json

class TextConverterLogger:
    """Centralized logging system with professional features"""

    def __init__(self, app_name: str = "TextConverter", debug_mode: bool = False):
        self.app_name = app_name
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(app_name)

        # Create logs directory
        self.log_dir = Path.home() / "Library" / "Logs" / app_name
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.setup_logger()

    def setup_logger(self):
        """Configure the logger with multiple handlers"""
        self.logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)

        # Clear existing handlers
        self.logger.handlers.clear()

        # File handler with rotation (keep 10 files, 10MB each)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{self.app_name.lower()}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO if not self.debug_mode else logging.DEBUG)

        # Error file handler (separate file for errors only)
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{self.app_name.lower()}_errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)

        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s() | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )

        # Apply formatters
        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(error_handler)

        # Log startup
        self.logger.info(f"=== {self.app_name} Started ===")
        self.logger.info(f"Version: 1.0.0")
        self.logger.info(f"Debug Mode: {self.debug_mode}")
        self.logger.info(f"Log Directory: {self.log_dir}")

    def info(self, message: str, **kwargs):
        """Log info message with optional context"""
        self._log_with_context(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with optional context"""
        self._log_with_context(logging.WARNING, message, **kwargs)

    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception and context"""
        if exception:
            self.logger.error(f"{message} | Exception: {str(exception)}")
            if self.debug_mode:
                self.logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            self._log_with_context(logging.ERROR, message, **kwargs)

    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critical message with optional exception and context"""
        if exception:
            self.logger.critical(f"{message} | Exception: {str(exception)}")
            self.logger.critical(f"Traceback: {traceback.format_exc()}")
        else:
            self._log_with_context(logging.CRITICAL, message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with optional context"""
        if self.debug_mode:
            self._log_with_context(logging.DEBUG, message, **kwargs)

    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log message with additional context data"""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            message = f"{message} | Context: {context}"

        self.logger.log(level, message)

    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        self.info(f"Performance: {operation} took {duration:.3f}s", **kwargs)

    def log_user_action(self, action: str, **kwargs):
        """Log user actions for analytics"""
        self.info(f"User Action: {action}", **kwargs)

    def log_system_info(self):
        """Log system information for debugging"""
        import platform
        import psutil

        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "disk_free_gb": round(psutil.disk_usage('/').free / (1024**3), 2)
        }

        self.info("System Information", **system_info)

    def create_crash_report(self, exception: Exception, context: Dict[str, Any] = None):
        """Create detailed crash report"""
        crash_time = datetime.now().isoformat()
        crash_file = self.log_dir / f"crash_report_{crash_time.replace(':', '-')}.json"

        crash_data = {
            "timestamp": crash_time,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "system_info": self._get_system_info()
        }

        try:
            with open(crash_file, 'w', encoding='utf-8') as f:
                json.dump(crash_data, f, indent=2, ensure_ascii=False)

            self.critical(f"Crash report created: {crash_file}", exception=exception)
            return crash_file
        except Exception as e:
            self.critical(f"Failed to create crash report: {e}")
            return None

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for crash reports"""
        try:
            import platform
            import psutil

            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        except Exception:
            return {"error": "Could not gather system info"}

    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up log files older than specified days"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)

            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.info(f"Deleted old log file: {log_file.name}")

        except Exception as e:
            self.error(f"Failed to cleanup old logs: {e}")

# Global logger instance
_logger_instance: Optional[TextConverterLogger] = None

def get_logger(debug_mode: bool = False) -> TextConverterLogger:
    """Get or create the global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = TextConverterLogger(debug_mode=debug_mode)
    return _logger_instance

def setup_global_exception_handler():
    """Setup global exception handler for uncaught exceptions"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Allow KeyboardInterrupt to terminate the program
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger = get_logger()
        logger.critical(
            "Uncaught exception occurred",
            exception=exc_value
        )
        logger.create_crash_report(exc_value, {
            "exception_type": exc_type.__name__,
            "in_main_thread": True
        })

    sys.excepthook = handle_exception