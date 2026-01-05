# Virtual Controller Driver

This folder contains the virtual controller driver for SteamVR headless mode.

## Setup Instructions

To use virtual controllers with this application, you need to obtain a compatible OpenVR controller driver DLL. Here are your options:

### Option 1: Use OpenVR-InputEmulator-Fixed (Recommended)

1. Download the latest release from: https://github.com/averinoing/OpenVR-InputEmulator-Fixed/releases
2. Extract the downloaded archive
3. Copy `driver_00vrinputemulator.dll` from the release to:
   ```
   drivers/virtual_controller/bin/win64/driver_virtual_controller.dll
   ```

### Option 2: Build VirtualControllerDriver

1. Clone the repository: https://github.com/SecondReality/VirtualControllerDriver
2. Build the project using Visual Studio
3. Copy the compiled `driver_virtualcontroller.dll` to:
   ```
   drivers/virtual_controller/bin/win64/driver_virtual_controller.dll
   ```

### Option 3: Build a Custom Driver

Follow the OpenVR driver tutorial to create a custom controller driver:
- Tutorial: https://github.com/ValveSoftware/openvr/wiki/Driver-Documentation
- Example: https://github.com/terminal29/Simple-OpenVR-Driver-Tutorial

## Directory Structure

```
virtual_controller/
├── driver.vrdrivermanifest    # Driver manifest file
├── bin/
│   └── win64/
│       └── driver_virtual_controller.dll  # PUT THE DRIVER DLL HERE
└── resources/
    └── settings/
        └── default.vrsettings  # Driver configuration (managed by the app)
```

## How It Works

1. When you enable headless mode with virtual controllers, the application:
   - Copies this driver folder to SteamVR's `drivers/` directory
   - Configures the number of controllers in `default.vrsettings`
   - SteamVR loads the driver on next restart

2. When you disable headless mode:
   - The controller count is set to 0, disabling the controllers
   - The driver remains installed but inactive

## Configuration

The application manages the `default.vrsettings` file automatically. Key settings:

- `enable`: Whether the driver is enabled
- `controller_count`: Number of controllers to spawn (0-4)
- `controller_N_role`: Role of each controller (left, right, tracker)
- `position_x/y/z`: Default spawn position for controllers

## Troubleshooting

### No DLL Found
If you see errors about missing DLL files, make sure you've placed a valid driver DLL at:
```
drivers/virtual_controller/bin/win64/driver_virtual_controller.dll
```

### Controllers Not Appearing
1. Restart SteamVR after enabling virtual controllers
2. Check SteamVR settings to ensure the driver is loaded
3. Check SteamVR logs at: `%LOCALAPPDATA%\openvr\vrserver.txt`

### Permission Errors
The application needs admin privileges to copy drivers to the SteamVR directory. Make sure to allow elevation when prompted.

## Notes

- This driver is separate from the null driver used for headless HMD mode
- The null driver provides the virtual headset
- This driver provides virtual controllers
- Both work together to create a complete headless VR environment
