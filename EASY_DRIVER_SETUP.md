# Easy Driver Setup

I've downloaded the OpenVR InputEmulator installer for you. Here's how to set it up:

## Quick Method (Automated)

Run this script to automatically extract and install the driver:

```bash
python extract_driver.py
```

The script will:
1. Run the OpenVR InputEmulator installer (you'll need to click through it)
2. Find your SteamVR installation
3. Copy the driver DLL to the correct location for this app
4. Set everything up automatically

## Manual Method

If the automated script doesn't work, follow these steps:

### Step 1: Install OpenVR InputEmulator

1. Run `OpenVR-InputEmulator-v1.3.exe` (already downloaded in this folder)
2. Follow the installation wizard
3. Complete the installation

### Step 2: Locate the Driver DLL

After installation, find the driver at:
```
C:\Program Files (x86)\Steam\steamapps\common\SteamVR\drivers\00vrinputemulator\bin\win64\driver_00vrinputemulator.dll
```

(Adjust the Steam path if you installed Steam in a different location)

### Step 3: Copy to Application

Copy the DLL and rename it:
- **From**: `driver_00vrinputemulator.dll`
- **To**: `drivers\virtual_controller\bin\win64\driver_virtual_controller.dll`

### Step 4: Done!

You're all set! Now you can:
1. Launch the SteamVR Headless Toggle application
2. Check "Enable virtual controllers with headless mode"
3. Set your desired controller count (2 recommended)
4. Click "ENABLE HEADLESS MODE"

## Troubleshooting

**Can't find the DLL?**
- Make sure OpenVR InputEmulator installed successfully
- Check your Steam installation path
- Look in SteamVR/drivers/00vrinputemulator/bin/win64/

**Installation fails?**
- Run the installer as administrator
- Make sure SteamVR is closed during installation
- Temporarily disable antivirus if it blocks the installer

**Still having issues?**
- See VIRTUAL_CONTROLLERS_SETUP.md for alternative drivers
- Check the drivers/virtual_controller/README.md for more options

## What's Been Downloaded

- **OpenVR-InputEmulator-v1.3.exe** (5.6 MB)
  - Official release from: https://github.com/matzman666/OpenVR-InputEmulator
  - Version: 1.3 (Latest stable release)
  - Compatible with modern SteamVR versions

This is the most reliable and feature-rich virtual controller driver available.
