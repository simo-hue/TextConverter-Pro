#!/bin/bash

# Professional macOS Installer Creator for TextConverter Pro
# Creates a native .pkg installer with custom welcome screen and license

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Creating macOS Installer Package for TextConverter Pro${NC}"
echo "================================================================="

# Configuration
APP_NAME="TextConverter Pro"
PKG_NAME="TextConverter-Pro-Installer"
VERSION="1.0.0"
IDENTIFIER="com.simomattioli.textconverter-pro"
BUILD_DIR="dist"
INSTALLER_DIR="installer"
RESOURCES_DIR="installer/Resources"

# Step 1: Verify .app bundle exists
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo -e "${RED}❌ App bundle not found!${NC}"
    echo "Please run ./scripts/build_app.sh first"
    exit 1
fi

# Step 2: Prepare installer directory structure
echo -e "${YELLOW}📁 Preparing installer structure...${NC}"
rm -rf "$INSTALLER_DIR"
mkdir -p "$INSTALLER_DIR"
mkdir -p "$RESOURCES_DIR"
mkdir -p "$INSTALLER_DIR/payload/Applications"

# Copy app to payload
cp -R "dist/${APP_NAME}.app" "$INSTALLER_DIR/payload/Applications/"

# Step 3: Create welcome text
echo -e "${YELLOW}📝 Creating installer resources...${NC}"
cat > "$RESOURCES_DIR/Welcome.txt" << 'EOF'
Welcome to TextConverter Pro!

TextConverter Pro is the ultimate macOS text case conversion tool for developers and power users.

Key Features:
• Lightning-fast global hotkeys (⌘⇧U, ⌘⇧L, ⌘⇧C)
• Instant text transformation without app switching
• Professional analytics and performance monitoring
• Auto-updates from GitHub releases
• Native macOS integration

This installer will:
1. Install TextConverter Pro to your Applications folder
2. Set up necessary permissions
3. Configure auto-launch (optional)

After installation, you'll find TextConverter Pro in your Applications folder.
Grant Accessibility permissions when prompted to enable global hotkeys.

Transform your text workflow today!
EOF

# Step 4: Create license file
cat > "$RESOURCES_DIR/License.txt" << 'EOF'
MIT License

Copyright (c) 2024 Simone Mattioli

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# Step 5: Create ReadMe file
cat > "$RESOURCES_DIR/ReadMe.txt" << 'EOF'
TextConverter Pro v1.0.0

INSTALLATION COMPLETE

TextConverter Pro has been installed successfully!

NEXT STEPS:

1. LAUNCH THE APP
   • Open Applications folder
   • Double-click TextConverter Pro
   • Look for "TXT" icon in your menu bar

2. GRANT PERMISSIONS
   • Go to System Preferences → Security & Privacy → Privacy → Accessibility
   • Click the lock and enter your password
   • Add TextConverter Pro and enable the checkbox

3. START USING
   • Select any text in any application
   • Copy with ⌘C
   • Press conversion hotkeys:
     ⌘⇧U = UPPERCASE
     ⌘⇧L = lowercase
     ⌘⇧C = Capitalize Case

4. CUSTOMIZE (OPTIONAL)
   • Click the menu bar icon for preferences
   • Adjust hotkeys, notifications, and behavior
   • View analytics and performance metrics

TROUBLESHOOTING:

• If hotkeys don't work: Check Accessibility permissions
• If auto-paste fails: Increase paste delay in preferences
• For updates: The app will notify you automatically

SUPPORT:

• Documentation: README.md in the app bundle
• Issues: https://github.com/simo-hue/TextConverter-Pro/issues
• Discussions: https://github.com/simo-hue/TextConverter-Pro/discussions

Thank you for using TextConverter Pro!
- Simone Mattioli
EOF

# Step 6: Create postinstall script (optional)
mkdir -p "$INSTALLER_DIR/scripts"
cat > "$INSTALLER_DIR/scripts/postinstall" << 'EOF'
#!/bin/bash

# Post-installation script for TextConverter Pro
# This runs after the app is installed

