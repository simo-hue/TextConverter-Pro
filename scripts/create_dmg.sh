#!/bin/bash

# Professional DMG Creator for TextConverter Pro
# Creates a beautiful drag-and-drop disk image installer

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}💿 Creating DMG Installer for TextConverter Pro${NC}"
echo "=================================================="

# Configuration
APP_NAME="TextConverter Pro"
DMG_NAME="TextConverter-Pro"
VERSION="1.0.0"
BUILD_DIR="dist"
DMG_DIR="dmg_build"

# Step 1: Verify .app bundle exists
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo -e "${RED}❌ App bundle not found!${NC}"
    echo "Please run ./scripts/build_app.sh first"
    exit 1
fi

# Step 2: Prepare DMG directory
echo -e "${YELLOW}📁 Preparing DMG contents...${NC}"
rm -rf "$DMG_DIR"
mkdir -p "$DMG_DIR"

# Copy app to DMG directory
cp -R "dist/${APP_NAME}.app" "$DMG_DIR/"

# Create Applications symlink for drag-and-drop
ln -s /Applications "$DMG_DIR/Applications"

# Step 3: Create README for DMG
cat > "$DMG_DIR/README.txt" << 'EOF'
TextConverter Pro v1.0.0

INSTALLATION INSTRUCTIONS:

1. Drag "TextConverter Pro" to the "Applications" folder
2. Open Applications folder and launch TextConverter Pro
3. Grant Accessibility permissions in System Preferences
4. Look for "TXT" icon in your menu bar

QUICK START:

• Select text anywhere on your Mac
• Copy with ⌘C
• Press hotkeys to convert:
  - ⌘⇧U = UPPERCASE
  - ⌘⇧L = lowercase
  - ⌘⇧C = Capitalize Case

FEATURES:

✨ Instant text conversion with global hotkeys
📊 Professional analytics and insights
🔄 Auto-updates from GitHub
⚙️ Comprehensive settings and customization
🎨 Native macOS integration

SUPPORT:

📚 Documentation: https://github.com/simo-hue/TextConverter-Pro
🐛 Issues: https://github.com/simo-hue/TextConverter-Pro/issues
💬 Discussions: https://github.com/simo-hue/TextConverter-Pro/discussions

Thank you for choosing TextConverter Pro!
- Simone Mattioli (https://github.com/simo-hue)
EOF

# Step 4: Setup custom background image
echo -e "${YELLOW}🎨 Setting up DMG background...${NC}"
mkdir -p "$DMG_DIR/.background"
cp "background_installer.png" "$DMG_DIR/.background/background.png"

# Step 5: Create temporary DMG
echo -e "${YELLOW}💿 Creating disk image...${NC}"

# Calculate size needed (add 50MB buffer)
SIZE=$(du -sm "$DMG_DIR" | cut -f1)
SIZE=$((SIZE + 50))

# Create writable DMG
hdiutil create -srcfolder "$DMG_DIR" -volname "$APP_NAME" -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" -format UDRW -size "${SIZE}m" \
    "temp_${DMG_NAME}.dmg"

# Step 6: Mount and customize DMG
echo -e "${YELLOW}⚙️  Customizing DMG layout...${NC}"

# Mount the DMG
DEVICE=$(hdiutil attach -readwrite -noverify "temp_${DMG_NAME}.dmg" | \
         egrep '^/dev/' | sed 1q | awk '{print $1}')

# Wait for mount
sleep 2

# Set DMG window properties using AppleScript
osascript << 'EOF'
tell application "Finder"
    tell disk "TextConverter Pro"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false

        -- Set window size and position
        set the bounds of container window to {100, 100, 600, 400}

        -- Set icon view options
        set opts to the icon view options of container window
        set arrangement of opts to not arranged
        set icon size of opts to 128
        set background picture of opts to file ".background:background.png"

        -- Position icons
        set position of item "TextConverter Pro.app" of container window to {150, 200}
        set position of item "Applications" of container window to {350, 200}
        set position of item "README.txt" of container window to {250, 300}

        -- Update and close
        update without registering applications
        delay 2
        close
    end tell
end tell
EOF

# Sync filesystem
sync

# Unmount
hdiutil detach "$DEVICE"

# Step 7: Convert to compressed, read-only DMG
echo -e "${YELLOW}🗜️  Compressing final DMG...${NC}"

hdiutil convert "temp_${DMG_NAME}.dmg" -format UDZO -imagekey zlib-level=9 \
    -o "dist/${DMG_NAME}-${VERSION}.dmg"

# Step 8: Verify the DMG
if [ -f "dist/${DMG_NAME}-${VERSION}.dmg" ]; then
    echo -e "${GREEN}✅ DMG created successfully!${NC}"

    # Get DMG size
    DMG_SIZE=$(du -sh "dist/${DMG_NAME}-${VERSION}.dmg" | cut -f1)
    echo -e "${BLUE}📊 DMG size: ${DMG_SIZE}${NC}"
    echo -e "${BLUE}📁 DMG location: $(pwd)/dist/${DMG_NAME}-${VERSION}.dmg${NC}"

    # Test mount
    echo -e "${YELLOW}🧪 Testing DMG mount...${NC}"
    hdiutil attach "dist/${DMG_NAME}-${VERSION}.dmg" -verify
    sleep 2
    hdiutil detach "/Volumes/${APP_NAME}" || true

    echo -e "${GREEN}✅ DMG verification completed${NC}"

else
    echo -e "${RED}❌ DMG creation failed!${NC}"
    exit 1
fi

# Cleanup
echo -e "${YELLOW}🧹 Cleaning up temporary files...${NC}"
rm -f "temp_${DMG_NAME}.dmg"
rm -rf "$DMG_DIR"

echo ""
echo -e "${GREEN}🎉 DMG creation completed successfully!${NC}"
echo ""
echo "User Installation Instructions:"
echo "1. Double-click the .dmg file"
echo "2. Drag TextConverter Pro to Applications folder"
echo "3. Launch from Applications"
echo "4. Grant permissions when prompted"
echo ""
echo "Distribution ready: dist/${DMG_NAME}-${VERSION}.dmg"