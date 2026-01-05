# Virtual Controllers Setup Guide

This guide will help you set up virtual VR controllers for use with the SteamVR Headless Toggle application.

## What You Need

1. The SteamVR Headless Toggle application (this app)
2. A compatible virtual controller driver DLL
3. SteamVR installed on your system

## Quick Setup (5 Minutes)

### Step 1: Download a Virtual Controller Driver

**Option A: OpenVR-InputEmulator-Fixed (Recommended)**

1. Go to: https://github.com/averinoing/OpenVR-InputEmulator-Fixed/releases
2. Download the latest release (e.g., `OpenVR-InputEmulator-Fixed-v1.x.x.zip`)
3. Extract the ZIP file
4. Navigate to the extracted folder and find `driver_00vrinputemulator.dll` (usually in the `bin/win64/` folder)

**Option B: Build VirtualControllerDriver**

1. Clone: https://github.com/SecondReality/VirtualControllerDriver
2. Open the solution in Visual Studio
3. Build the project for x64 Release
4. Find the compiled `driver_virtualcontroller.dll` in the build output

### Step 2: Install the Driver to the Application

1. Locate your SteamVR Headless Toggle installation folder
2. Navigate to: `drivers/virtual_controller/bin/win64/`
3. Copy the driver DLL and rename it to: `driver_virtual_controller.dll`
4. Your final path should be:
   ```
   [App Folder]/drivers/virtual_controller/bin/win64/driver_virtual_controller.dll
   ```

### Step 3: Enable Virtual Controllers

1. Launch the SteamVR Headless Toggle application
2. You should see a "Virtual Controllers" section in the main window
3. Check the box: "Enable virtual controllers with headless mode"
4. Use the slider to select how many controllers you want (0-4)
   - **2 controllers** = Left and right hand controllers (recommended)
   - **1 controller** = Single controller
   - **3-4 controllers** = Additional trackers

### Step 4: Test It Out

1. Click "ENABLE HEADLESS MODE" in the main window
2. The app will:
   - Enable the null driver for headless HMD
   - Install and configure the virtual controller driver
   - Set up the specified number of controllers
3. Launch SteamVR
4. You should see:
   - A virtual headset in SteamVR
   - Virtual controllers appear in the SteamVR status window
   - The controllers may be visible in VR applications

### Step 5: Using the Controllers

The virtual controllers will:
- Appear as tracked devices in SteamVR
- Be recognized by VR applications
- Have static positions (they don't move by default)
- Work with applications that require controller presence

## Advanced Configuration

### Controller Roles

By default, controllers are assigned these roles:
- Controller 0: Left hand
- Controller 1: Right hand
- Controller 2-3: Trackers

You can modify these in: `drivers/virtual_controller/resources/settings/default.vrsettings`

### Driver Settings

The driver configuration file is at:
```
drivers/virtual_controller/resources/settings/default.vrsettings
```

Key settings:
```json
{
  "driver_virtual_controller": {
    "enable": true,
    "controller_count": 2,
    "controller_0_role": "left",
    "controller_1_role": "right",
    "position_x": 0.0,
    "position_y": 1.0,
    "position_z": -0.5
  }
}
```

**Note**: The application manages these settings automatically, but you can manually edit them if needed.

### Controller Positions

The default spawn position is:
- X: 0.0 (center)
- Y: 1.0 (1 meter up)
- Z: -0.5 (0.5 meters forward)

To change positions, edit the driver config file (changes will be overwritten when the app reconfigures the driver).

## Troubleshooting

### Controllers Not Appearing in SteamVR

**Check 1: Driver DLL is Present**
```
[App Folder]/drivers/virtual_controller/bin/win64/driver_virtual_controller.dll
```
This file must exist and be a valid OpenVR driver.

**Check 2: SteamVR Restart**
After enabling headless mode with controllers:
1. Close SteamVR completely
2. Wait 5 seconds
3. Launch SteamVR again
4. Check SteamVR status window for devices

**Check 3: Application Settings**
1. Open the app settings (gear icon)
2. Verify SteamVR paths are detected correctly
3. Make sure "Enable virtual controllers" is checked

**Check 4: SteamVR Logs**
Check for errors in:
```
%LOCALAPPDATA%\openvr\vrserver.txt
```

Look for lines containing:
- `virtual_controller`
- `driver` load errors
- Controller registration messages

### Driver Compatibility Issues

**Error: "DLL could not be loaded"**
- Make sure you're using a 64-bit driver DLL
- Try a different driver (OpenVR-InputEmulator-Fixed vs VirtualControllerDriver)
- Check that your SteamVR version is compatible

**Error: "Driver failed to initialize"**
- Check SteamVR logs for specific error messages
- Ensure the driver manifest file exists
- Verify file permissions

### Admin Permissions

If you get permission errors:
1. The app will prompt for administrator elevation
2. Click "Yes" to restart with elevated privileges
3. Installing drivers to SteamVR requires admin rights

### Controllers Appear But Don't Work

This is expected behavior for basic virtual controllers:
- They provide presence detection
- They have static positions
- They don't have input emulation (unless using InputEmulator)

For interactive controllers with input:
- Use OpenVR-InputEmulator-Fixed
- Configure input bindings in SteamVR
- Use the InputEmulator client to send button presses

## Uninstalling Virtual Controllers

To stop using virtual controllers:

1. Uncheck "Enable virtual controllers with headless mode" in the app
2. Click "ENABLE HEADLESS MODE" then "DISABLE HEADLESS MODE"
3. The driver will be disabled (set to 0 controllers)

To completely remove:
1. Disable headless mode in the app
2. Navigate to: `[SteamVR]/drivers/`
3. Delete the `virtual_controller` folder

## Additional Resources

- **OpenVR Driver Documentation**: https://github.com/ValveSoftware/openvr/wiki/Driver-Documentation
- **OpenVR-InputEmulator**: https://github.com/matzman666/OpenVR-InputEmulator
- **OpenVR-InputEmulator-Fixed**: https://github.com/averinoing/OpenVR-InputEmulator-Fixed
- **VirtualControllerDriver**: https://github.com/SecondReality/VirtualControllerDriver
- **SteamVR Settings**: https://developer.valvesoftware.com/wiki/SteamVR/steamvr.vrsettings

## FAQ

**Q: How many controllers should I use?**
A: For most applications, 2 controllers (left and right hand) is recommended.

**Q: Can I use keyboard/mouse to control the virtual controllers?**
A: Only if you use OpenVR-InputEmulator-Fixed, which includes input emulation features.

**Q: Do the controllers move?**
A: By default, no. They have static positions. Advanced drivers like InputEmulator support position updates.

**Q: Will this work with all VR games?**
A: Most games that require controller presence will recognize them. Input interaction depends on the driver and configuration.

**Q: Can I use this with a real VR headset?**
A: This is designed for headless mode. If you have a real headset, you should use real controllers.

**Q: How do I update the driver?**
A: Download a new driver DLL and replace the existing one in `drivers/virtual_controller/bin/win64/`

## Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review SteamVR logs
3. Ensure you're using a compatible driver version
4. Report issues on the GitHub repository
