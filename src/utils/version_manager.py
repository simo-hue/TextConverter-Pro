"""
Professional version management and update checking system
"""

import re
from typing import Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Version:
    """Semantic version representation"""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None

    @classmethod
    def from_string(cls, version_str: str) -> 'Version':
        """Parse version string (e.g., '1.2.3-beta.1+build.123')"""
        # Regex for semantic versioning
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$'
        match = re.match(pattern, version_str.strip())

        if not match:
            raise ValueError(f"Invalid version string: {version_str}")

        major, minor, patch, prerelease, build = match.groups()

        return cls(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            prerelease=prerelease,
            build=build
        )

    def to_string(self) -> str:
        """Convert to version string"""
        version = f"{self.major}.{self.minor}.{self.patch}"

        if self.prerelease:
            version += f"-{self.prerelease}"

        if self.build:
            version += f"+{self.build}"

        return version

    def __str__(self) -> str:
        return self.to_string()

    def __lt__(self, other: 'Version') -> bool:
        """Compare versions (less than)"""
        # Compare major.minor.patch
        self_tuple = (self.major, self.minor, self.patch)
        other_tuple = (other.major, other.minor, other.patch)

        if self_tuple != other_tuple:
            return self_tuple < other_tuple

        # Handle prerelease versions (1.0.0-alpha < 1.0.0)
        if self.prerelease and not other.prerelease:
            return True
        elif not self.prerelease and other.prerelease:
            return False
        elif self.prerelease and other.prerelease:
            return self.prerelease < other.prerelease

        return False

    def __eq__(self, other: 'Version') -> bool:
        """Compare versions (equality)"""
        return (
            self.major == other.major and
            self.minor == other.minor and
            self.patch == other.patch and
            self.prerelease == other.prerelease
        )

    def __le__(self, other: 'Version') -> bool:
        return self < other or self == other

    def __gt__(self, other: 'Version') -> bool:
        return not self <= other

    def __ge__(self, other: 'Version') -> bool:
        return not self < other

    def is_stable(self) -> bool:
        """Check if this is a stable release (no prerelease)"""
        return self.prerelease is None

    def is_major_update(self, other: 'Version') -> bool:
        """Check if other version is a major update from this one"""
        return other.major > self.major

    def is_minor_update(self, other: 'Version') -> bool:
        """Check if other version is a minor update from this one"""
        return other.major == self.major and other.minor > self.minor

    def is_patch_update(self, other: 'Version') -> bool:
        """Check if other version is a patch update from this one"""
        return (other.major == self.major and
                other.minor == self.minor and
                other.patch > self.patch)

    def get_update_type(self, other: 'Version') -> Optional[str]:
        """Get update type relative to another version"""
        if other <= self:
            return None

        if self.is_major_update(other):
            return "major"
        elif self.is_minor_update(other):
            return "minor"
        elif self.is_patch_update(other):
            return "patch"
        else:
            return "prerelease"

# Current application version
CURRENT_VERSION = Version.from_string("1.0.0")

def get_current_version() -> Version:
    """Get current application version"""
    return CURRENT_VERSION

def bump_version(current: Version, bump_type: str) -> Version:
    """Bump version based on type"""
    if bump_type == "major":
        return Version(current.major + 1, 0, 0)
    elif bump_type == "minor":
        return Version(current.major, current.minor + 1, 0)
    elif bump_type == "patch":
        return Version(current.major, current.minor, current.patch + 1)
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

def format_version_for_display(version: Version) -> str:
    """Format version for user display"""
    base = f"v{version.major}.{version.minor}.{version.patch}"

    if version.prerelease:
        base += f" ({version.prerelease})"

    return base