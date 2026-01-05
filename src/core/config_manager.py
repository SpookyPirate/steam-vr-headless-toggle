import json
import os
from pathlib import Path
from typing import Any, Optional
from datetime import datetime


class ConfigManager:
    """Manages application configuration persistence."""

    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "file_paths": {
            "null_driver": "",
            "steamvr_config": "",
            "steamvr_root": ""
        },
        "state": {
            "last_toggle_state": "disabled",
            "last_successful_toggle": ""
        },
        "virtual_controllers": {
            "enabled": True,
            "controller_count": 2,
            "auto_enable_with_headless": True
        },
        "ui": {
            "window_position": {
                "x": 100,
                "y": 100
            },
            "theme": "dark"
        },
        "backups": {
            "enabled": True,
            "max_backups": 5,
            "backup_directory": "backups/"
        }
    }

    def __init__(self, config_path: str = "config/app_config.json"):
        """Initialize ConfigManager.

        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.config_data = {}
        self._ensure_config_directory()
        self.load_config()

    def _ensure_config_directory(self):
        """Ensure the configuration directory exists."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> dict:
        """Load configuration from file.

        Returns:
            dict: Configuration data
        """
        if not self.config_path.exists():
            # Create default config if it doesn't exist
            self.config_data = self.DEFAULT_CONFIG.copy()
            self.save_config()
        else:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                # Merge with defaults in case new keys were added
                self._merge_with_defaults()
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using defaults.")
                self.config_data = self.DEFAULT_CONFIG.copy()
                self.save_config()

        return self.config_data

    def _merge_with_defaults(self):
        """Merge loaded config with defaults to ensure all keys exist."""
        def merge_dicts(default: dict, loaded: dict) -> dict:
            result = default.copy()
            for key, value in loaded.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result

        self.config_data = merge_dicts(self.DEFAULT_CONFIG, self.config_data)

    def save_config(self) -> bool:
        """Save configuration to file.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._ensure_config_directory()
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Dot-notation key (e.g., 'file_paths.null_driver')
            default: Default value if key not found

        Returns:
            The configuration value
        """
        keys = key.split('.')
        value = self.config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Dot-notation key (e.g., 'file_paths.null_driver')
            value: Value to set
        """
        keys = key.split('.')
        data = self.config_data

        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]

        data[keys[-1]] = value

    def get_null_driver_path(self) -> str:
        """Get the null driver file path.

        Returns:
            str: Path to null driver file
        """
        return self.get('file_paths.null_driver', '')

    def get_steamvr_config_path(self) -> str:
        """Get the SteamVR config file path.

        Returns:
            str: Path to SteamVR config file
        """
        return self.get('file_paths.steamvr_config', '')

    def set_file_paths(self, null_driver: str, steamvr_config: str) -> None:
        """Set both file paths.

        Args:
            null_driver: Path to null driver file
            steamvr_config: Path to SteamVR config file
        """
        self.set('file_paths.null_driver', null_driver)
        self.set('file_paths.steamvr_config', steamvr_config)

    def get_last_state(self) -> str:
        """Get the last toggle state.

        Returns:
            str: Last state ('enabled' or 'disabled')
        """
        return self.get('state.last_toggle_state', 'disabled')

    def set_last_state(self, state: str) -> None:
        """Set the last toggle state.

        Args:
            state: State to set ('enabled' or 'disabled')
        """
        self.set('state.last_toggle_state', state)
        self.set('state.last_successful_toggle', datetime.now().isoformat())

    def get_backup_directory(self) -> str:
        """Get the backup directory path.

        Returns:
            str: Backup directory path
        """
        return self.get('backups.backup_directory', 'backups/')

    def get_max_backups(self) -> int:
        """Get the maximum number of backups to keep.

        Returns:
            int: Maximum number of backups
        """
        return self.get('backups.max_backups', 5)

    def are_backups_enabled(self) -> bool:
        """Check if backups are enabled.

        Returns:
            bool: True if backups are enabled
        """
        return self.get('backups.enabled', True)

    def get_steamvr_root_path(self) -> str:
        """Get the SteamVR root directory path.

        Returns:
            str: Path to SteamVR root directory
        """
        return self.get('file_paths.steamvr_root', '')

    def set_steamvr_root_path(self, path: str) -> None:
        """Set the SteamVR root directory path.

        Args:
            path: Path to SteamVR root directory
        """
        self.set('file_paths.steamvr_root', path)

    def are_virtual_controllers_enabled(self) -> bool:
        """Check if virtual controllers are enabled.

        Returns:
            bool: True if virtual controllers are enabled
        """
        return self.get('virtual_controllers.enabled', True)

    def set_virtual_controllers_enabled(self, enabled: bool) -> None:
        """Set whether virtual controllers are enabled.

        Args:
            enabled: Whether to enable virtual controllers
        """
        self.set('virtual_controllers.enabled', enabled)

    def get_controller_count(self) -> int:
        """Get the number of virtual controllers.

        Returns:
            int: Number of controllers
        """
        return self.get('virtual_controllers.controller_count', 2)

    def set_controller_count(self, count: int) -> None:
        """Set the number of virtual controllers.

        Args:
            count: Number of controllers (0-4)
        """
        self.set('virtual_controllers.controller_count', count)

    def should_auto_enable_controllers(self) -> bool:
        """Check if controllers should auto-enable with headless mode.

        Returns:
            bool: True if controllers should auto-enable
        """
        return self.get('virtual_controllers.auto_enable_with_headless', True)
