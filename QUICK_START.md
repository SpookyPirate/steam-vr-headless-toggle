# Quick Start Guide

## For Users (Running the App)

### Option 1: Use Pre-built Executable

1. Download `SteamVR-Headless-Toggle.exe`
2. Double-click to run
3. If files are detected automatically, you're ready to go!
4. Click the big button to toggle VR mode

### Option 2: Run from Source

```bash
# Install Python 3.10 or later first
pip install -r requirements.txt
python src/main.py
```

## For Developers (Building the App)

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd steam-simulated-vr-headset-toggle

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Run in Development Mode

```bash
python src/main.py
```

### Build Standalone Executable

```bash
python build_exe.py
```

The executable will be in the `dist/` folder.

### Testing

1. **First Run Test**:
   - Delete `config/app_config.json` if it exists
   - Run the app
   - Verify auto-detection works
   - Check that settings dialog opens if files aren't found

2. **Toggle Test**:
   - Enable VR mode
   - Check that files are modified correctly
   - Verify backup was created in `backups/` folder
   - Disable VR mode
   - Verify files are restored to original state

3. **Settings Test**:
   - Click settings gear
   - Test "Auto-Detect Paths" button
   - Test "Browse" buttons
   - Verify validation messages

4. **Admin Test**:
   - Run as non-admin user
   - Try to toggle (should prompt for elevation)

## Common Development Tasks

### Add a New Feature

1. Create new module in appropriate directory (`src/core/`, `src/ui/`, `src/utils/`)
2. Import in relevant files
3. Test thoroughly
4. Update README.md

### Modify UI

- Edit `src/ui/main_window.py` for main window
- Edit `src/ui/settings_dialog.py` for settings
- Edit `src/ui/styles.py` for colors/fonts

### Change File Operations

- Edit `src/core/file_manager.py` for JSON operations
- Edit `src/core/state_manager.py` for toggle logic

### Update Configuration

- Edit `src/core/config_manager.py`
- Update `DEFAULT_CONFIG` dictionary

## Project Structure Overview

```
src/
├── main.py              # Start here
├── ui/                  # All GUI code
├── core/                # Business logic
└── utils/               # Helper functions

config/                  # User settings (auto-generated)
backups/                 # Auto-backups (auto-generated)
resources/               # Icons and assets
```

## Tips

- Always test with Steam closed
- Keep backups of your VR settings before testing
- Use virtual environment for development
- The app requires Windows-specific APIs (pywin32)

## Need Help?

- Check README.md for full documentation
- Look at existing code for examples
- File structure is organized by function
