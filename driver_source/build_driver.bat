@echo off
echo ========================================
echo Virtual Controller Driver Build Script
echo ========================================
echo.

REM Check if OpenVR SDK exists
if not exist "openvr\headers\openvr_driver.h" (
    echo ERROR: OpenVR SDK not found!
    echo.
    echo Please download OpenVR SDK from:
    echo https://github.com/ValveSoftware/openvr/releases
    echo.
    echo Extract it to: driver_source\openvr\
    echo.
    pause
    exit /b 1
)

echo OpenVR SDK found!
echo.

REM Create build directory
if not exist "build" mkdir build
cd build

echo Running CMake...
cmake .. -G "Visual Studio 16 2019" -A x64
if errorlevel 1 (
    echo.
    echo ERROR: CMake failed!
    echo Make sure you have Visual Studio 2019 or later installed.
    echo.
    pause
    exit /b 1
)

echo.
echo Building driver (Release mode)...
cmake --build . --config Release
if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo.
echo Driver DLL is at:
echo build\bin\Release\driver_virtualcontroller.dll
echo.
echo Next step:
echo Copy the DLL to:
echo ..\drivers\virtual_controller\bin\win64\driver_virtual_controller.dll
echo.

REM Offer to copy automatically
set /p COPY="Copy DLL automatically? (y/n): "
if /i "%COPY%"=="y" (
    if not exist "..\drivers\virtual_controller\bin\win64" mkdir "..\drivers\virtual_controller\bin\win64"
    copy "bin\Release\driver_virtualcontroller.dll" "..\drivers\virtual_controller\bin\win64\driver_virtual_controller.dll"
    echo.
    echo DLL copied successfully!
    echo You can now use the app to install virtual controllers.
)

echo.
pause
