#!/bin/bash

# Professional release creation script for TextConverter Pro
# This script creates GitHub releases with proper versioning

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_OWNER="simo-hue"
REPO_NAME="TextConverter-Pro"
BUILD_DIR="dist"
RELEASE_DIR="release"

echo -e "${BLUE}🚀 TextConverter Pro Release Creator${NC}"
echo "=================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install with: brew install gh"
    exit 1
fi

# Check if logged into GitHub
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged into GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Get current version from version_manager.py
CURRENT_VERSION=$(python3 -c "
import sys
import os
sys.path.insert(0, os.path.join('src'))
from utils.version_manager import get_current_version
print(get_current_version().to_string())
")

echo -e "${BLUE}Current version: ${CURRENT_VERSION}${NC}"

# Ask for new version
echo ""
echo "What type of release is this?"
echo "1) Patch (bug fixes) - ${CURRENT_VERSION} → $(python3 -c "
import sys, os
sys.path.insert(0, 'src')
from utils.version_manager import get_current_version, bump_version
print(bump_version(get_current_version(), 'patch').to_string())
")"
echo "2) Minor (new features) - ${CURRENT_VERSION} → $(python3 -c "
import sys, os
sys.path.insert(0, 'src')
from utils.version_manager import get_current_version, bump_version
print(bump_version(get_current_version(), 'minor').to_string())
")"
echo "3) Major (breaking changes) - ${CURRENT_VERSION} → $(python3 -c "
import sys, os
sys.path.insert(0, 'src')
from utils.version_manager import get_current_version, bump_version
print(bump_version(get_current_version(), 'major').to_string())
")"
echo "4) Custom version"

read -p "Enter choice (1-4): " version_choice

case $version_choice in
    1)
        NEW_VERSION=$(python3 -c "
import sys, os
sys.path.insert(0, 'src')
from utils.version_manager import get_current_version, bump_version
print(bump_version(get_current_version(), 'patch').to_string())
")
        ;;
    2)
        NEW_VERSION=$(python3 -c "
import sys, os
sys.path.insert(0, 'src')
from utils.version_manager import get_current_version, bump_version
print(bump_version(get_current_version(), 'minor').to_string())
")
        ;;
    3)
        NEW_VERSION=$(python3 -c "
import sys, os
sys.path.insert(0, 'src')
from utils.version_manager import get_current_version, bump_version
print(bump_version(get_current_version(), 'major').to_string())
")
        ;;
    4)
        read -p "Enter custom version (e.g., 1.2.3): " NEW_VERSION
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}New version: ${NEW_VERSION}${NC}"

# Confirm release
echo ""
read -p "Create release v${NEW_VERSION}? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Release cancelled"
    exit 0
fi

# Update version in code
echo -e "${YELLOW}📝 Updating version in code...${NC}"
python3 -c "
import sys, os, re
sys.path.insert(0, 'src')

# Update version_manager.py
version_file = 'src/utils/version_manager.py'
with open(version_file, 'r') as f:
    content = f.read()

# Replace version string
content = re.sub(
    r'CURRENT_VERSION = Version\.from_string\(\"[^\"]+\"\)',
    f'CURRENT_VERSION = Version.from_string(\"${NEW_VERSION}\")',
    content
)

with open(version_file, 'w') as f:
    f.write(content)

print('✅ Updated version in code')
"

# Build the application
echo -e "${YELLOW}🔨 Building application...${NC}"
./scripts/build.sh

if [ ! -f "${BUILD_DIR}/text_converter_app.app" ]; then
    echo -e "${RED}❌ Build failed - app not found${NC}"
    exit 1
fi

# Create release directory
echo -e "${YELLOW}📦 Creating release package...${NC}"
rm -rf "${RELEASE_DIR}"
mkdir -p "${RELEASE_DIR}"

# Create app bundle zip
cd "${BUILD_DIR}"
zip -r "../${RELEASE_DIR}/TextConverter-v${NEW_VERSION}-macOS.zip" text_converter_app.app
cd ..

# Create source code zip
git archive --format=zip --output="${RELEASE_DIR}/TextConverter-v${NEW_VERSION}-Source.zip" HEAD

# Generate release notes
echo -e "${YELLOW}📋 Generating release notes...${NC}"

# Get commits since last tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LAST_TAG" ]; then
    COMMITS=$(git log ${LAST_TAG}..HEAD --oneline --no-merges)
else
    COMMITS=$(git log --oneline --no-merges -10)  # Last 10 commits if no tags
fi

# Create release notes file
cat > "${RELEASE_DIR}/release_notes.md" << EOF
# TextConverter Pro v${NEW_VERSION}

## What's New

<!-- Add your release highlights here -->
- Improved performance and stability
- Bug fixes and optimizations

## Changes

$(echo "$COMMITS" | sed 's/^/- /')

## Installation

### macOS App Bundle
1. Download \`TextConverter-v${NEW_VERSION}-macOS.zip\`
2. Extract and move \`text_converter_app.app\` to \`/Applications/\`
3. Grant Accessibility permissions in System Preferences
4. Launch TextConverter from Applications

### Build from Source
1. Download \`TextConverter-v${NEW_VERSION}-Source.zip\`
2. Extract and run \`./scripts/build.sh\`
3. Follow installation instructions above

## System Requirements
- macOS 10.12 or later
- Python 3.8+ (for source builds)

## Documentation
- [User Guide](https://github.com/${REPO_OWNER}/${REPO_NAME}#usage)
- [Configuration](https://github.com/${REPO_OWNER}/${REPO_NAME}#configuration)
- [Troubleshooting](https://github.com/${REPO_OWNER}/${REPO_NAME}#troubleshooting)
EOF

echo -e "${BLUE}📋 Release notes created at ${RELEASE_DIR}/release_notes.md${NC}"
echo "Edit the release notes now if needed, then press Enter to continue..."
read

# Commit version bump
echo -e "${YELLOW}📝 Committing version bump...${NC}"
git add src/utils/version_manager.py
git commit -m "Bump version to v${NEW_VERSION}" || true

# Create and push tag
echo -e "${YELLOW}🏷️  Creating git tag...${NC}"
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"
git push origin "v${NEW_VERSION}"
git push origin main

# Create GitHub release
echo -e "${YELLOW}🚀 Creating GitHub release...${NC}"
gh release create "v${NEW_VERSION}" \
    --title "TextConverter Pro v${NEW_VERSION}" \
    --notes-file "${RELEASE_DIR}/release_notes.md" \
    "${RELEASE_DIR}/TextConverter-v${NEW_VERSION}-macOS.zip" \
    "${RELEASE_DIR}/TextConverter-v${NEW_VERSION}-Source.zip"

# Get release URL
RELEASE_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/tag/v${NEW_VERSION}"

echo ""
echo -e "${GREEN}✅ Release created successfully!${NC}"
echo -e "${BLUE}🔗 Release URL: ${RELEASE_URL}${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Test the release download and installation"
echo "2. Update any documentation if needed"
echo "3. Announce the release to users"
echo ""
echo -e "${GREEN}🎉 Release v${NEW_VERSION} is now live!${NC}"

# Cleanup
rm -rf "${RELEASE_DIR}"
echo "Cleaned up temporary files"