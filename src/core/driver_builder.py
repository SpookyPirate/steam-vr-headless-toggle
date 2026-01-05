"""
Automated Driver Builder
Downloads OpenVR SDK and builds the custom virtual controller driver.
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path
from typing import Tuple, Optional, Callable


class DriverBuilder:
    """Handles automated building of the custom virtual controller driver."""

    OPENVR_SDK_URL = "https://github.com/ValveSoftware/openvr/archive/refs/tags/v1.23.7.zip"
    OPENVR_SDK_VERSION = "1.23.7"

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize DriverBuilder.

        Args:
            project_root: Root directory of the project (defaults to 3 levels up from this file)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.driver_source_path = self.project_root / "driver_source"
        self.openvr_path = self.driver_source_path / "openvr"
        self.build_path = self.driver_source_path / "build"
        self.output_dll_path = self.project_root / "drivers" / "virtual_controller" / "bin" / "win64" / "driver_virtual_controller.dll"

    def check_prerequisites(self) -> Tuple[bool, str]:
        """Check if build prerequisites are available.

        Returns:
            Tuple of (has_prerequisites, missing_info)
        """
        missing = []

        # Check for CMake
        try:
            result = subprocess.run(["cmake", "--version"],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            if result.returncode != 0:
                missing.append("CMake (install from https://cmake.org/download/)")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            missing.append("CMake (install from https://cmake.org/download/)")

        # Check for Visual Studio (try to find MSBuild)
        msbuild_paths = [
            r"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe",
            r"C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe",
            r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe",
            r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe",
        ]

        has_vs = any(Path(p).exists() for p in msbuild_paths)
        if not has_vs:
            missing.append("Visual Studio 2019+ with C++ Desktop Development workload")

        if missing:
            return False, "Missing prerequisites:\n" + "\n".join(f"  - {item}" for item in missing)

        return True, ""

    def download_openvr_sdk(self, progress_callback: Optional[Callable[[int], None]] = None) -> Tuple[bool, str]:
        """Download and extract OpenVR SDK.

        Args:
            progress_callback: Optional callback for download progress (0-100)

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Remove existing OpenVR folder
            if self.openvr_path.exists():
                shutil.rmtree(self.openvr_path)

            # Download OpenVR SDK
            zip_path = self.driver_source_path / f"openvr-{self.OPENVR_SDK_VERSION}.zip"

            def download_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(int((downloaded / total_size) * 100), 100)
                    progress_callback(percent)

            urllib.request.urlretrieve(
                self.OPENVR_SDK_URL,
                zip_path,
                reporthook=download_progress
            )

            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.driver_source_path)

            # Rename extracted folder to "openvr"
            extracted_folder = self.driver_source_path / f"openvr-{self.OPENVR_SDK_VERSION}"
            if extracted_folder.exists():
                extracted_folder.rename(self.openvr_path)

            # Clean up ZIP
            zip_path.unlink()

            # Verify essential files exist
            header_file = self.openvr_path / "headers" / "openvr_driver.h"
            lib_file = self.openvr_path / "lib" / "win64" / "openvr_api.lib"

            if not header_file.exists():
                return False, f"OpenVR headers not found after extraction: {header_file}"

            if not lib_file.exists():
                return False, f"OpenVR library not found after extraction: {lib_file}"

            return True, ""

        except Exception as e:
            return False, f"Failed to download OpenVR SDK: {str(e)}"

    def build_driver(self, progress_callback: Optional[Callable[[str], None]] = None) -> Tuple[bool, str]:
        """Build the virtual controller driver.

        Args:
            progress_callback: Optional callback for build status messages

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Create build directory
            if self.build_path.exists():
                shutil.rmtree(self.build_path)
            self.build_path.mkdir(exist_ok=True)

            # Run CMake configure
            if progress_callback:
                progress_callback("Configuring CMake...")

            cmake_result = subprocess.run(
                ["cmake", "..", "-G", "Visual Studio 16 2019", "-A", "x64"],
                cwd=self.build_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if cmake_result.returncode != 0:
                # Try Visual Studio 2022 if 2019 failed
                cmake_result = subprocess.run(
                    ["cmake", "..", "-G", "Visual Studio 17 2022", "-A", "x64"],
                    cwd=self.build_path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if cmake_result.returncode != 0:
                    return False, f"CMake configuration failed:\n{cmake_result.stderr}"

            # Run CMake build
            if progress_callback:
                progress_callback("Building driver DLL...")

            build_result = subprocess.run(
                ["cmake", "--build", ".", "--config", "Release"],
                cwd=self.build_path,
                capture_output=True,
                text=True,
                timeout=180
            )

            if build_result.returncode != 0:
                return False, f"Build failed:\n{build_result.stderr}"

            # Verify DLL was created
            built_dll = self.build_path / "bin" / "Release" / "driver_virtualcontroller.dll"
            if not built_dll.exists():
                # Try alternate path
                built_dll = self.build_path / "Release" / "driver_virtualcontroller.dll"
                if not built_dll.exists():
                    return False, "Build completed but DLL not found in expected location"

            # Copy DLL to output location
            if progress_callback:
                progress_callback("Copying DLL to driver folder...")

            self.output_dll_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(built_dll, self.output_dll_path)

            # Verify final DLL exists
            if not self.output_dll_path.exists():
                return False, "Failed to copy DLL to output location"

            return True, ""

        except subprocess.TimeoutExpired:
            return False, "Build process timed out"
        except Exception as e:
            return False, f"Build failed: {str(e)}"

    def build_full_automated(self,
                           download_progress: Optional[Callable[[int], None]] = None,
                           build_progress: Optional[Callable[[str], None]] = None) -> Tuple[bool, str]:
        """Fully automated build process: check prerequisites, download SDK, build driver.

        Args:
            download_progress: Optional callback for download progress (0-100)
            build_progress: Optional callback for build status messages

        Returns:
            Tuple of (success, error_message)
        """
        # Check prerequisites
        has_prereqs, prereq_error = self.check_prerequisites()
        if not has_prereqs:
            return False, prereq_error

        # Download OpenVR SDK if needed
        if not self.openvr_path.exists():
            if build_progress:
                build_progress("Downloading OpenVR SDK...")

            success, error = self.download_openvr_sdk(download_progress)
            if not success:
                return False, error

        # Build the driver
        success, error = self.build_driver(build_progress)
        if not success:
            return False, error

        return True, ""

    def is_driver_built(self) -> bool:
        """Check if the driver DLL has been built.

        Returns:
            bool: True if driver DLL exists
        """
        return self.output_dll_path.exists()
