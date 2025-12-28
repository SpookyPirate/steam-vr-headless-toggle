import os
from typing import Tuple
from src.core.file_manager import FileManager


class FileValidator:
    """Validates VR settings files."""

    # Required keys for null driver file
    NULL_DRIVER_REQUIRED_KEYS = [
        'driver_null.enable'
    ]

    # Required keys for SteamVR config file
    STEAMVR_CONFIG_REQUIRED_KEYS = [
        'steamvr.requireHmd',
        'steamvr.forcedDriver',
        'steamvr.activateMultipleDrivers'
    ]

    @staticmethod
    def validate_null_driver_file(file_path: str) -> Tuple[bool, str]:
        """Validate the null driver file structure.

        Args:
            file_path: Path to null driver file

        Returns:
            Tuple of (valid, error_message)
        """
        if not file_path:
            return False, "No file path provided"

        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        # Check if file is writable
        if not FileManager.check_file_writable(file_path):
            return False, f"File is not writable: {file_path}"

        # Validate JSON structure
        valid, error = FileManager.validate_json_structure(
            file_path,
            FileValidator.NULL_DRIVER_REQUIRED_KEYS
        )

        if not valid:
            return False, f"Invalid null driver file structure: {error}"

        return True, ""

    @staticmethod
    def validate_steamvr_config_file(file_path: str) -> Tuple[bool, str]:
        """Validate the SteamVR config file structure.

        Args:
            file_path: Path to SteamVR config file

        Returns:
            Tuple of (valid, error_message)
        """
        if not file_path:
            return False, "No file path provided"

        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        # Check if file is writable
        if not FileManager.check_file_writable(file_path):
            return False, f"File is not writable: {file_path}"

        # Validate JSON structure
        valid, error = FileManager.validate_json_structure(
            file_path,
            FileValidator.STEAMVR_CONFIG_REQUIRED_KEYS
        )

        if not valid:
            return False, f"Invalid SteamVR config file structure: {error}"

        return True, ""

    @staticmethod
    def validate_both_files(null_driver_path: str, steamvr_config_path: str) -> Tuple[bool, str]:
        """Validate both files.

        Args:
            null_driver_path: Path to null driver file
            steamvr_config_path: Path to SteamVR config file

        Returns:
            Tuple of (valid, error_message)
        """
        # Validate null driver
        valid, error = FileValidator.validate_null_driver_file(null_driver_path)
        if not valid:
            return False, error

        # Validate SteamVR config
        valid, error = FileValidator.validate_steamvr_config_file(steamvr_config_path)
        if not valid:
            return False, error

        return True, ""

    @staticmethod
    def check_file_writable(file_path: str) -> bool:
        """Check if a file is writable.

        Args:
            file_path: Path to file

        Returns:
            bool: True if writable
        """
        return FileManager.check_file_writable(file_path)

    @staticmethod
    def check_json_integrity(file_path: str) -> bool:
        """Check if a file contains valid JSON.

        Args:
            file_path: Path to file

        Returns:
            bool: True if valid JSON
        """
        success, _, _ = FileManager.read_json_file(file_path)
        return success

    @staticmethod
    def get_file_permissions(file_path: str) -> dict:
        """Get detailed file permission information.

        Args:
            file_path: Path to file

        Returns:
            dict: Permission information
        """
        result = {
            'exists': False,
            'readable': False,
            'writable': False,
            'size': 0
        }

        if not os.path.exists(file_path):
            return result

        result['exists'] = True
        result['readable'] = os.access(file_path, os.R_OK)
        result['writable'] = os.access(file_path, os.W_OK)

        try:
            result['size'] = os.path.getsize(file_path)
        except:
            pass

        return result
