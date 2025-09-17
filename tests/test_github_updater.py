#!/usr/bin/env python3
"""
Unit tests for GitHub updater system
"""

import unittest
import tempfile
import os
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.version_manager import Version
from src.utils.github_updater import GitHubUpdater, GitHubRelease

class TestVersionManager(unittest.TestCase):
    """Test cases for version management"""

    def test_version_parsing(self):
        """Test version string parsing"""
        # Basic version
        v1 = Version.from_string("1.2.3")
        self.assertEqual(v1.major, 1)
        self.assertEqual(v1.minor, 2)
        self.assertEqual(v1.patch, 3)
        self.assertIsNone(v1.prerelease)

        # Prerelease version
        v2 = Version.from_string("2.0.0-beta.1")
        self.assertEqual(v2.major, 2)
        self.assertEqual(v2.minor, 0)
        self.assertEqual(v2.patch, 0)
        self.assertEqual(v2.prerelease, "beta.1")

        # Version with build
        v3 = Version.from_string("1.0.0+build.123")
        self.assertEqual(v3.build, "build.123")

    def test_version_comparison(self):
        """Test version comparison logic"""
        v1_0_0 = Version.from_string("1.0.0")
        v1_0_1 = Version.from_string("1.0.1")
        v1_1_0 = Version.from_string("1.1.0")
        v2_0_0 = Version.from_string("2.0.0")
        v1_0_0_beta = Version.from_string("1.0.0-beta")

        # Basic comparisons
        self.assertTrue(v1_0_0 < v1_0_1)
        self.assertTrue(v1_0_1 < v1_1_0)
        self.assertTrue(v1_1_0 < v2_0_0)

        # Prerelease comparisons
        self.assertTrue(v1_0_0_beta < v1_0_0)
        self.assertFalse(v1_0_0 < v1_0_0_beta)

        # Equality
        self.assertEqual(v1_0_0, Version.from_string("1.0.0"))

    def test_update_type_detection(self):
        """Test update type detection"""
        v1_0_0 = Version.from_string("1.0.0")
        v1_0_1 = Version.from_string("1.0.1")
        v1_1_0 = Version.from_string("1.1.0")
        v2_0_0 = Version.from_string("2.0.0")

        self.assertEqual(v1_0_0.get_update_type(v1_0_1), "patch")
        self.assertEqual(v1_0_0.get_update_type(v1_1_0), "minor")
        self.assertEqual(v1_0_0.get_update_type(v2_0_0), "major")
        self.assertIsNone(v1_0_1.get_update_type(v1_0_0))  # Downgrade

    def test_version_string_output(self):
        """Test version string generation"""
        v1 = Version(1, 2, 3)
        self.assertEqual(str(v1), "1.2.3")

        v2 = Version(1, 2, 3, "beta.1")
        self.assertEqual(str(v2), "1.2.3-beta.1")

        v3 = Version(1, 2, 3, "beta.1", "build.123")
        self.assertEqual(str(v3), "1.2.3-beta.1+build.123")

class TestGitHubRelease(unittest.TestCase):
    """Test cases for GitHubRelease"""

    def test_github_release_creation(self):
        """Test GitHubRelease creation and properties"""
        release = GitHubRelease(
            tag_name="v1.2.3",
            name="Version 1.2.3",
            body="Release notes",
            published_at="2024-01-01T12:00:00Z",
            html_url="https://github.com/owner/repo/releases/tag/v1.2.3",
            download_url="https://github.com/owner/repo/releases/download/v1.2.3/app.zip",
            prerelease=False,
            size_bytes=1048576
        )

        self.assertEqual(release.version.major, 1)
        self.assertEqual(release.version.minor, 2)
        self.assertEqual(release.version.patch, 3)
        self.assertEqual(release.size_mb, 1.0)
        self.assertFalse(release.prerelease)

    def test_tag_name_parsing(self):
        """Test parsing version from tag names"""
        # With 'v' prefix
        release1 = GitHubRelease(
            tag_name="v1.2.3",
            name="", body="", published_at="2024-01-01T12:00:00Z",
            html_url="", download_url="", prerelease=False, size_bytes=0
        )
        self.assertEqual(release1.version, Version.from_string("1.2.3"))

        # Without 'v' prefix
        release2 = GitHubRelease(
            tag_name="2.0.0-beta",
            name="", body="", published_at="2024-01-01T12:00:00Z",
            html_url="", download_url="", prerelease=True, size_bytes=0
        )
        self.assertEqual(release2.version, Version.from_string("2.0.0-beta"))

