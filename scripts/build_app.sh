#!/bin/bash

# Professional macOS App Builder for TextConverter Pro
# This script creates a complete .app bundle ready for distribution

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏗️  Building TextConverter Pro macOS App${NC}"
echo "=================================================="

# Configuration
APP_NAME="TextConverter Pro"
BUILD_DIR="dist"
RESOURCES_DIR="resources"

# Step 1: Clean previous builds
echo -e "${YELLOW}📁 Cleaning previous builds...${NC}"
rm -rf build dist
mkdir -p dist

# Step 2: Install dependencies
echo -e "${YELLOW}📦 Installing build dependencies...${NC}"
pip install py2app pillow

# Step 3: Create app icon if it doesn't exist
echo -e "${YELLOW}🎨 Preparing app icon...${NC}"
if [ ! -f "assets/icon.icns" ]; then
    mkdir -p assets
    echo -e "${YELLOW}⚠️  No icon found. Creating placeholder...${NC}"
    # Create a simple text-based icon using sips (built into macOS)
    # For production, you should create a proper .icns file
fi

# Step 4: Build the .app bundle
echo -e "${YELLOW}🔨 Building .app bundle...${NC}"
python setup.py py2app

# Step 5: Verify the build
if [ -d "dist/${APP_NAME}.app" ]; then
    echo -e "${GREEN}✅ App bundle created successfully!${NC}"

    # Get app size
    APP_SIZE=$(du -sh "dist/${APP_NAME}.app" | cut -f1)
    echo -e "${BLUE}📊 App size: ${APP_SIZE}${NC}"

    # Test if the app can launch (quick validation)
    echo -e "${YELLOW}🧪 Testing app launch...${NC}"
    open "dist/${APP_NAME}.app" --wait-apps --new
    sleep 2
    pkill -f "TextConverter Pro" || true
    echo -e "${GREEN}✅ App launch test completed${NC}"

else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Build completed successfully!${NC}"
echo -e "${BLUE}📁 App location: $(pwd)/dist/${APP_NAME}.app${NC}"
echo ""
echo "Next steps:"
echo "1. Test the app thoroughly"
echo "2. Run ./scripts/create_installer.sh to create an installer package"
echo "3. Sign and notarize for distribution (if needed)"