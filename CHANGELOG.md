# Changelog

All notable changes to TextConverter Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Custom app icon and branding
- Additional text transformation modes
- Multi-language support
- Batch text processing
- Integration with popular text editors

## [1.0.0] - 2024-09-17

### Added
- **Professional Distribution System**: DMG and PKG installers for easy installation
- **Complete Menu Bar Application**: Native macOS integration with "TXT" menu bar icon
- **Global Hotkey Support**: System-wide text conversion with customizable shortcuts
- **Text Transformations**: UPPERCASE, lowercase, and Capitalize Case conversions
- **Auto-Paste Technology**: Intelligent text replacement without breaking workflow
- **Professional Settings Manager**: Comprehensive configuration with backup and validation
- **Advanced Error Handling**: Robust error management with detailed logging
- **Auto-Update System**: GitHub-based automatic updates with version management
- **Rich Notifications**: Customizable feedback system with multiple styles
- **Theme Support**: System, Light, and Dark theme compatibility
- **Performance Monitoring**: Real-time metrics and diagnostic capabilities
- **Professional Logging**: Comprehensive logging system with rotation and cleanup
- **Modular Architecture**: Clean separation of concerns for maintainability

### Distribution Methods
- **DMG Installer**: Drag-and-drop installation for end users (`TextConverter-Pro-1.0.0.dmg`)
- **PKG Installer**: Guided installation with automatic permission setup (`TextConverter-Pro-Installer-1.0.0.pkg`)
- **Source Build**: Complete build system with Makefile automation
- **App Bundle**: Professional `.app` package for Applications folder

### Technical Features
- **Build System**: Professional py2app configuration with comprehensive module inclusion
- **Import Resolution**: Advanced Python path management for bundled applications
- **Platform Compatibility**: Universal binary support for Intel and Apple Silicon
- **Dependency Management**: Automatic handling of pynput, rumps, and PyObjC frameworks
- **Error Recovery**: Robust fallback systems and graceful error handling

### Default Hotkeys
- `⌘⇧U` - Convert selected text to **UPPERCASE**
- `⌘⇧L` - Convert selected text to **lowercase**
- `⌘⇧C` - Convert selected text to **Capitalize Case**

### System Requirements
- **macOS**: 10.12 (Sierra) or later
- **Memory**: 50MB RAM (15MB runtime usage)
- **Storage**: 15-20MB disk space
- **Permissions**: Accessibility access required for global hotkeys
- **Architecture**: Universal (Intel x64 and Apple Silicon)