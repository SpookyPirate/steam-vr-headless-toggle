# Building the Virtual Controller Driver

This driver creates simple virtual VR controllers that appear in SteamVR.

## Prerequisites

1. **Visual Studio 2019 or later** (Community Edition is fine)
   - Download: https://visualstudio.microsoft.com/downloads/
   - Install with "Desktop development with C++" workload

2. **CMake** (3.10 or later)
   - Download: https://cmake.org/download/
   - Or install via: `choco install cmake` (if you have Chocolatey)

3. **OpenVR SDK**
   - Download: https://github.com/ValveSoftware/openvr/releases
   - Extract to `driver_source/openvr/`

## Quick Build (Windows)

### Option 1: Using CMake GUI

1. Open CMake GUI
2. Set source directory: `driver_source`
3. Set build directory: `driver_source/build`
4. Click "Configure"
5. Select "Visual Studio 16 2019" (or your version)
6. Click "Generate"
7. Click "Open Project"
8. In Visual Studio, build in Release mode
9. Find DLL in: `driver_source/build/bin/Release/driver_virtualcontroller.dll`

### Option 2: Command Line

```bash
cd driver_source
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

The DLL will be at: `build/bin/Release/driver_virtualcontroller.dll`

## Installation

1. Copy the built DLL:
   ```
   FROM: driver_source/build/bin/Release/driver_virtualcontroller.dll
   TO: drivers/virtual_controller/bin/win64/driver_virtual_controller.dll
   ```

2. The app will automatically install it to SteamVR when you enable controllers

## Troubleshooting

**Error: Cannot find OpenVR headers**
- Make sure OpenVR SDK is extracted to `driver_source/openvr/`
- The path should contain `headers/openvr_driver.h`

**Error: Cannot find openvr_api.lib**
- Check that `driver_source/openvr/lib/win64/openvr_api.lib` exists
- Re-extract the OpenVR SDK if needed

**CMake not found**
- Add CMake to your PATH or use full path to cmake.exe

## Alternative: Download Pre-built

If building is too complex, you can download a pre-built driver:
1. Check releases on the GitHub repository
2. Or use the InputEmulator approach (already installed)
