import os
import winreg
from pathlib import Path
from typing import Optional, Dict, List


class PathDetector:
    """Auto-detects Steam directory and SteamVR configuration files."""

    # Relative paths from Steam directory
    NULL_DRIVER_RELATIVE = "steamapps/common/SteamVR/drivers/null/resources/settings/default.vrsettings"
    STEAMVR_CONFIG_RELATIVE = "steamapps/common/SteamVR/resources/settings/default.vrsettings"

    @staticmethod
    def find_steam_directory() -> Optional[str]:
        """Find the Steam installation directory.

        Returns:
            Optional[str]: Path to Steam directory, or None if not found
        """
        # Try Windows registry first
        steam_path = PathDetector._check_registry()
        if steam_path and os.path.exists(steam_path):
            return steam_path

        # Check common locations
        common_paths = PathDetector.check_common_steam_locations()
        for path in common_paths:
            if os.path.exists(path):
                return path

        return None

    @staticmethod
    def _check_registry() -> Optional[str]:
        """Check Windows registry for Steam installation path.

        Returns:
            Optional[str]: Steam path from registry, or None
        """
        try:
            # Try 64-bit registry first
            key_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Valve\Steam"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam"),
            ]

            for hkey, key_path in key_paths:
                try:
                    with winreg.OpenKey(hkey, key_path) as key:
                        install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                        if install_path and os.path.exists(install_path):
                            return install_path
                except FileNotFoundError:
                    continue
                except Exception:
                    continue

        except Exception as e:
            print(f"Error checking registry: {e}")

        return None

    @staticmethod
    def check_common_steam_locations() -> List[str]:
        """Get list of common Steam installation locations.

        Returns:
            List[str]: List of possible Steam paths
        """
        locations = []

        # Common Windows locations
        locations.append(r"C:\Program Files (x86)\Steam")
        locations.append(r"C:\Program Files\Steam")

        # Check all fixed drives
        try:
            import string
            from ctypes import windll

            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(letter)
                bitmask >>= 1

            for drive in drives:
                locations.append(f"{drive}:\\Steam")
                locations.append(f"{drive}:\\Program Files (x86)\\Steam")
                locations.append(f"{drive}:\\Program Files\\Steam")
        except Exception as e:
            print(f"Error detecting drives: {e}")

        return locations

    @staticmethod
    def find_null_driver_file(steam_dir: str) -> Optional[str]:
        """Find the null driver file given a Steam directory.

        Args:
            steam_dir: Path to Steam directory

        Returns:
            Optional[str]: Path to null driver file, or None if not found
        """
        if not steam_dir:
            return None

        null_driver_path = os.path.join(steam_dir, PathDetector.NULL_DRIVER_RELATIVE)
        if os.path.exists(null_driver_path):
            return null_driver_path

        return None

    @staticmethod
    def find_steamvr_config_file(steam_dir: str) -> Optional[str]:
        """Find the SteamVR config file given a Steam directory.

        Args:
            steam_dir: Path to Steam directory

        Returns:
            Optional[str]: Path to SteamVR config file, or None if not found
        """
        if not steam_dir:
            return None

        steamvr_config_path = os.path.join(steam_dir, PathDetector.STEAMVR_CONFIG_RELATIVE)
        if os.path.exists(steamvr_config_path):
            return steamvr_config_path

        return None

    @staticmethod
    def auto_detect_all_paths() -> Dict[str, Optional[str]]:
        """Auto-detect all required paths.

        Returns:
            Dict with keys: 'steam_dir', 'null_driver', 'steamvr_config'
        """
        result = {
            'steam_dir': None,
            'null_driver': None,
            'steamvr_config': None
        }

        # Find Steam directory
        steam_dir = PathDetector.find_steam_directory()
        if not steam_dir:
            return result

        result['steam_dir'] = steam_dir

        # Find both required files
        result['null_driver'] = PathDetector.find_null_driver_file(steam_dir)
        result['steamvr_config'] = PathDetector.find_steamvr_config_file(steam_dir)

        return result

    @staticmethod
    def validate_paths(null_driver: str, steamvr_config: str) -> Dict[str, bool]:
        """Validate that both paths exist and are accessible.

        Args:
            null_driver: Path to null driver file
            steamvr_config: Path to SteamVR config file

        Returns:
            Dict with validation results
        """
        return {
            'null_driver_exists': os.path.exists(null_driver) if null_driver else False,
            'steamvr_config_exists': os.path.exists(steamvr_config) if steamvr_config else False,
            'both_valid': (
                os.path.exists(null_driver) and os.path.exists(steamvr_config)
                if null_driver and steamvr_config else False
            )
        }