class TestGitHubUpdater(unittest.TestCase):
    """Test cases for GitHubUpdater"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = Path(self.temp_dir) / "update_cache.json"

        # Create updater with test settings
        self.updater = GitHubUpdater("testowner", "testrepo", Version.from_string("1.0.0"))
        self.updater.cache_file = self.cache_file

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_updater_initialization(self):
        """Test updater initialization"""
        self.assertEqual(self.updater.repo_owner, "testowner")
        self.assertEqual(self.updater.repo_name, "testrepo")
        self.assertEqual(self.updater.current_version, Version.from_string("1.0.0"))

    @patch('urllib.request.urlopen')
    def test_fetch_latest_release_success(self, mock_urlopen):
        """Test successful release fetching"""
        # Mock response data
        mock_response_data = {
            "tag_name": "v1.1.0",
            "name": "Version 1.1.0",
            "body": "Bug fixes and improvements",
            "published_at": "2024-01-01T12:00:00Z",
            "html_url": "https://github.com/testowner/testrepo/releases/tag/v1.1.0",
            "prerelease": False,
            "assets": [{
                "name": "testapp.zip",
                "browser_download_url": "https://github.com/testowner/testrepo/releases/download/v1.1.0/testapp.zip",
                "size": 1048576
            }]
        }

        # Mock urllib response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(mock_response_data).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Test check for updates
        release = self.updater.check_for_updates(force_check=True)

        self.assertIsNotNone(release)
        self.assertEqual(release.version, Version.from_string("1.1.0"))
        self.assertEqual(release.size_bytes, 1048576)

    @patch('urllib.request.urlopen')
    def test_no_update_available(self, mock_urlopen):
        """Test when no update is available"""
        # Mock response for same version
        mock_response_data = {
            "tag_name": "v1.0.0",
            "name": "Version 1.0.0",
            "body": "Initial release",
            "published_at": "2024-01-01T12:00:00Z",
            "html_url": "https://github.com/testowner/testrepo/releases/tag/v1.0.0",
            "prerelease": False,
            "assets": []
        }

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(mock_response_data).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Test check for updates
        release = self.updater.check_for_updates(force_check=True)

        self.assertIsNone(release)

    def test_cache_functionality(self):
        """Test update cache functionality"""
        # Create a test release
        test_release = GitHubRelease(
            tag_name="v1.1.0",
            name="Test Release",
            body="Test notes",
            published_at="2024-01-01T12:00:00Z",
            html_url="https://example.com",
            download_url="https://example.com/download",
            prerelease=False,
            size_bytes=1024
        )

        # Cache the release
        self.updater._cache_release(test_release)

        # Check that cache file exists
        self.assertTrue(self.cache_file.exists())

        # Test loading from cache
        cached_release = self.updater._get_cached_release()
        self.assertIsNotNone(cached_release)
        self.assertEqual(cached_release.version, test_release.version)

    def test_expired_cache(self):
        """Test that expired cache is ignored"""
        # Create cache data with old timestamp
        cache_data = {
            'cached_at': (datetime.now() - timedelta(hours=25)).isoformat(),  # Older than 24 hours
            'release': {
                'tag_name': 'v1.1.0',
                'name': 'Test',
                'body': '',
                'published_at': '2024-01-01T12:00:00Z',
                'html_url': '',
                'download_url': '',
                'prerelease': False,
                'size_bytes': 0
            }
        }

        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f)

        # Should return None for expired cache
        cached_release = self.updater._get_cached_release()
        self.assertIsNone(cached_release)

    def test_parse_release_data(self):
        """Test parsing of GitHub API release data"""
        api_data = {
            "tag_name": "v2.0.0-beta.1",
            "name": "Beta Release",
            "body": "Beta testing release",
            "published_at": "2024-01-01T12:00:00Z",
            "html_url": "https://github.com/testowner/testrepo/releases/tag/v2.0.0-beta.1",
            "prerelease": True,
            "assets": [{
                "name": "textconverter-beta.zip",
                "browser_download_url": "https://example.com/download.zip",
                "size": 2097152
            }]
        }

        release = self.updater._parse_release_data(api_data)

        self.assertEqual(release.version, Version.from_string("2.0.0-beta.1"))
        self.assertTrue(release.prerelease)
        self.assertEqual(release.size_mb, 2.0)
        self.assertEqual(release.download_url, "https://example.com/download.zip")

    def test_get_release_notes_formatting(self):
        """Test release notes formatting"""
        release = GitHubRelease(
            tag_name="v1.2.0",
            name="Version 1.2.0",
            body="## New Features\n- Feature 1\n- Feature 2\n\n## Bug Fixes\n- Fix 1",
            published_at="2024-01-15T10:30:00Z",
            html_url="",
            download_url="",
            prerelease=False,
            size_bytes=1572864  # 1.5 MB
        )

        notes = self.updater.get_release_notes(release)

        self.assertIn("Version v1.2.0", notes)
        self.assertIn("January 15, 2024", notes)
        self.assertIn("1.5 MB", notes)
        self.assertIn("## New Features", notes)

if __name__ == "__main__":
    unittest.main()