"""
Update management UI and user interaction
"""

import rumps
import threading
from typing import Optional, Callable
from pathlib import Path
from datetime import datetime, timedelta

from ..utils.github_updater import GitHubUpdater, GitHubRelease, get_github_updater
from ..utils.version_manager import Version, format_version_for_display
from ..utils.settings import get_settings_manager
from ..utils.logger import get_logger
from ..utils.error_handler import safe_execute

class UpdateManager:
    """Manages update checking and user interaction"""

    def __init__(self, notification_callback: Optional[Callable] = None):
        self.settings_manager = get_settings_manager()
        self.logger = get_logger()
        self.notification_callback = notification_callback

        # Initialize GitHub updater
        self.updater = get_github_updater()

        # Update checking state
        self.last_check_time: Optional[datetime] = None
        self.available_update: Optional[GitHubRelease] = None
        self.update_in_progress = False

        # Schedule periodic checks if enabled
        self.setup_periodic_checks()

    def setup_periodic_checks(self):
        """Setup periodic update checking"""
        if self.settings_manager.settings.behavior.check_updates:
            # Check every 24 hours
            timer = rumps.Timer(self.check_for_updates_background, 24 * 60 * 60)
            timer.start()
            self.logger.info("Periodic update checking enabled")

            # Also check on startup (after 30 seconds)
            startup_timer = rumps.Timer(self.check_for_updates_background, 30)
            startup_timer.count = 1  # Run only once
            startup_timer.start()

    def create_update_menu(self) -> rumps.MenuItem:
        """Create update management menu"""
        update_menu = rumps.MenuItem("🔄 Updates")

        if self.available_update:
            # Update available
            version_str = format_version_for_display(self.available_update.version)
            update_menu.add([
                rumps.MenuItem(f"✨ Update Available: {version_str}", callback=None),
                rumps.separator,
                rumps.MenuItem("📥 Download and Install", callback=self.start_update_process),
                rumps.MenuItem("📋 View Release Notes", callback=self.show_release_notes),
                rumps.MenuItem("🌐 Open GitHub Page", callback=self.open_github_page),
                rumps.separator,
                rumps.MenuItem("⏭️ Skip This Version", callback=self.skip_version),
                rumps.MenuItem("🔍 Check Again", callback=self.manual_check_updates),
            ])
        else:
            # No update or unknown status
            last_check_text = "Never"
            if self.last_check_time:
                time_diff = datetime.now() - self.last_check_time
                if time_diff.days > 0:
                    last_check_text = f"{time_diff.days} days ago"
                elif time_diff.seconds > 3600:
                    last_check_text = f"{time_diff.seconds // 3600} hours ago"
                else:
                    last_check_text = "Recently"

            update_menu.add([
                rumps.MenuItem("✅ Up to Date", callback=None),
                rumps.MenuItem(f"Last checked: {last_check_text}", callback=None),
                rumps.separator,
                rumps.MenuItem("🔍 Check for Updates", callback=self.manual_check_updates),
                rumps.MenuItem("⚙️ Update Settings", callback=self.show_update_settings),
            ])

        return update_menu

    def manual_check_updates(self, _=None):
        """Manually check for updates (user-initiated)"""
        if self.update_in_progress:
            self._show_notification("🔄 Update Check", "Update check already in progress")
            return

        self._show_notification("🔍 Checking Updates", "Checking for new versions...")

        def check_updates():
            self.check_for_updates_background(show_no_update_notification=True)

        threading.Thread(target=check_updates, daemon=True).start()

    def check_for_updates_background(self, show_no_update_notification: bool = False):
        """Check for updates in background"""
        try:
            self.logger.info("Checking for updates...")

            # Check if updates are enabled
            if not self.settings_manager.settings.behavior.check_updates:
                self.logger.debug("Update checking disabled in settings")
                return

            self.update_in_progress = True
            release = self.updater.check_for_updates(force_check=True)
            self.last_check_time = datetime.now()

            if release:
                self.available_update = release
                update_type = self.updater.current_version.get_update_type(release.version)

                self.logger.info("Update available",
                               version=str(release.version),
                               update_type=update_type)

                # Show notification about available update
                self._show_update_available_notification(release, update_type)

            else:
                self.available_update = None
                self.logger.info("No updates available")

                if show_no_update_notification:
                    self._show_notification("✅ Up to Date", "You have the latest version")

        except Exception as e:
            self.logger.error("Failed to check for updates", exception=e)
            if show_no_update_notification:
                self._show_notification("❌ Update Check Failed", "Could not check for updates")

        finally:
            self.update_in_progress = False

    def _show_update_available_notification(self, release: GitHubRelease, update_type: str):
        """Show notification about available update"""
        version_str = format_version_for_display(release.version)

        # Customize notification based on update type
        if update_type == "major":
            title = "🚀 Major Update Available"
            message = f"TextConverter {version_str} is available with new features!"
        elif update_type == "minor":
            title = "✨ Update Available"
            message = f"TextConverter {version_str} is available with improvements!"
        else:
            title = "🔧 Update Available"
            message = f"TextConverter {version_str} is available with bug fixes!"

        self._show_notification(title, message)

    def start_update_process(self, _=None):
        """Start the update download and installation process"""
        if not self.available_update:
            return

        if self.update_in_progress:
            self._show_notification("🔄 Update in Progress", "Update is already in progress")
            return

        # Show confirmation dialog
        result = rumps.alert(
            title="Confirm Update",
            message=f"Download and install TextConverter {format_version_for_display(self.available_update.version)}?\n\n"
                   f"Size: {self.available_update.size_mb:.1f} MB\n"
                   f"The application will restart after installation.",
            ok="Update Now",
            cancel="Cancel"
        )

        if result == 1:  # OK clicked
            self._download_and_install_update()

    def _download_and_install_update(self):
        """Download and install update in background"""
        def update_process():
            try:
                self.update_in_progress = True
                release = self.available_update

                self.logger.info("Starting update process", version=str(release.version))

                # Show download progress
                self._show_notification("📥 Downloading Update", f"Downloading {format_version_for_display(release.version)}...")

                # Download update with progress tracking
                progress_notification_sent = False

                def progress_callback(progress):
                    nonlocal progress_notification_sent
                    if progress > 0.5 and not progress_notification_sent:
                        self._show_notification("📥 Download Progress", f"Download {int(progress * 100)}% complete")
                        progress_notification_sent = True

                download_path = self.updater.download_update(release, progress_callback)

                if not download_path:
                    raise Exception("Download failed")

                self._show_notification("🔧 Installing Update", "Installing update...")

                # Install update
                success = self.updater.install_update(download_path, backup_current=True)

                if success:
                    self.logger.info("Update installed successfully")

                    # Show success dialog and offer to restart
                    result = rumps.alert(
                        title="Update Complete",
                        message=f"TextConverter has been updated to {format_version_for_display(release.version)}!\n\n"
                               f"The application needs to restart to use the new version.",
                        ok="Restart Now",
                        cancel="Restart Later"
                    )

                    if result == 1:  # Restart now
                        self._restart_application()
                    else:
                        self._show_notification("✅ Update Complete", "Restart when convenient to use new version")

                    # Clear available update
                    self.available_update = None

                else:
                    raise Exception("Installation failed")

            except Exception as e:
                self.logger.error("Update process failed", exception=e)
                self._show_notification("❌ Update Failed", f"Update failed: {str(e)}")

                # Show detailed error dialog
                rumps.alert(
                    title="Update Failed",
                    message=f"The update could not be installed:\n\n{str(e)}\n\n"
                           f"You can try again later or download manually from GitHub."
                )

            finally:
                self.update_in_progress = False

        threading.Thread(target=update_process, daemon=True).start()

    def show_release_notes(self, _=None):
        """Show release notes for available update"""
        if not self.available_update:
            return

        release_notes = self.updater.get_release_notes(self.available_update)

        # Show in a dialog (rumps has limited text display, so truncate if needed)
        if len(release_notes) > 1000:
            release_notes = release_notes[:1000] + "\n\n... (view full notes on GitHub)"

        rumps.alert(
            title="Release Notes",
            message=release_notes
        )

    def open_github_page(self, _=None):
        """Open GitHub releases page"""
        if self.available_update:
            self.updater.open_release_page(self.available_update)
        else:
            # Open general releases page
            import webbrowser
            url = f"https://github.com/{self.updater.repo_owner}/{self.updater.repo_name}/releases"
            webbrowser.open(url)

    def skip_version(self, _=None):
        """Skip this version update"""
        if not self.available_update:
            return

        result = rumps.alert(
            title="Skip Version",
            message=f"Skip TextConverter {format_version_for_display(self.available_update.version)}?\n\n"
                   f"You won't be notified about this version again.",
            ok="Skip",
            cancel="Cancel"
        )

        if result == 1:  # Skip
            # TODO: Add skipped versions to settings
            self.available_update = None
            self._show_notification("⏭️ Version Skipped", "This version will be skipped")

    def show_update_settings(self, _=None):
        """Show update-related settings"""
        current_setting = self.settings_manager.settings.behavior.check_updates

        result = rumps.alert(
            title="Update Settings",
            message=f"Automatic update checking is currently {'enabled' if current_setting else 'disabled'}.\n\n"
                   f"When enabled, TextConverter checks for updates daily.",
            ok="Toggle Setting",
            cancel="Cancel"
        )

        if result == 1:  # Toggle
            new_setting = not current_setting
            self.settings_manager.update_behavior(check_updates=new_setting)

            status = "enabled" if new_setting else "disabled"
            self._show_notification("⚙️ Settings Updated", f"Automatic update checking {status}")

            if new_setting:
                self.setup_periodic_checks()

    def _restart_application(self):
        """Restart the application"""
        try:
            import sys
            import os

            # Get current executable path
            executable = sys.executable

            # Schedule restart using launchctl (macOS)
            restart_script = f'''
            #!/bin/bash
            sleep 2
            open "{executable}"
            '''

            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(restart_script)
                script_path = f.name

            os.chmod(script_path, 0o755)
            os.system(f'"{script_path}" &')

            # Quit current instance
            rumps.quit_application()

        except Exception as e:
            self.logger.error("Failed to restart application", exception=e)
            self._show_notification("❌ Restart Failed", "Please restart manually")

    def _show_notification(self, title: str, message: str):
        """Show notification using callback or rumps"""
        try:
            if self.notification_callback:
                self.notification_callback(title, message)
            else:
                rumps.notification(title, None, message, sound=False)
        except Exception as e:
            self.logger.error("Failed to show notification", exception=e)

    def get_update_status_text(self) -> str:
        """Get current update status as text"""
        if self.available_update:
            version_str = format_version_for_display(self.available_update.version)
            return f"Update available: {version_str}"
        elif self.last_check_time:
            time_diff = datetime.now() - self.last_check_time
            if time_diff.days > 7:
                return "Check for updates"
            else:
                return "Up to date"
        else:
            return "Check for updates"