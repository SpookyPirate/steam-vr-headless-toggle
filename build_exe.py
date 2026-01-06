"""
Build script for creating standalone executable using PyInstaller.

Usage:
    python build_exe.py
"""

import PyInstaller.__main__
import os
import sys


def build():
    """Build the executable."""

    # Get the absolute path to the project
    project_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_dir, 'src')
    main_script = os.path.join(src_dir, 'main.py')

    # Icon path
    icon_path = os.path.join(project_dir, 'ui-photos', 'steamvr-headless-toggle-icon.ico')

    # Driver folder path
    drivers_dir = os.path.join(project_dir, 'drivers')

    print("Building SteamVR Headless Toggle executable...")
    print(f"Project directory: {project_dir}")
    print(f"Main script: {main_script}")

    # PyInstaller arguments
    args = [
        main_script,
        '--name=SteamVR-Headless-Toggle',
        '--onefile',
        '--windowed',  # No console window
        '--clean',
        '--noconfirm',
        f'--distpath={os.path.join(project_dir, "dist")}',
        f'--workpath={os.path.join(project_dir, "build")}',
        f'--specpath={project_dir}',
    ]

    # Add icon if it exists
    if os.path.exists(icon_path):
        args.append(f'--icon={icon_path}')
        print(f"Using icon: {icon_path}")
    else:
        print("Warning: Icon not found, using default")

    # Add data files - bundle the virtual controller driver
    if os.path.exists(drivers_dir):
        args.append(f'--add-data={drivers_dir};drivers')
        print(f"Bundling drivers folder: {drivers_dir}")
    else:
        print("Warning: Drivers folder not found")

    # Add icon for runtime loading
    if os.path.exists(icon_path):
        args.append(f'--add-data={icon_path};ui-photos')
        print(f"Bundling icon: {icon_path}")

    # Run PyInstaller
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "="*50)
        print("Build completed successfully!")
        print(f"Executable location: {os.path.join(project_dir, 'dist', 'SteamVR-Headless-Toggle.exe')}")
        print("="*50)
    except Exception as e:
        print(f"\nError during build: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build()
