from enum import Enum
from typing import Tuple
from src.core.file_manager import FileManager
from src.utils.validators import FileValidator


class ToggleState(Enum):
    """Represents the current toggle state."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    UNKNOWN = "unknown"


class StateManager:
    """Manages VR toggle state and coordinates file modifications."""

    def __init__(self, null_driver_path: str, steamvr_config_path: str, backup_dir: str = "backups"):
        """Initialize StateManager.

        Args:
            null_driver_path: Path to null driver file
            steamvr_config_path: Path to SteamVR config file
            backup_dir: Directory for backups
        """
        self.null_driver_path = null_driver_path
        self.steamvr_config_path = steamvr_config_path
        self.backup_dir = backup_dir
        self.file_manager = FileManager()

    def get_current_state(self) -> ToggleState:
        """Determine the current VR mode state by reading the files.

        Returns:
            ToggleState: Current state
        """
        try:
            # Read null driver file
            success, null_data, error = self.file_manager.read_json_file(self.null_driver_path)
            if not success:
                return ToggleState.ERROR

            # Read SteamVR config file
            success, steamvr_data, error = self.file_manager.read_json_file(self.steamvr_config_path)
            if not success:
                return ToggleState.ERROR

            # Check if VR mode is enabled
            null_enabled = null_data.get('driver_null', {}).get('enable', False)
            require_hmd = steamvr_data.get('steamvr', {}).get('requireHmd', True)
            forced_driver = steamvr_data.get('steamvr', {}).get('forcedDriver', '')
            activate_multiple = steamvr_data.get('steamvr', {}).get('activateMultipleDrivers', False)

            # Enabled state: null driver enabled, requireHmd false, forcedDriver "null", activateMultipleDrivers true
            if null_enabled and not require_hmd and forced_driver == "null" and activate_multiple:
                return ToggleState.ENABLED

            # Disabled state: null driver disabled, requireHmd true, forcedDriver "", activateMultipleDrivers false
            if not null_enabled and require_hmd and forced_driver == "" and not activate_multiple:
                return ToggleState.DISABLED

            # Mixed state - return unknown
            return ToggleState.UNKNOWN

        except Exception as e:
            print(f"Error getting current state: {e}")
            return ToggleState.ERROR

    def toggle(self) -> Tuple[bool, str, ToggleState]:
        """Toggle between enabled and disabled states.

        Returns:
            Tuple of (success, error_message, new_state)
        """
        current_state = self.get_current_state()

        if current_state == ToggleState.ERROR:
            return False, "Cannot determine current state", ToggleState.ERROR

        # Determine target state
        if current_state == ToggleState.DISABLED or current_state == ToggleState.UNKNOWN:
            # Enable VR mode
            return self.enable_simulated_vr()
        else:
            # Disable VR mode
            return self.disable_simulated_vr()

    def enable_simulated_vr(self) -> Tuple[bool, str, ToggleState]:
        """Enable simulated VR mode (null driver).

        Returns:
            Tuple of (success, error_message, new_state)
        """
        try:
            # Verify files first
            valid, error = self.verify_files()
            if not valid:
                return False, error, ToggleState.ERROR

            # Modify null driver file
            success, error = self._modify_null_driver(True)
            if not success:
                return False, f"Failed to modify null driver: {error}", ToggleState.ERROR

            # Modify SteamVR config file
            success, error = self._modify_steamvr_config(True)
            if not success:
                # Rollback null driver change
                self._modify_null_driver(False)
                return False, f"Failed to modify SteamVR config: {error}", ToggleState.ERROR

            # Verify the changes
            new_state = self.get_current_state()
            if new_state != ToggleState.ENABLED:
                return False, "State verification failed", ToggleState.ERROR

            return True, "", ToggleState.ENABLED

        except Exception as e:
            return False, f"Unexpected error: {str(e)}", ToggleState.ERROR

    def disable_simulated_vr(self) -> Tuple[bool, str, ToggleState]:
        """Disable simulated VR mode (restore normal mode).

        Returns:
            Tuple of (success, error_message, new_state)
        """
        try:
            # Verify files first
            valid, error = self.verify_files()
            if not valid:
                return False, error, ToggleState.ERROR

            # Modify null driver file
            success, error = self._modify_null_driver(False)
            if not success:
                return False, f"Failed to modify null driver: {error}", ToggleState.ERROR

            # Modify SteamVR config file
            success, error = self._modify_steamvr_config(False)
            if not success:
                # Rollback null driver change
                self._modify_null_driver(True)
                return False, f"Failed to modify SteamVR config: {error}", ToggleState.ERROR

            # Verify the changes
            new_state = self.get_current_state()
            if new_state != ToggleState.DISABLED:
                return False, "State verification failed", ToggleState.ERROR

            return True, "", ToggleState.DISABLED

        except Exception as e:
            return False, f"Unexpected error: {str(e)}", ToggleState.ERROR

    def verify_files(self) -> Tuple[bool, str]:
        """Verify that both files are valid and writable.

        Returns:
            Tuple of (valid, error_message)
        """
        return FileValidator.validate_both_files(
            self.null_driver_path,
            self.steamvr_config_path
        )

    def _modify_null_driver(self, enable: bool) -> Tuple[bool, str]:
        """Modify the null driver enable setting.

        Args:
            enable: True to enable, False to disable

        Returns:
            Tuple of (success, error_message)
        """
        return self.file_manager.modify_json_value(
            self.null_driver_path,
            'driver_null.enable',
            enable,
            self.backup_dir
        )

    def _modify_steamvr_config(self, enable: bool) -> Tuple[bool, str]:
        """Modify the SteamVR config settings.

        Args:
            enable: True to enable simulated VR, False to disable

        Returns:
            Tuple of (success, error_message)
        """
        if enable:
            # Enable: requireHmd=false, forcedDriver="null", activateMultipleDrivers=true
            require_hmd = False
            forced_driver = "null"
            activate_multiple = True
        else:
            # Disable: requireHmd=true, forcedDriver="", activateMultipleDrivers=false
            require_hmd = True
            forced_driver = ""
            activate_multiple = False

        # Modify requireHmd
        success, error = self.file_manager.modify_json_value(
            self.steamvr_config_path,
            'steamvr.requireHmd',
            require_hmd,
            self.backup_dir
        )
        if not success:
            return False, error

        # Modify forcedDriver
        success, error = self.file_manager.modify_json_value(
            self.steamvr_config_path,
            'steamvr.forcedDriver',
            forced_driver,
            self.backup_dir
        )
        if not success:
            return False, error

        # Modify activateMultipleDrivers
        success, error = self.file_manager.modify_json_value(
            self.steamvr_config_path,
            'steamvr.activateMultipleDrivers',
            activate_multiple,
            self.backup_dir
        )
        if not success:
            return False, error

        return True, ""
