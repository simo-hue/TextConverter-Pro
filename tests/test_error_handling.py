#!/usr/bin/env python3
"""
Unit tests for error handling system
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.exceptions import (
    TextConverterError, ClipboardError, ConversionError,
    get_user_friendly_error
)
from src.utils.error_handler import (
    ErrorHandler, retry_on_error, safe_execute, error_boundary
)
from src.utils.logger import TextConverterLogger

class TestCustomExceptions(unittest.TestCase):
    """Test cases for custom exception classes"""

    def test_text_converter_error_basic(self):
        """Test basic TextConverterError functionality"""
        error = TextConverterError("Test error")
        self.assertEqual(str(error), "[TextConverterError] Test error")
        self.assertEqual(error.error_code, "TextConverterError")

    def test_text_converter_error_with_context(self):
        """Test TextConverterError with context"""
        context = {"operation": "test", "value": 123}
        error = TextConverterError("Test error", "TEST_CODE", context)

        self.assertIn("TEST_CODE", str(error))
        self.assertIn("operation=test", str(error))
        self.assertIn("value=123", str(error))

    def test_clipboard_error(self):
        """Test ClipboardError specific functionality"""
        error = ClipboardError("Clipboard failed")
        self.assertEqual(error.error_code, "CLIPBOARD_ERROR")
        self.assertIn("Clipboard failed", str(error))

    def test_get_user_friendly_error(self):
        """Test user-friendly error message retrieval"""
        error_info = get_user_friendly_error("CLIPBOARD_ERROR")
        self.assertIn("title", error_info)
        self.assertIn("message", error_info)
        self.assertIn("solution", error_info)

        # Test unknown error code
        unknown_error = get_user_friendly_error("UNKNOWN_ERROR")
        self.assertEqual(unknown_error["title"], "Unknown Error")

class TestErrorHandler(unittest.TestCase):
    """Test cases for ErrorHandler class"""

    def setUp(self):
        """Set up test fixtures"""
        self.notification_mock = Mock()
        self.error_handler = ErrorHandler(self.notification_mock)

    def test_handle_error_basic(self):
        """Test basic error handling"""
        error = TextConverterError("Test error")
        result = self.error_handler.handle_error(error, "test context")

        self.assertTrue(result)  # Should handle gracefully
        self.notification_mock.assert_called_once()

    def test_handle_critical_error(self):
        """Test critical error handling"""
        error = TextConverterError("Critical error")
        result = self.error_handler.handle_error(error, "test context", critical=True)

        self.assertFalse(result)  # Should indicate critical error
        self.notification_mock.assert_called_once()

    def test_handle_error_no_notification(self):
        """Test error handling without user notification"""
        error = TextConverterError("Test error")
        result = self.error_handler.handle_error(error, notify_user=False)

        self.assertTrue(result)
        self.notification_mock.assert_not_called()

class TestErrorDecorators(unittest.TestCase):
    """Test cases for error handling decorators"""

    def test_retry_on_error_success(self):
        """Test retry decorator with successful function"""
        call_count = 0

        @retry_on_error(max_retries=3)
        def test_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = test_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 1)

    def test_retry_on_error_with_retries(self):
        """Test retry decorator with failing then succeeding function"""
        call_count = 0

        @retry_on_error(max_retries=3, delay=0.01)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Test error")
            return "success"

        result = test_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)

    def test_retry_on_error_max_retries_exceeded(self):
        """Test retry decorator when max retries exceeded"""
        call_count = 0

        @retry_on_error(max_retries=2, delay=0.01)
        def test_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent error")

        with self.assertRaises(ValueError):
            test_function()

        self.assertEqual(call_count, 3)  # Initial + 2 retries

    def test_error_boundary_success(self):
        """Test error boundary with successful function"""
        @error_boundary(default_return="default")
        def test_function():
            return "success"

        result = test_function()
        self.assertEqual(result, "success")

    def test_error_boundary_with_error(self):
        """Test error boundary with failing function"""
        @error_boundary(default_return="default")
        def test_function():
            raise ValueError("Test error")

        result = test_function()
        self.assertEqual(result, "default")

    def test_safe_execute_success(self):
        """Test safe_execute with successful function"""
        def test_function(x, y):
            return x + y

        result = safe_execute(test_function, 1, 2, default_return=0)
        self.assertEqual(result, 3)

    def test_safe_execute_with_error(self):
        """Test safe_execute with failing function"""
        def test_function():
            raise ValueError("Test error")

        result = safe_execute(test_function, default_return="default")
        self.assertEqual(result, "default")

class TestLogger(unittest.TestCase):
    """Test cases for logging system"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test logs
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_logger_initialization(self):
        """Test logger initialization"""
        logger = TextConverterLogger("TestApp", debug_mode=True)
        self.assertEqual(logger.app_name, "TestApp")
        self.assertTrue(logger.debug_mode)

    def test_logging_methods(self):
        """Test various logging methods"""
        logger = TextConverterLogger("TestApp", debug_mode=True)

        # Test different log levels
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        logger.debug("Test debug message")

    def test_logging_with_context(self):
        """Test logging with context parameters"""
        logger = TextConverterLogger("TestApp", debug_mode=True)

        logger.info("Test message", operation="test", value=123)
        logger.error("Error message", error_code="TEST_ERROR")

    def test_performance_logging(self):
        """Test performance logging"""
        logger = TextConverterLogger("TestApp")

        logger.log_performance("test_operation", 0.123)
        logger.log_performance("slow_operation", 1.456, details="extra info")

    @patch('src.utils.logger.psutil')
    def test_system_info_logging(self, mock_psutil):
        """Test system information logging"""
        # Mock psutil functions
        mock_psutil.cpu_count.return_value = 8
        mock_psutil.virtual_memory.return_value = Mock(total=16*1024**3)
        mock_psutil.disk_usage.return_value = Mock(free=100*1024**3)

        logger = TextConverterLogger("TestApp")
        logger.log_system_info()

if __name__ == "__main__":
    unittest.main()