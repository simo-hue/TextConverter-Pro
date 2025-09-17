#!/bin/bash

echo "🔨 Building Text Converter for macOS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo -e "${RED}❌ Error: setup.py not found. Run this script from the project root.${NC}"
    exit 1
fi

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

# Clean previous builds
echo -e "${YELLOW}🧹 Cleaning previous builds...${NC}"
rm -rf build/ dist/

# Build the app
echo -e "${YELLOW}🏗️ Building macOS app bundle...${NC}"
python3 setup.py py2app

# Check if build succeeded
if [ -d "dist/text_converter_app.app" ]; then
    echo -e "${GREEN}✅ App built successfully!${NC}"
    echo ""
    echo -e "${GREEN}📁 Location: $(pwd)/dist/text_converter_app.app${NC}"
    echo ""
    echo -e "${YELLOW}🚀 To install:${NC}"
    echo "   1. Copy dist/text_converter_app.app to /Applications/"
    echo "   2. Open the app from Finder"
    echo "   3. Grant Accessibility permissions in System Preferences"
    echo "   4. Look for 'TXT' icon in menu bar"
    echo ""
    echo -e "${YELLOW}🔧 To auto-start on login:${NC}"
    echo "   System Preferences → Users & Groups → Login Items"
    echo ""
    echo -e "${YELLOW}📋 Global shortcuts:${NC}"
    echo "   ⌘⇧U = UPPERCASE"
    echo "   ⌘⇧L = lowercase"
    echo "   ⌘⇧C = Capitalize"
else
    echo -e "${RED}❌ Build failed - app not found in dist/${NC}"
    exit 1
fi