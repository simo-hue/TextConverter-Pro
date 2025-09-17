# 🚀 Installation Guide - TextConverter Pro

This guide covers all installation methods for TextConverter Pro on macOS.

## 📋 Table of Contents
- [Quick Installation](#-quick-installation)
- [System Requirements](#-system-requirements)
- [Installation Methods](#-installation-methods)
- [Permission Setup](#-permission-setup)
- [Troubleshooting](#-troubleshooting)
- [Uninstallation](#-uninstallation)

---

## ⚡ Quick Installation

### Option 1: DMG Installer (Recommended)
1. Download `TextConverter-Pro-1.0.0.dmg` (16MB) from [GitHub Releases](https://github.com/simo-hue/TextConverter-Pro/releases)
2. Double-click the DMG file to mount
3. Drag **TextConverter Pro** to **Applications** folder
4. Launch from Applications and grant Accessibility permissions
5. Look for "TXT" icon in your menu bar

### Option 2: PKG Installer
1. Download `TextConverter-Pro-Installer-1.0.0.pkg` (16MB) from [GitHub Releases](https://github.com/simo-hue/TextConverter-Pro/releases)
2. Double-click the PKG file
3. Follow the guided installer with welcome screen and license
4. Installer will guide you through permission setup
5. Launch from Applications - fully configured!

---

## 💻 System Requirements

### Minimum Requirements
- **macOS**: 10.12 (Sierra) or later
- **Architecture**: Intel x64 or Apple Silicon (M1/M2)
- **Memory**: 50MB RAM
- **Storage**: 15MB free space
- **Permissions**: Accessibility access required

### Recommended
- **macOS**: 12.0 (Monterey) or later
- **Memory**: 100MB RAM for optimal performance
- **Storage**: 50MB free space

---

## 📦 Installation Methods

### Method 1: Pre-built DMG (Easiest)

**Best for**: Regular users who want simple installation

```bash
# Download and install via curl (optional)
curl -L https://github.com/simo-hue/TextConverter-Pro/releases/latest/download/TextConverter-Pro-1.0.0.dmg -o TextConverter-Pro.dmg
open TextConverter-Pro.dmg
```

**Steps**:
1. Double-click the DMG file
2. Drag the app to Applications folder
3. Eject the DMG
4. Launch from Applications

### Method 2: PKG Installer

**Best for**: Enterprise deployment, automated installation

```bash
# Download and install via command line
curl -L https://github.com/simo-hue/TextConverter-Pro/releases/latest/download/TextConverter-Pro-Installer-1.0.0.pkg -o TextConverter-Pro-Installer.pkg
sudo installer -pkg TextConverter-Pro-Installer.pkg -target /
```

**Features**:
- Guided installation process
- Automatic permission setup
- Welcome and license screens
- Post-installation scripts

### Method 3: Build from Source

**Best for**: Developers, customization, latest features

#### Prerequisites
```bash
# Install Python 3.8+
brew install python@3.11

# Install build dependencies
pip install py2app pillow
```

#### Build Process
```bash
# Clone the repository
git clone https://github.com/simo-hue/TextConverter-Pro.git
cd TextConverter-Pro

# Install Python dependencies
pip install -r requirements.txt

# Build the .app bundle
make app

# Create all distribution packages
make all  # Creates both DMG and PKG installers

# Individual build targets
make dmg        # Create DMG installer only
make installer  # Create PKG installer only
```

#### Build Targets
```bash
make clean      # Clean build artifacts
make app        # Build .app bundle
make installer  # Create .pkg installer
make dmg        # Create .dmg disk image
make all        # Build everything
```

---

## 🔐 Permission Setup

TextConverter Pro requires **Accessibility** permissions to function properly.

### Automatic Setup (PKG Installer)
The PKG installer will guide you through permission setup automatically.

### Manual Setup
1. **Open System Preferences**
   - Apple menu → System Preferences
   - Or Spotlight → "System Preferences"

2. **Navigate to Privacy Settings**
   - Click **Security & Privacy**
   - Click **Privacy** tab
   - Select **Accessibility** in the sidebar

3. **Add TextConverter Pro**
   - Click the **lock icon** (bottom left)
   - Enter your administrator password
   - Click the **+** button
   - Navigate to `/Applications/TextConverter Pro.app`
   - Click **Open**

4. **Enable Permissions**
   - Ensure the **checkbox** next to TextConverter Pro is **checked** ✅
   - Click the lock icon to prevent further changes

### Verification
- Launch TextConverter Pro
- Look for "TXT" icon in menu bar
- Try a hotkey (⌘⇧U) with selected text
- If working: ✅ Setup complete!

---

## 🧪 Testing Installation

### Quick Test
```bash
# Test if app can launch
open "/Applications/TextConverter Pro.app"

# Check if menu bar icon appears
# Look for "TXT" in your menu bar
```

### Full Test
1. **Select text** in any application (e.g., "hello world")
2. **Copy text** with ⌘C
3. **Press hotkey** ⌘⇧U
4. **Verify result**: Text should change to "HELLO WORLD"

### Test All Features
- **Uppercase**: ⌘⇧U
- **Lowercase**: ⌘⇧L
- **Capitalize**: ⌘⇧C
- **Menu access**: Click menu bar icon
- **Statistics**: Menu → Show Statistics

---

## 🚨 Troubleshooting

### App Won't Launch
```bash
# Check if app is properly signed
spctl -a -t exec -vv "/Applications/TextConverter Pro.app"

# Run from terminal to see errors
"/Applications/TextConverter Pro.app/Contents/MacOS/TextConverter Pro"
```

**Solutions**:
- **Gatekeeper issues**: Right-click app → Open → Open anyway
- **Permission issues**: Check Accessibility permissions
- **Corrupted download**: Re-download the installer

### Hotkeys Not Working

**Symptoms**: Menu bar icon appears, but hotkeys don't respond

**Solutions**:
1. **Check Accessibility permissions** (most common)
2. **Restart the app**:
   ```bash
   pkill -f "TextConverter Pro"
   open "/Applications/TextConverter Pro.app"
   ```
3. **Check for conflicting apps**: Disable other global hotkey apps temporarily
4. **Reset permissions**: Remove and re-add in Accessibility settings

### Auto-paste Not Working

**Symptoms**: Text converts but doesn't paste back

**Solutions**:
1. **Increase paste delay**: Menu → Preferences → Behavior → Paste Delay
2. **Check app compatibility**: Some apps (Adobe products) block programmatic paste
3. **Manual paste**: Use ⌘V after conversion

### Performance Issues

**Symptoms**: Slow conversions, high memory usage

**Solutions**:
1. **Check system resources**: Activity Monitor → TextConverter Pro
2. **Restart app**: Fresh start often resolves memory issues
3. **Reduce text length**: Very large texts (>100KB) may be slow
4. **Check logs**: `~/Library/Logs/TextConverter/`

### Menu Bar Icon Missing

**Solutions**:
```bash
# Restart menu bar services
sudo killall SystemUIServer

# Re-launch TextConverter Pro
open "/Applications/TextConverter Pro.app"
```

---

## 🗑️ Uninstallation

### Method 1: Manual Removal
```bash
# Remove application
rm -rf "/Applications/TextConverter Pro.app"

# Remove user data (optional)
rm -rf "~/Library/Application Support/TextConverter"
rm -rf "~/Library/Logs/TextConverter"
rm -rf "~/Library/Preferences/com.simomattioli.textconverter-pro.plist"
```

### Method 2: Complete Cleanup Script
```bash
#!/bin/bash
# Save as uninstall_textconverter.sh

echo "Uninstalling TextConverter Pro..."

# Kill running processes
pkill -f "TextConverter Pro" || true

# Remove application
rm -rf "/Applications/TextConverter Pro.app"

# Remove user data
rm -rf "$HOME/Library/Application Support/TextConverter"
rm -rf "$HOME/Library/Logs/TextConverter"
rm -rf "$HOME/Library/Preferences/com.simomattioli.textconverter-pro.plist"

# Remove from Login Items (if added)
osascript -e 'tell application "System Events" to delete login item "TextConverter Pro"' 2>/dev/null || true

echo "✅ TextConverter Pro uninstalled completely"
echo "Note: Accessibility permissions remain and can be manually removed"
```

### Remove Accessibility Permissions
1. System Preferences → Security & Privacy → Privacy → Accessibility
2. Select TextConverter Pro in the list
3. Click the **-** button
4. Click lock to save changes

---

## 📞 Installation Support

### Getting Help
- **Documentation**: [FEATURES.md](FEATURES.md)
- **Issues**: [GitHub Issues](https://github.com/simo-hue/TextConverter-Pro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/simo-hue/TextConverter-Pro/discussions)

### Reporting Installation Issues
When reporting installation problems, please include:
- macOS version
- Installation method used
- Error messages (if any)
- Console logs: `Console.app` → Filter: "TextConverter"

### Common Installation Scenarios

#### First-time macOS User
1. Use **DMG installer** (simplest)
2. Follow permission setup carefully
3. Test with simple text first

#### Enterprise Deployment
1. Use **PKG installer** for scripted deployment
2. Pre-approve Accessibility permissions via MDM
3. Deploy via company software distribution

#### Developer Setup
1. **Build from source** for latest features
2. Use `make dev-install` for development dependencies
3. Run tests with `make test`

---

*Happy converting! 🚀*