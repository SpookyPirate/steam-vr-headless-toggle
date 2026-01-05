"""
Automatic driver installer for virtual controllers.
Downloads and installs the OpenVR InputEmulator driver automatically.
"""

import os
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Tuple, Optional


class DriverInstaller:
    """Handles automatic download and installation of virtual controller drivers."""

    # OpenVR InputEmulator download URL
    DRIVER_DOWNLOAD_URL = "https://github.com/matzman666/OpenVR-InputEmulator/releases/download/v1.3/OpenVR-InputEmulator-v1.3.exe"
    DRIVER_VERSION = "v1.3"

    def __init__(self, app_root: Path, steamvr_path: str):
        """Initialize the driver installer.

        Args:
            app_root: Root directory of the application
            steamvr_path: Path to SteamVR installation
        """
        self.app_root = Path(app_root)
        self.steamvr_path = Path(steamvr_path)
        self.driver_dest = self.app_root / "drivers" / "virtual_controller" / "bin" / "win64" / "driver_virtual_controller.dll"

    def is_driver_installed(self) -> bool:
        """Check if the virtual controller driver is already installed.

        Returns:
            bool: True if driver DLL exists
        """
        return self.driver_dest.exists()

    def download_installer(self, progress_callback=None) -> Tuple[bool, str, Optional[Path]]:
        """Download the OpenVR InputEmulator installer.

        Args:
            progress_callback: Optional callback function(downloaded, total) for progress updates

        Returns:
            Tuple of (success, error_message, installer_path)
        """
        try:
            # Create temp directory for download
            temp_dir = Path(tempfile.gettempdir()) / "steamvr_headless_driver"
            temp_dir.mkdir(exist_ok=True)
            installer_path = temp_dir / "OpenVR-InputEmulator.exe"

            # Clean up old installer if exists
            if installer_path.exists():
                try:
                    installer_path.unlink()
                except:
                    pass

            # Download with progress
            def report_progress(block_num, block_size, total_size):
                if progress_callback:
                    downloaded = block_num * block_size
                    progress_callback(downloaded, total_size)

            urllib.request.urlretrieve(
                self.DRIVER_DOWNLOAD_URL,
                installer_path,
                reporthook=report_progress
            )

            return True, "", installer_path

        except Exception as e:
            return False, f"Failed to download installer: {str(e)}", None

    def cleanup_temp_files(self):
        """Clean up temporary installer files."""
        try:
            temp_dir = Path(tempfile.gettempdir()) / "steamvr_headless_driver"
            if temp_dir.exists():
                for file in temp_dir.glob("*.exe"):
                    try:
                        file.unlink()
                    except:
                        pass
        except:
            pass

    def extract_driver_from_steamvr(self) -> Tuple[bool, str]:
        """Extract the driver DLL from SteamVR installation after InputEmulator is installed.

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Look for InputEmulator driver in SteamVR
            input_emulator_dll = self.steamvr_path / "drivers" / "00vrinputemulator" / "bin" / "win64" / "driver_00vrinputemulator.dll"

            if not input_emulator_dll.exists():
                return False, f"InputEmulator driver not found at: {input_emulator_dll}"

            # Create destination directory
            self.driver_dest.parent.mkdir(parents=True, exist_ok=True)

            # Copy the DLL
            shutil.copy2(input_emulator_dll, self.driver_dest)

            return True, ""

        except Exception as e:
            return False, f"Failed to extract driver: {str(e)}"

    def run_installer(self, installer_path: Path) -> Tuple[bool, str]:
        """Run the OpenVR InputEmulator installer with admin privileges.

        Args:
            installer_path: Path to the installer executable

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Run installer with admin elevation using ShellExecute
            import ctypes

            # ShellExecute with 'runas' verb to request elevation
            result = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",  # Request elevation
                str(installer_path),
                None,
                None,
                1  # SW_SHOWNORMAL
            )

            # ShellExecute returns a value > 32 on success
            if result <= 32:
                return False, f"Failed to start installer (error code: {result})"

            return True, ""

        except Exception as e:
            return False, f"Failed to run installer: {str(e)}"

    def install_driver_automatic(self, progress_callback=None, status_callback=None) -> Tuple[bool, str]:
        """Automatically download and install the virtual controller driver.

        Args:
            progress_callback: Optional callback(downloaded, total) for download progress
            status_callback: Optional callback(status_message) for status updates

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Step 1: Download installer
            if status_callback:
                status_callback("Downloading OpenVR InputEmulator...")

            success, error, installer_path = self.download_installer(progress_callback)
            if not success:
                return False, error

            # Step 2: Run installer
            if status_callback:
                status_callback("Running installer... (please complete the installation)")

            success, error = self.run_installer(installer_path)
            if not success:
                return False, error

            # Step 3: Extract driver from SteamVR
            if status_callback:
                status_callback("Extracting driver...")

            success, error = self.extract_driver_from_steamvr()
            if not success:
                return False, error

            # Step 4: Cleanup
            try:
                installer_path.unlink()
            except:
                pass  # Ignore cleanup errors

            if status_callback:
                status_callback("Driver installed successfully!")

            return True, ""

        except Exception as e:
            return False, f"Unexpected error during installation: {str(e)}"

    def install_driver_from_local(self, installer_path: str) -> Tuple[bool, str]:
        """Install driver from a locally provided installer file.

        Args:
            installer_path: Path to local installer executable

        Returns:
            Tuple of (success, error_message)
        """
        installer = Path(installer_path)
        if not installer.exists():
            return False, f"Installer not found: {installer_path}"

        # Run the local installer
        success, error = self.run_installer(installer)
        if not success:
            return False, error

        # Extract the driver
        return self.extract_driver_from_steamvr()

    def get_installation_info(self) -> dict:
        """Get information about the driver installation status.

        Returns:
            dict: Installation status information
        """
        return {
            "installed": self.is_driver_installed(),
            "driver_path": str(self.driver_dest),
            "driver_exists": self.driver_dest.exists(),
            "driver_size": self.driver_dest.stat().st_size if self.driver_dest.exists() else 0,
            "steamvr_path": str(self.steamvr_path),
            "version": self.DRIVER_VERSION
        }