echo "TextConverter Pro installed successfully!"

# Make sure the app is executable
chmod +x "/Applications/TextConverter Pro.app/Contents/MacOS/TextConverter Pro"

# Optional: Add to Login Items (you might want to make this user choice)
# osascript -e 'tell application "System Events" to make login item at end with properties {name:"TextConverter Pro", path:"/Applications/TextConverter Pro.app", hidden:false}'

exit 0
EOF
chmod +x "$INSTALLER_DIR/scripts/postinstall"

# Step 7: Create the package
echo -e "${YELLOW}🔧 Building installer package...${NC}"

# Calculate installed size
INSTALLED_SIZE=$(du -sk "$INSTALLER_DIR/payload" | cut -f1)

# Create package using pkgbuild
pkgbuild \
    --root "$INSTALLER_DIR/payload" \
    --identifier "$IDENTIFIER" \
    --version "$VERSION" \
    --install-location "/" \
    --scripts "$INSTALLER_DIR/scripts" \
    "$INSTALLER_DIR/${PKG_NAME}-${VERSION}.pkg"

# Create distribution XML for product archive
cat > "$INSTALLER_DIR/distribution.xml" << EOF
<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="2">
    <title>TextConverter Pro</title>
    <background file="background.png" mime-type="image/png" alignment="topleft" scaling="proportional"/>
    <welcome file="Welcome.txt"/>
    <license file="License.txt"/>
    <readme file="ReadMe.txt"/>

    <pkg-ref id="$IDENTIFIER"/>

    <options customize="never" require-scripts="false" hostArchitectures="x86_64,arm64"/>

    <choices-outline>
        <line choice="default">
            <line choice="$IDENTIFIER"/>
        </line>
    </choices-outline>

    <choice id="default"/>

    <choice id="$IDENTIFIER" visible="false">
        <pkg-ref id="$IDENTIFIER"/>
    </choice>

    <pkg-ref id="$IDENTIFIER" version="$VERSION" onConclusion="none">
        ${PKG_NAME}-${VERSION}.pkg
    </pkg-ref>

</installer-gui-script>
EOF

# Create the final product archive
echo -e "${YELLOW}🎁 Creating final installer...${NC}"
productbuild \
    --distribution "$INSTALLER_DIR/distribution.xml" \
    --resources "$RESOURCES_DIR" \
    --package-path "$INSTALLER_DIR" \
    "dist/${PKG_NAME}-${VERSION}.pkg"

# Step 8: Verify the package
if [ -f "dist/${PKG_NAME}-${VERSION}.pkg" ]; then
    echo -e "${GREEN}✅ Installer package created successfully!${NC}"

    # Get package size
    PKG_SIZE=$(du -sh "dist/${PKG_NAME}-${VERSION}.pkg" | cut -f1)
    echo -e "${BLUE}📊 Package size: ${PKG_SIZE}${NC}"
    echo -e "${BLUE}📁 Package location: $(pwd)/dist/${PKG_NAME}-${VERSION}.pkg${NC}"

    # Package info
    echo ""
    echo -e "${BLUE}Package Information:${NC}"
    echo "• Name: TextConverter Pro"
    echo "• Version: $VERSION"
    echo "• Identifier: $IDENTIFIER"
    echo "• Install Location: /Applications"
    echo "• Installed Size: ~$((INSTALLED_SIZE / 1024)) MB"

else
    echo -e "${RED}❌ Package creation failed!${NC}"
    exit 1
fi

# Cleanup
echo -e "${YELLOW}🧹 Cleaning up temporary files...${NC}"
rm -rf "$INSTALLER_DIR"

echo ""
echo -e "${GREEN}🎉 Installer creation completed successfully!${NC}"
echo ""
echo "Installation Instructions:"
echo "1. Double-click the .pkg file to install"
echo "2. Follow the installer prompts"
echo "3. Grant Accessibility permissions when prompted"
echo "4. Look for 'TXT' in the menu bar"
echo ""
echo "Distribution ready: dist/${PKG_NAME}-${VERSION}.pkg"