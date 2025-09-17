#!/usr/bin/env python3
"""
Unit tests for text converter functionality
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.converter import TextConverter, ConversionType

class TestTextConverter(unittest.TestCase):
    """Test cases for TextConverter class"""

    def setUp(self):
        """Set up test fixtures"""
        self.converter = TextConverter()

    def test_uppercase_conversion(self):
        """Test uppercase conversion"""
        # Mock pyperclip for testing
        test_text = "hello world"
        result = self.converter._apply_conversion(test_text, ConversionType.UPPERCASE)
        self.assertEqual(result, "HELLO WORLD")

    def test_lowercase_conversion(self):
        """Test lowercase conversion"""
        test_text = "HELLO WORLD"
        result = self.converter._apply_conversion(test_text, ConversionType.LOWERCASE)
        self.assertEqual(result, "hello world")

    def test_capitalize_conversion(self):
        """Test capitalize conversion"""
        test_text = "hello world"
        result = self.converter._apply_conversion(test_text, ConversionType.CAPITALIZE)
        self.assertEqual(result, "Hello World")

    def test_original_text_length(self):
        """Test original text length tracking"""
        self.converter.original_text = "test text"
        self.assertEqual(self.converter.get_original_text_length(), 9)

if __name__ == "__main__":
    unittest.main()