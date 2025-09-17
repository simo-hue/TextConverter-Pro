"""
GitHub-based auto-updater for TextConverter Pro
"""

import json
import urllib.request
import urllib.error
import ssl
import shutil
import tempfile
import zipfile
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from .logger import get_logger
from .exceptions import ConfigurationError
from .error_handler import error_boundary, retry_on_error
from .version_manager import Version, get_current_version, format_version_for_display

@dataclass
class GitHubRelease:
    """GitHub release information"""
    tag_name: str
    name: str
    body: str
    published_at: str
    html_url: str
    download_url: str
    prerelease: bool
    size_bytes: int

    @property
    def version(self) -> Version:
        """Parse version from tag name"""
        # Remove 'v' prefix if present
        version_str = self.tag_name.lstrip('v')
        return Version.from_string(version_str)

    @property
    def published_date(self) -> datetime:
        """Parse published date"""
        return datetime.fromisoformat(self.published_at.replace('Z', '+00:00'))

    @property
    def size_mb(self) -> float:
        """Get size in MB"""
        return self.size_bytes / (1024 * 1024)

class GitHubUpdater:
    """Professional GitHub-based auto-updater"""

    def __init__(self,
                 repo_owner: str,
                 repo_name: str,
                 current_version: Optional[Version] = None,
                 check_prereleases: bool = False):

        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version or get_current_version()
        self.check_prereleases = check_prereleases
        self.logger = get_logger()

        # GitHub API URLs
        self.api_base = "https://api.github.com"
        self.releases_url = f"{self.api_base}/repos/{repo_owner}/{repo_name}/releases"
        self.latest_release_url = f"{self.releases_url}/latest"

        # Cache settings
        self.cache_duration = timedelta(hours=1)
        self.cache_file = Path.home() / "Library" / "Caches" / "TextConverter" / "update_cache.json"
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        self.logger.info("GitHub updater initialized",
                        repo=f"{repo_owner}/{repo_name}",
                        current_version=str(self.current_version))

    @retry_on_error(max_retries=3, delay=1.0)
    def check_for_updates(self, force_check: bool = False) -> Optional[GitHubRelease]:
        """Check for available updates"""
        try:
            # Check cache first (unless forced)
            if not force_check:
                cached_release = self._get_cached_release()
                if cached_release:
                    return cached_release

            # Fetch latest release from GitHub
            if self.check_prereleases:
                release_data = self._fetch_all_releases()
                if not release_data:
                    return None
                latest_data = release_data[0]  # First release is latest
            else:
                latest_data = self._fetch_latest_stable_release()
                if not latest_data:
                    return None

            # Parse release information
            release = self._parse_release_data(latest_data)

            # Check if it's newer than current version
            if release.version > self.current_version:
                # Cache the result
                self._cache_release(release)

                self.logger.info("Update available",
                               current_version=str(self.current_version),
                               latest_version=str(release.version),
                               update_type=self.current_version.get_update_type(release.version))
                return release
            else:
                self.logger.debug("No updates available",
                                current_version=str(self.current_version),
                                latest_version=str(release.version))
                return None

        except Exception as e:
            self.logger.error("Failed to check for updates", exception=e)
            raise

    @retry_on_error(max_retries=2, delay=2.0)
    def _fetch_latest_stable_release(self) -> Optional[Dict[str, Any]]:
        """Fetch latest stable release from GitHub API"""
        try:
            # Create SSL context that doesn't verify certificates (for corporate networks)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(self.latest_release_url, context=context, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    self.logger.debug("Fetched latest stable release", tag=data.get('tag_name'))
                    return data
                else:
                    self.logger.warning(f"GitHub API returned status {response.status}")
                    return None

        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.logger.warning("No releases found for repository")
                return None
            else:
                self.logger.error(f"HTTP error fetching release: {e.code}")
                raise
        except Exception as e:
            self.logger.error("Failed to fetch latest release", exception=e)
            raise

    @retry_on_error(max_retries=2, delay=2.0)
    def _fetch_all_releases(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch all releases (including prereleases)"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # Fetch first page of releases
            with urllib.request.urlopen(f"{self.releases_url}?per_page=10", context=context, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    self.logger.debug(f"Fetched {len(data)} releases")
                    return data
                else:
                    self.logger.warning(f"GitHub API returned status {response.status}")
                    return None

        except Exception as e:
            self.logger.error("Failed to fetch releases", exception=e)
            raise

    def _parse_release_data(self, data: Dict[str, Any]) -> GitHubRelease:
        """Parse GitHub release data"""
        # Find appropriate download asset (looking for .zip or .app)
        download_url = None
        asset_size = 0

        assets = data.get('assets', [])
        for asset in assets:
            name = asset.get('name', '').lower()
            if (name.endswith('.zip') or
                name.endswith('.app.zip') or
                'textconverter' in name):
                download_url = asset.get('browser_download_url')
                asset_size = asset.get('size', 0)
                break

        # Fallback to source code download
        if not download_url:
            download_url = data.get('zipball_url')

        return GitHubRelease(
            tag_name=data['tag_name'],
            name=data['name'],
            body=data.get('body', ''),
            published_at=data['published_at'],
            html_url=data['html_url'],
            download_url=download_url,
            prerelease=data.get('prerelease', False),
            size_bytes=asset_size
        )

    def _get_cached_release(self) -> Optional[GitHubRelease]:
        """Get cached release if still valid"""
        try:
            if not self.cache_file.exists():
                return None

            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)

            # Check cache age
            cached_time = datetime.fromisoformat(cache_data['cached_at'])
            if datetime.now() - cached_time > self.cache_duration:
                return None

            # Check if cached version is newer than current
            cached_release = GitHubRelease(**cache_data['release'])
            if cached_release.version > self.current_version:
                self.logger.debug("Using cached update info", version=str(cached_release.version))
                return cached_release

            return None

        except Exception as e:
            self.logger.debug("Failed to load cache", exception=e)
            return None

    def _cache_release(self, release: GitHubRelease):
        """Cache release information"""
        try:
            cache_data = {
                'cached_at': datetime.now().isoformat(),
                'release': {
                    'tag_name': release.tag_name,
                    'name': release.name,
                    'body': release.body,
                    'published_at': release.published_at,
                    'html_url': release.html_url,
                    'download_url': release.download_url,
                    'prerelease': release.prerelease,
                    'size_bytes': release.size_bytes
                }
            }

            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            self.logger.debug("Cached release info", version=str(release.version))

        except Exception as e:
            self.logger.debug("Failed to cache release", exception=e)

    @error_boundary(context="downloading update", default_return=None)
    def download_update(self, release: GitHubRelease, progress_callback: Optional[callable] = None) -> Optional[Path]:
        """Download update package"""
        try:
            self.logger.info("Starting download",
                           version=str(release.version),
                           size_mb=round(release.size_mb, 2))

            # Create temporary download location
            temp_dir = Path(tempfile.mkdtemp(prefix="textconverter_update_"))
            download_path = temp_dir / f"TextConverter_{release.tag_name}.zip"

            # Download with progress tracking
            def download_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    progress = min(downloaded / total_size, 1.0)
                    progress_callback(progress)

            urllib.request.urlretrieve(
                release.download_url,
                download_path,
                reporthook=download_progress
            )

            self.logger.info("Download completed",
                           path=str(download_path),
                           size_mb=round(download_path.stat().st_size / (1024*1024), 2))

            return download_path

        except Exception as e:
            self.logger.error("Failed to download update", exception=e)
            raise

    @error_boundary(context="installing update", default_return=False)
    def install_update(self, download_path: Path, backup_current: bool = True) -> bool:
        """Install downloaded update"""
        try:
            self.logger.info("Starting update installation", download_path=str(download_path))

            # Get current application path
            current_app_path = self._get_current_app_path()
            if not current_app_path:
                raise ConfigurationError("Could not determine current application path")

            # Create backup if requested
            backup_path = None
            if backup_current:
                backup_path = self._create_backup(current_app_path)

            # Extract update
            temp_extract_dir = Path(tempfile.mkdtemp(prefix="textconverter_extract_"))

            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_dir)

            # Find the new app bundle
            new_app_path = self._find_app_bundle(temp_extract_dir)
            if not new_app_path:
                raise ConfigurationError("Could not find app bundle in update package")

            # Install update
            self._replace_application(current_app_path, new_app_path)

            self.logger.info("Update installed successfully")

            # Cleanup
            shutil.rmtree(temp_extract_dir, ignore_errors=True)
            download_path.unlink(missing_ok=True)

            return True

        except Exception as e:
            self.logger.error("Failed to install update", exception=e)

            # Restore backup if available
            if backup_path and backup_path.exists():
                try:
                    self._restore_backup(backup_path, current_app_path)
                    self.logger.info("Restored backup after failed update")
                except Exception as restore_error:
                    self.logger.critical("Failed to restore backup", exception=restore_error)

            raise

    def _get_current_app_path(self) -> Optional[Path]:
        """Get path to current application bundle"""
        try:
            # Try to get bundle path from running process
            import sys
            executable_path = Path(sys.executable)

            # Walk up to find .app bundle
            current = executable_path
            while current.parent != current:
                if current.name.endswith('.app'):
                    return current
                current = current.parent

            # Fallback: assume we're in Applications
            app_name = "TextConverter.app"
            possible_paths = [
                Path("/Applications") / app_name,
                Path.home() / "Applications" / app_name,
            ]

            for path in possible_paths:
                if path.exists():
                    return path

            return None

        except Exception as e:
            self.logger.error("Failed to get current app path", exception=e)
            return None

    def _create_backup(self, app_path: Path) -> Path:
        """Create backup of current application"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path.home() / "Library" / "Application Support" / "TextConverter" / "Backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = backup_dir / f"TextConverter_backup_{timestamp}.app"
        shutil.copytree(app_path, backup_path)

        self.logger.info("Created backup", backup_path=str(backup_path))
        return backup_path

    def _find_app_bundle(self, extract_dir: Path) -> Optional[Path]:
        """Find app bundle in extracted directory"""
        for item in extract_dir.rglob("*.app"):
            if item.is_dir():
                return item
        return None

    def _replace_application(self, old_path: Path, new_path: Path):
        """Replace old application with new one"""
        # Move old app to temporary location
        temp_old = old_path.parent / f"{old_path.name}.old"

        if temp_old.exists():
            shutil.rmtree(temp_old)

        shutil.move(str(old_path), str(temp_old))

        try:
            # Move new app to final location
            shutil.move(str(new_path), str(old_path))

            # Remove old app
            shutil.rmtree(temp_old)

        except Exception as e:
            # Restore old app if new installation failed
            if temp_old.exists() and not old_path.exists():
                shutil.move(str(temp_old), str(old_path))
            raise

    def _restore_backup(self, backup_path: Path, target_path: Path):
        """Restore application from backup"""
        if target_path.exists():
            shutil.rmtree(target_path)
        shutil.copytree(backup_path, target_path)

    def get_release_notes(self, release: GitHubRelease) -> str:
        """Format release notes for display"""
        notes = release.body or "No release notes available."

        # Add some basic formatting
        formatted_notes = f"""Version {format_version_for_display(release.version)}
Released: {release.published_date.strftime('%B %d, %Y')}

{notes}

Download size: {release.size_mb:.1f} MB
"""
        return formatted_notes

    def open_release_page(self, release: GitHubRelease):
        """Open release page in default browser"""
        try:
            import webbrowser
            webbrowser.open(release.html_url)
            self.logger.info("Opened release page", url=release.html_url)
        except Exception as e:
            self.logger.error("Failed to open release page", exception=e)

# Global updater instance
_updater_instance: Optional[GitHubUpdater] = None

def get_github_updater(repo_owner: str = "simonemattioli",
                      repo_name: str = "textconverter-pro") -> GitHubUpdater:
    """Get or create the global GitHub updater instance"""
    global _updater_instance
    if _updater_instance is None:
        _updater_instance = GitHubUpdater(repo_owner, repo_name)
    return _updater_instance