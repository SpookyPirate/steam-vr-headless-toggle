"""
Virtual Controller Manager
Handles enabling/disabling virtual VR controllers for headless mode.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Tuple, Optional


class ControllerManager:
    """Manages virtual VR controller driver installation and configuration."""

    def __init__(self, steamvr_path: str):
        """Initialize ControllerManager.

        Args:
            steamvr_path: Path to SteamVR installation (e.g., C:/Program Files (x86)/Steam/steamapps/common/SteamVR)
        """
        self.steamvr_path = Path(steamvr_path)
        self.drivers_path = self.steamvr_path / "drivers"
        # Use our custom virtual controller driver
        self.driver_name = "virtual_controller"
        self.driver_install_path = self.drivers_path / self.driver_name

        # Path to bundled driver in our application
        # Support both development and PyInstaller bundled paths
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.bundled_driver_path = Path(sys._MEIPASS) / "drivers" / self.driver_name
        else:
            # Running as script
            self.bundled_driver_path = Path(__file__).parent.parent.parent / "drivers" / self.driver_name

    def is_driver_installed(self) -> bool:
        """Check if virtual controller driver is installed in SteamVR.

        Returns:
            bool: True if driver is installed in SteamVR
        """
        # Check if driver is installed in SteamVR (not just bundled with app)
        driver_dll = self.driver_install_path / "bin" / "win64" / "driver_virtual_controller.dll"
        return driver_dll.exists()

    def install_driver(self) -> Tuple[bool, str]:
        """Install the virtual controller driver to SteamVR.

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not self.bundled_driver_path.exists():
                return False, f"Bundled driver not found at {self.bundled_driver_path}"

            # Check if DLL exists
            driver_dll = self.bundled_driver_path / "bin" / "win64" / "driver_virtual_controller.dll"
            if not driver_dll.exists():
                return False, (
                    "Driver DLL not found. Please build the driver first.\n\n"
                    "See driver_source/BUILD_INSTRUCTIONS.md for details."
                )

            if not self.drivers_path.exists():
                return False, f"SteamVR drivers directory not found at {self.drivers_path}"

            # Copy driver to SteamVR drivers folder
            if self.driver_install_path.exists():
                shutil.rmtree(self.driver_install_path)

            shutil.copytree(self.bundled_driver_path, self.driver_install_path)

            return True, ""

        except PermissionError:
            return False, "Permission denied. Administrator privileges required."
        except Exception as e:
            return False, f"Failed to install driver: {str(e)}"

    def uninstall_driver(self) -> Tuple[bool, str]:
        """Uninstall the virtual controller driver from SteamVR.

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not self.driver_install_path.exists():
                return True, ""  # Already uninstalled

            shutil.rmtree(self.driver_install_path)
            return True, ""

        except PermissionError:
            return False, "Permission denied. Administrator privileges required."
        except Exception as e:
            return False, f"Failed to uninstall driver: {str(e)}"

    def configure_controller_count(self, count: int) -> Tuple[bool, str]:
        """Configure the number of virtual controllers.

        Args:
            count: Number of controllers (1-4)

        Returns:
            Tuple of (success, error_message)
        """
        if count < 0 or count > 4:
            return False, "Controller count must be between 0 and 4"

        try:
            # Path to driver config file
            config_path = self.driver_install_path / "resources" / "settings" / "default.vrsettings"

            if not config_path.exists():
                # Create config if it doesn't exist
                config_path.parent.mkdir(parents=True, exist_ok=True)
                config_data = {}
            else:
                # Read existing config
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

            # Update controller count for our custom driver
            if 'driver_virtualcontroller' not in config_data:
                config_data['driver_virtualcontroller'] = {}

            config_data['driver_virtualcontroller']['controller_count'] = count
            config_data['driver_virtualcontroller']['enable'] = count > 0

            # Write updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=3)

            return True, ""

        except Exception as e:
            return False, f"Failed to configure controller count: {str(e)}"

    def enable_controllers(self, count: int = 2) -> Tuple[bool, str]:
        """Enable virtual controllers.

        Args:
            count: Number of controllers to spawn (default 2)

        Returns:
            Tuple of (success, error_message)
        """
        # Install driver if not already installed
        if not self.is_driver_installed():
            success, error = self.install_driver()
            if not success:
                return False, error

        # Configure controller count
        success, error = self.configure_controller_count(count)
        if not success:
            return False, error

        return True, ""

    def disable_controllers(self) -> Tuple[bool, str]:
        """Disable virtual controllers by setting count to 0.

        Returns:
            Tuple of (success, error_message)
        """
        if not self.is_driver_installed():
            return True, ""  # Already disabled

        # Set controller count to 0 instead of uninstalling
        # This is faster and preserves settings
        success, error = self.configure_controller_count(0)
        if not success:
            return False, error

        return True, ""

    def get_controller_count(self) -> int:
        """Get the current configured controller count.

        Returns:
            int: Number of configured controllers (0 if driver not installed or config not found)
        """
        try:
            config_path = self.driver_install_path / "resources" / "settings" / "default.vrsettings"

            if not config_path.exists():
                return 0

            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            return config_data.get('driver_virtual_controller', {}).get('controller_count', 0)

        except Exception:
            return 0

    def validate_steamvr_path(self) -> Tuple[bool, str]:
        """Validate that the SteamVR path is correct.

        Returns:
            Tuple of (valid, error_message)
        """
        if not self.steamvr_path.exists():
            return False, f"SteamVR path does not exist: {self.steamvr_path}"

        if not self.drivers_path.exists():
            return False, f"SteamVR drivers folder not found: {self.drivers_path}"

        return True, ""
