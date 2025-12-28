import ctypes
import sys
import os
from typing import List


def is_admin() -> bool:
    """Check if the current process has administrator privileges.

    Returns:
        bool: True if running as administrator
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False


def run_as_admin(argv: List[str] = None) -> bool:
    """Re-launch the current script with administrator privileges.

    Args:
        argv: Command line arguments (defaults to sys.argv)

    Returns:
        bool: True if elevation was requested successfully
    """
    if argv is None:
        argv = sys.argv

    try:
        if hasattr(sys, '_MEIPASS'):
            # Running as PyInstaller bundle
            script = sys.executable
        else:
            # Running as Python script
            script = os.path.abspath(sys.argv[0])

        params = ' '.join([f'"{arg}"' for arg in argv[1:]])

        # Use ShellExecuteW to request elevation
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            script,
            params,
            None,
            1  # SW_SHOWNORMAL
        )

        # Return value > 32 indicates success
        return ret > 32

    except Exception as e:
        print(f"Error requesting admin elevation: {e}")
        return False


def needs_admin_for_files(file_paths: List[str]) -> bool:
    """Check if admin privileges are needed to write to files.

    Args:
        file_paths: List of file paths to check

    Returns:
        bool: True if any file requires admin access
    """
    if not file_paths:
        return False

    for file_path in file_paths:
        if not file_path:
            continue

        try:
            # Check if file exists
            if os.path.exists(file_path):
                # Try to open file in append mode to test write access
                try:
                    with open(file_path, 'a'):
                        pass
                except (IOError, OSError, PermissionError):
                    # Cannot write to file
                    return True
            else:
                # File doesn't exist, check parent directory
                parent_dir = os.path.dirname(file_path)
                if parent_dir and not os.access(parent_dir, os.W_OK):
                    return True

        except Exception:
            # On any error, assume admin is needed
            return True

    return False


def request_admin_elevation() -> bool:
    """Request administrator elevation for the current process.

    This will re-launch the application with elevated privileges.

    Returns:
        bool: True if elevation was requested successfully
    """
    if is_admin():
        return True  # Already running as admin

    # Re-launch with admin rights
    return run_as_admin(sys.argv)
