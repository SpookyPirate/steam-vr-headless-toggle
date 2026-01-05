"""
Helper script to extract virtual controller driver from OpenVR InputEmulator installer.

This script will:
1. Run the installer (requires admin rights)
2. Copy the driver DLL from SteamVR installation
3. Place it in the correct location for this app
"""

import os
import shutil
import subprocess
from pathlib import Path


def find_steam_vr():
    """Find SteamVR installation directory."""
    # Common Steam installation paths
    possible_paths = [
        r"C:\Program Files (x86)\Steam\steamapps\common\SteamVR",
        r"C:\Program Files\Steam\steamapps\common\SteamVR",
        r"D:\Steam\steamapps\common\SteamVR",
        r"E:\Steam\steamapps\common\SteamVR",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def extract_driver():
    """Extract driver from installed InputEmulator."""
    print("OpenVR InputEmulator Driver Extractor")
    print("=" * 50)

    # Check if installer exists
    installer_path = Path("OpenVR-InputEmulator-v1.3.exe")
    if not installer_path.exists():
        print("ERROR: OpenVR-InputEmulator-v1.3.exe not found!")
        print("Please download it first.")
        return False

    # Install InputEmulator
    print("\n1. Installing OpenVR InputEmulator...")
    print("   (This will open an installer window - please complete the installation)")

    try:
        subprocess.run([str(installer_path)], check=True)
    except Exception as e:
        print(f"   ERROR: Installation failed: {e}")
        return False

    print("   Installation complete!")

    # Find SteamVR
    print("\n2. Locating SteamVR installation...")
    steamvr_path = find_steam_vr()

    if not steamvr_path:
        print("   ERROR: Could not find SteamVR installation!")
        print("   Please locate it manually.")
        return False

    print(f"   Found: {steamvr_path}")

    # Find InputEmulator driver DLL
    print("\n3. Locating InputEmulator driver DLL...")
    dll_path = Path(steamvr_path) / "drivers" / "00vrinputemulator" / "bin" / "win64" / "driver_00vrinputemulator.dll"

    if not dll_path.exists():
        print(f"   ERROR: Driver DLL not found at: {dll_path}")
        return False

    print(f"   Found: {dll_path}")

    # Copy to our driver directory
    print("\n4. Copying driver to application...")
    dest_dir = Path("drivers") / "virtual_controller" / "bin" / "win64"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / "driver_virtual_controller.dll"

    try:
        shutil.copy2(dll_path, dest_path)
        print(f"   Copied to: {dest_path}")
    except Exception as e:
        print(f"   ERROR: Failed to copy: {e}")
        return False

    print("\n" + "=" * 50)
    print("SUCCESS! Virtual controller driver is ready!")
    print("\nYou can now:")
    print("1. Run the main application")
    print("2. Enable virtual controllers in the UI")
    print("3. Set your desired controller count")
    print("4. Enable headless mode")

    return True


if __name__ == "__main__":
    try:
        success = extract_driver()
        if not success:
            print("\nExtraction failed. Please follow the manual instructions in")
            print("VIRTUAL_CONTROLLERS_SETUP.md")
            input("\nPress Enter to exit...")
            exit(1)
        else:
            input("\nPress Enter to exit...")
            exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        input("\nPress Enter to exit...")
        exit(1)
