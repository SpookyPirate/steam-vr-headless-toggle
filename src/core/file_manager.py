import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from datetime import datetime


class FileManager:
    """Handles safe JSON file operations with backups and atomic writes."""

    @staticmethod
    def read_json_file(file_path: str) -> Tuple[bool, Optional[Dict], str]:
        """Read a JSON file safely.

        Args:
            file_path: Path to the JSON file

        Returns:
            Tuple of (success, data, error_message)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return True, data, ""
        except FileNotFoundError:
            return False, None, f"File not found: {file_path}"
        except json.JSONDecodeError as e:
            return False, None, f"Invalid JSON in {file_path}: {str(e)}"
        except IOError as e:
            return False, None, f"Error reading {file_path}: {str(e)}"
        except Exception as e:
            return False, None, f"Unexpected error reading {file_path}: {str(e)}"

    @staticmethod
    def write_json_file(file_path: str, data: Dict, indent: int = 3) -> Tuple[bool, str]:
        """Write JSON data to file using atomic write operation.

        Args:
            file_path: Path to the JSON file
            data: Data to write
            indent: Indentation level (default 3 for SteamVR format)

        Returns:
            Tuple of (success, error_message)
        """
        try:
            file_path = Path(file_path)
            dir_path = file_path.parent

            # Create temporary file in the same directory
            with tempfile.NamedTemporaryFile(
                mode='w',
                dir=dir_path,
                delete=False,
                suffix='.tmp',
                encoding='utf-8'
            ) as tmp_file:
                json.dump(data, tmp_file, indent=indent, ensure_ascii=False)
                tmp_path = tmp_file.name

            # Atomic rename (replace original with temp)
            shutil.move(tmp_path, str(file_path))

            return True, ""
        except IOError as e:
            return False, f"Error writing to {file_path}: {str(e)}"
        except Exception as e:
            # Clean up temp file if it exists
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass
            return False, f"Unexpected error writing to {file_path}: {str(e)}"

    @staticmethod
    def backup_file(file_path: str, backup_dir: str = "backups") -> Tuple[bool, str, str]:
        """Create a backup of a file.

        Args:
            file_path: Path to file to backup
            backup_dir: Directory to store backups

        Returns:
            Tuple of (success, backup_path, error_message)
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False, "", f"File not found: {file_path}"

            # Create backup directory if it doesn't exist
            backup_dir_path = Path(backup_dir)
            backup_dir_path.mkdir(parents=True, exist_ok=True)

            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            backup_filename = f"{file_path.stem}.backup.{timestamp}{file_path.suffix}"
            backup_path = backup_dir_path / backup_filename

            # Copy file to backup location
            shutil.copy2(file_path, backup_path)

            return True, str(backup_path), ""
        except IOError as e:
            return False, "", f"Error creating backup: {str(e)}"
        except Exception as e:
            return False, "", f"Unexpected error creating backup: {str(e)}"

    @staticmethod
    def restore_file(backup_path: str, original_path: str) -> Tuple[bool, str]:
        """Restore a file from backup.

        Args:
            backup_path: Path to backup file
            original_path: Path to restore to

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not os.path.exists(backup_path):
                return False, f"Backup file not found: {backup_path}"

            shutil.copy2(backup_path, original_path)
            return True, ""
        except IOError as e:
            return False, f"Error restoring backup: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error restoring backup: {str(e)}"

    @staticmethod
    def validate_json_structure(file_path: str, required_keys: list) -> Tuple[bool, str]:
        """Validate that a JSON file contains required keys.

        Args:
            file_path: Path to JSON file
            required_keys: List of required keys (dot notation supported)

        Returns:
            Tuple of (valid, error_message)
        """
        success, data, error = FileManager.read_json_file(file_path)
        if not success:
            return False, error

        missing_keys = []
        for key_path in required_keys:
            keys = key_path.split('.')
            current = data

            for key in keys:
                if not isinstance(current, dict) or key not in current:
                    missing_keys.append(key_path)
                    break
                current = current[key]

        if missing_keys:
            return False, f"Missing required keys: {', '.join(missing_keys)}"

        return True, ""

    @staticmethod
    def modify_json_value(file_path: str, key_path: str, new_value: Any, backup_dir: str = "backups") -> Tuple[bool, str]:
        """Safely modify a specific value in a JSON file.

        This method:
        1. Creates a backup
        2. Reads the JSON
        3. Modifies the specific value
        4. Writes atomically
        5. Validates the write
        6. Rolls back on error

        Args:
            file_path: Path to JSON file
            key_path: Dot-notation path to key (e.g., 'steamvr.requireHmd')
            new_value: New value to set
            backup_dir: Directory for backups

        Returns:
            Tuple of (success, error_message)
        """
        # Create backup first
        success, backup_path, error = FileManager.backup_file(file_path, backup_dir)
        if not success:
            return False, f"Backup failed: {error}"

        try:
            # Read current data
            success, data, error = FileManager.read_json_file(file_path)
            if not success:
                return False, error

            # Navigate to the key and modify
            keys = key_path.split('.')
            current = data

            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]

            # Set the new value
            current[keys[-1]] = new_value

            # Write atomically
            success, error = FileManager.write_json_file(file_path, data)
            if not success:
                # Restore from backup on write failure
                FileManager.restore_file(backup_path, file_path)
                return False, error

            # Verify the write by reading back
            success, verify_data, error = FileManager.read_json_file(file_path)
            if not success or verify_data != data:
                # Restore from backup on verification failure
                FileManager.restore_file(backup_path, file_path)
                return False, "Write verification failed. Changes reverted."

            return True, ""

        except Exception as e:
            # Restore from backup on any error
            FileManager.restore_file(backup_path, file_path)
            return False, f"Error modifying file: {str(e)}. Changes reverted."

    @staticmethod
    def cleanup_old_backups(backup_dir: str, max_backups: int = 5):
        """Remove old backups, keeping only the most recent ones.

        Args:
            backup_dir: Directory containing backups
            max_backups: Maximum number of backups to keep per file
        """
        try:
            backup_dir_path = Path(backup_dir)
            if not backup_dir_path.exists():
                return

            # Group backups by original filename
            backups_by_file = {}
            for backup_file in backup_dir_path.glob("*.backup.*"):
                # Extract original filename (everything before .backup.)
                original_name = backup_file.name.split('.backup.')[0]
                if original_name not in backups_by_file:
                    backups_by_file[original_name] = []
                backups_by_file[original_name].append(backup_file)

            # For each file, keep only the most recent backups
            for original_name, backups in backups_by_file.items():
                # Sort by modification time (newest first)
                backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)

                # Remove old backups
                for old_backup in backups[max_backups:]:
                    try:
                        old_backup.unlink()
                    except Exception as e:
                        print(f"Error removing old backup {old_backup}: {e}")

        except Exception as e:
            print(f"Error cleaning up backups: {e}")

    @staticmethod
    def check_file_writable(file_path: str) -> bool:
        """Check if a file is writable.

        Args:
            file_path: Path to file

        Returns:
            bool: True if writable, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                # Check if parent directory is writable
                parent_dir = os.path.dirname(file_path)
                return os.access(parent_dir, os.W_OK)
            else:
                return os.access(file_path, os.W_OK)
        except Exception:
            return False
