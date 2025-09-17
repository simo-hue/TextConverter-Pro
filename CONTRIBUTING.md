# 🤝 Contributing to TextConverter Pro

Thank you for your interest in contributing to TextConverter Pro! This document provides comprehensive guidelines for contributors to ensure high-quality contributions and maintain project standards.

## 📋 Table of Contents
- [🚀 Getting Started](#-getting-started)
- [🏗️ Development Setup](#️-development-setup)
- [📝 Contribution Guidelines](#-contribution-guidelines)
- [🐛 Bug Reports](#-bug-reports)
- [✨ Feature Requests](#-feature-requests)
- [🔧 Pull Request Process](#-pull-request-process)
- [📏 Code Standards](#-code-standards)
- [🧪 Testing Requirements](#-testing-requirements)
- [📚 Documentation](#-documentation)
- [👥 Community Guidelines](#-community-guidelines)

---

## 🚀 Getting Started

### Prerequisites
- macOS 10.12 (Sierra) or later
- Python 3.8 or higher
- Git knowledge and GitHub account
- Familiarity with macOS development concepts

### Quick Start
1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/TextConverter-Pro.git
   cd TextConverter-Pro
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Run Development Version**
   ```bash
   # Run the application
   python3 src/ui/menubar_app.py

   # Run tests
   python3 -m pytest tests/ -v
   ```

### Development Tools
We recommend using these tools for development:
- **IDE**: PyCharm, VS Code, or Vim with Python support
- **Linting**: pylint, flake8
- **Formatting**: black, isort
- **Type Checking**: mypy
- **Testing**: pytest

---

## 🏗️ Development Setup

### Project Structure
```
TextConverter-Pro/
├── src/                    # Source code
│   ├── core/              # Core business logic
│   │   ├── converter.py   # Text conversion engine
│   │   ├── hotkeys.py     # Global hotkey management
│   │   └── autopaste.py   # Auto-paste functionality
│   ├── ui/                # User interface
│   │   ├── menubar_app.py # Main menu bar application
│   │   └── preferences.py # Settings interface
│   └── utils/             # Utilities and helpers
│       ├── settings.py    # Configuration management
│       ├── logger.py      # Logging system
│       └── updater.py     # Auto-update system
├── tests/                 # Test suite
├── scripts/               # Build and deployment scripts
├── docs/                  # Documentation
└── requirements.txt       # Python dependencies
```

### Environment Setup
1. **Virtual Environment** (Required)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

2. **Dependencies Installation**
   ```bash
   # Production dependencies
   pip install -r requirements.txt

   # Development dependencies
   pip install -r requirements-dev.txt
   ```

3. **Pre-commit Hooks** (Recommended)
   ```bash
   pre-commit install
   ```

### Configuration
Create a local development configuration:
```bash
# Copy example configuration
cp config/development.json.example config/development.json

# Edit with your preferences
vim config/development.json
```

---

## 📝 Contribution Guidelines

### Types of Contributions
We welcome the following types of contributions:
- 🐛 **Bug fixes** - Fix existing issues
- ✨ **New features** - Add new functionality
- 📚 **Documentation** - Improve or add documentation
- 🧪 **Tests** - Add or improve test coverage
- 🎨 **UI/UX improvements** - Enhance user interface
- ⚡ **Performance optimizations** - Improve speed or efficiency
- 🔒 **Security improvements** - Enhance application security

### Before Contributing
1. **Search existing issues** to avoid duplicates
2. **Read the documentation** to understand the project
3. **Join discussions** in relevant GitHub Discussions
4. **Ask questions** if anything is unclear

### Contribution Workflow
1. **Create an Issue** (for significant changes)
2. **Fork and Branch** from the main branch
3. **Develop and Test** your changes locally
4. **Submit a Pull Request** with detailed description
5. **Participate in Review** process
6. **Address Feedback** and iterate

---

## 🐛 Bug Reports

### Before Reporting a Bug
1. **Check existing issues** for similar problems
2. **Try the latest version** to ensure it's not already fixed
3. **Reproduce the issue** consistently
4. **Gather system information**

### Bug Report Template
When creating a bug report, please use this template:

```markdown
## Bug Description
A clear and concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Execute '...'
4. See error

## Expected Behavior
A clear description of what you expected to happen.

## Actual Behavior
A clear description of what actually happened.

## Screenshots
If applicable, add screenshots to help explain your problem.

## Environment Information
- **macOS Version**: [e.g., macOS 12.0 Monterey]
- **TextConverter Version**: [e.g., v1.0.0]
- **Python Version**: [e.g., Python 3.9.0]
- **Installation Method**: [e.g., built from source, downloaded release]

## Log Output
Please include relevant log output:
```
[Paste log output here]
```

## Additional Context
Add any other context about the problem here.
```

### Critical Bugs
For security vulnerabilities or critical bugs:
- **Do NOT** create a public issue
- **Email directly**: [security email when available]
- **Include**: Detailed description and reproduction steps
- **Response time**: We aim to respond within 24 hours

---

## ✨ Feature Requests

### Before Requesting a Feature
1. **Search existing requests** to avoid duplicates
2. **Check the roadmap** in README.md
3. **Consider the scope** - does it fit the project goals?
4. **Think about implementation** - is it technically feasible?

### Feature Request Template
```markdown
## Feature Summary
A brief, clear description of the feature you'd like to see.

## Problem Statement
What problem does this feature solve? What use case does it address?

## Proposed Solution
A clear and concise description of what you want to happen.

## Alternative Solutions
Describe any alternative solutions or features you've considered.

## Implementation Ideas
If you have ideas about how this could be implemented, share them here.

## Use Cases
Describe specific scenarios where this feature would be useful:
- As a [user type], I want [goal] so that [benefit]

## Additional Context
Add any other context, mockups, or examples about the feature request.
```

### Feature Prioritization
Features are prioritized based on:
- **User Impact** - How many users will benefit?
- **Alignment** - Does it fit the project vision?
- **Complexity** - Implementation effort required
- **Maintenance** - Long-term maintenance burden
- **Community Interest** - Upvotes and discussions

---

## 🔧 Pull Request Process

### Pull Request Checklist
Before submitting a PR, ensure:
- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventional format
- [ ] No merge conflicts with main branch
- [ ] PR description explains the changes

### Pull Request Template
```markdown
## Description
Brief description of changes made in this PR.

## Related Issue
Fixes #(issue number)

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Changes Made
- List the specific changes made
- Be as detailed as necessary
- Include any breaking changes

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed
- [ ] Performance impact assessed

## Screenshots (if applicable)
Add screenshots to demonstrate the changes.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Additional Notes
Any additional information that reviewers should know.
```

### Review Process
1. **Automated Checks** - CI/CD pipeline runs tests
2. **Code Review** - Maintainers review code quality
3. **Testing** - Manual testing of changes
4. **Approval** - At least one maintainer approval required
5. **Merge** - Changes merged to main branch

### Review Criteria
- **Functionality** - Does it work as intended?
- **Code Quality** - Is it well-written and maintainable?
- **Performance** - Does it impact application performance?
- **Security** - Are there any security concerns?
- **Documentation** - Is it adequately documented?
- **Testing** - Is it properly tested?

---

## 📏 Code Standards

### Python Style Guide
We follow [PEP 8](https://pep8.org/) with these specific guidelines:

#### Formatting
- **Line Length**: 100 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Organized with isort
- **Code Formatting**: Automated with black

#### Naming Conventions
```python
# Classes: PascalCase
class TextConverter:
    pass

# Functions and variables: snake_case
def convert_text():
    user_input = get_input()

# Constants: UPPER_SNAKE_CASE
MAX_TEXT_LENGTH = 1000000

# Private methods: _leading_underscore
def _internal_method():
    pass
```

#### Documentation
```python
def convert_text(text: str, conversion_type: ConversionType) -> str:
    """
    Convert text to specified case type.

    Args:
        text: The input text to convert
        conversion_type: Type of conversion to apply

    Returns:
        The converted text string

    Raises:
        ConversionError: If conversion fails
        ValueError: If text is empty or invalid

    Example:
        >>> convert_text("hello world", ConversionType.UPPERCASE)
        "HELLO WORLD"
    """
    # Implementation here
```

### Error Handling
```python
# Use specific exceptions
try:
    result = risky_operation()
except SpecificError as e:
    logger.error("Operation failed", exception=e)
    raise ConversionError(f"Failed to convert: {e}")

# Use error boundaries for UI operations
@error_boundary(context="text conversion", notify_user=True)
def safe_conversion():
    # Implementation
```

### Logging Standards
```python
# Use structured logging
logger.info("Conversion completed",
           conversion_type=type.value,
           text_length=len(text),
           processing_time=duration)

# Log levels
logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Something unexpected happened")
logger.error("An error occurred", exception=e)
logger.critical("Critical system failure")
```

---

## 🧪 Testing Requirements

### Test Structure
```
tests/
├── unit/                  # Unit tests
│   ├── test_converter.py  # Core converter tests
│   ├── test_hotkeys.py    # Hotkey system tests
│   └── test_settings.py   # Settings management tests
├── integration/           # Integration tests
│   ├── test_end_to_end.py # Full workflow tests
│   └── test_ui_integration.py # UI integration tests
├── performance/           # Performance benchmarks
│   └── test_benchmarks.py
└── fixtures/              # Test data and fixtures
    └── sample_data.py
```

### Writing Tests
```python
import pytest
from unittest.mock import Mock, patch
from src.core.converter import TextConverter, ConversionType

class TestTextConverter:
    """Test cases for TextConverter class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.converter = TextConverter()

    def test_uppercase_conversion(self):
        """Test uppercase text conversion."""
        # Arrange
        input_text = "hello world"
        expected = "HELLO WORLD"

        # Act
        with patch('pyperclip.paste', return_value=input_text):
            with patch('pyperclip.copy') as mock_copy:
                result = self.converter.convert_text(ConversionType.UPPERCASE)

        # Assert
        assert result is True
        mock_copy.assert_called_once_with(expected)

    def test_empty_clipboard(self):
        """Test handling of empty clipboard."""
        with patch('pyperclip.paste', return_value=""):
            result = self.converter.convert_text(ConversionType.UPPERCASE)

        assert result is False

    @pytest.mark.parametrize("input_text,expected", [
        ("HELLO", "hello"),
        ("MiXeD cAsE", "mixed case"),
        ("123 ABC", "123 abc"),
    ])
    def test_lowercase_conversion_cases(self, input_text, expected):
        """Test various lowercase conversion cases."""
        with patch('pyperclip.paste', return_value=input_text):
            with patch('pyperclip.copy') as mock_copy:
                self.converter.convert_text(ConversionType.LOWERCASE)

        mock_copy.assert_called_once_with(expected)
```

### Test Requirements
- **Coverage**: Minimum 80% code coverage
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Performance Tests**: Benchmark critical operations
- **UI Tests**: Test user interface components
- **Mock External Dependencies**: Clipboard, file system, network

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_converter.py -v

# Run performance benchmarks
python -m pytest tests/performance/ --benchmark-only
```

---

## 📚 Documentation

### Documentation Standards
- **Code Comments**: Explain why, not what
- **Docstrings**: Comprehensive API documentation
- **README**: Keep up-to-date with features
- **CHANGELOG**: Document all changes
- **Architecture Docs**: Explain design decisions

### Documentation Types
1. **API Documentation** - Function and class documentation
2. **User Guides** - How to use features
3. **Developer Guides** - How to contribute and extend
4. **Architecture Docs** - System design and patterns
5. **Troubleshooting** - Common issues and solutions

### Writing Guidelines
- **Clear and Concise** - Easy to understand
- **Examples** - Include practical examples
- **Up-to-Date** - Keep synchronized with code
- **Searchable** - Use clear headings and structure
- **Accessible** - Consider all skill levels

---

## 👥 Community Guidelines

### Code of Conduct
We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). In summary:

#### Our Standards
- **Be Respectful** - Treat everyone with respect
- **Be Inclusive** - Welcome diverse perspectives
- **Be Constructive** - Provide helpful feedback
- **Be Patient** - Help others learn and grow
- **Be Professional** - Maintain professional interactions

#### Unacceptable Behavior
- Harassment or discrimination of any kind
- Trolling, insulting, or derogatory comments
- Public or private harassment
- Publishing private information without consent
- Other conduct inappropriate in a professional setting

### Communication Channels
- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and discussions
- **Pull Requests** - Code review and collaboration
- **Email** - Private or sensitive matters

### Getting Help
- **Documentation** - Check README and FEATURES.md first
- **Search Issues** - Look for existing solutions
- **Ask Questions** - Use GitHub Discussions
- **Be Specific** - Provide detailed information
- **Be Patient** - Maintainers respond when available

---

## 🏆 Recognition

### Contributors
We recognize contributors in several ways:
- **Contributors File** - Listed in CONTRIBUTORS.md
- **Release Notes** - Credited in changelog
- **GitHub Profile** - Contribution history visible
- **Special Recognition** - Outstanding contributions highlighted

### Contribution Levels
- **First-time Contributors** - Welcome and guidance provided
- **Regular Contributors** - Invited to discussions and planning
- **Core Contributors** - Given additional repository permissions
- **Maintainers** - Full project access and responsibility

---

## 📞 Getting Help

### Questions?
- **General Questions** - Use GitHub Discussions
- **Bug Reports** - Create a GitHub Issue
- **Security Issues** - Email directly (when available)
- **Feature Ideas** - GitHub Discussions or Issues

### Response Times
- **Issues**: 2-3 business days
- **Pull Requests**: 3-5 business days
- **Security Issues**: Within 24 hours
- **General Questions**: 1-2 business days

---

Thank you for contributing to TextConverter Pro! Your contributions help make this project better for everyone. 🚀

*For questions about this guide, please open a GitHub Discussion or Issue.*