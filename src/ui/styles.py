"""UI styling constants for dark mode theme."""


class Colors:
    """Color constants for dark mode theme."""

    # Background colors
    BACKGROUND = "#1e1e1e"  # Dark gray
    WIDGET_BG = "#2d2d2d"  # Slightly lighter gray
    BUTTON_BG = "#2d2d2d"  # Button background
    BUTTON_HOVER = "#3d3d3d"  # Button hover state

    # Text colors
    TEXT = "#ffffff"  # White
    TEXT_SECONDARY = "#cccccc"  # Light gray

    # Accent colors
    ACCENT = "#0078d4"  # Blue
    SUCCESS = "#00cc66"  # Green
    WARNING = "#ffcc00"  # Yellow
    ERROR = "#ff3333"  # Red

    # Status indicator colors
    STATUS_READY = "#00cc66"  # Green - ready to use
    STATUS_WARNING = "#ffcc00"  # Yellow - issues detected
    STATUS_ERROR = "#ff3333"  # Red - not ready
    STATUS_DISABLED = "#666666"  # Gray - disabled


class Fonts:
    """Font constants."""

    FAMILY = "Segoe UI"
    SIZE_NORMAL = 12
    SIZE_LARGE = 14
    SIZE_TITLE = 16
    SIZE_BUTTON = 13


class Dimensions:
    """Dimension constants."""

    # Main window
    MAIN_WINDOW_WIDTH = 360
    MAIN_WINDOW_HEIGHT = 420

    # Settings dialog
    SETTINGS_WIDTH = 550
    SETTINGS_HEIGHT = 450

    # Padding and spacing
    PADDING = 15
    SPACING = 10

    # Button sizes
    BUTTON_HEIGHT = 45
    SMALL_BUTTON_SIZE = 30
    ICON_BUTTON_SIZE = 25

    # Borders
    BORDER_WIDTH = 2
    CORNER_RADIUS = 6


class Texts:
    """Text constants."""

    # Window titles
    MAIN_TITLE = "Steam VR Headless Toggle"
    SETTINGS_TITLE = "Settings"

    # Button labels
    ENABLE_VR = "ENABLE HEADLESS MODE"
    DISABLE_VR = "DISABLE HEADLESS MODE"
    SETTINGS = "⚙"
    BROWSE = "Browse"
    SAVE = "Save"
    CANCEL = "Cancel"
    AUTO_DETECT = "Auto-Detect Paths"

    # Status messages
    FILES_DETECTED = "Files: ✓ Detected"
    FILES_NOT_FOUND = "Files: ✗ Not Found"
    FILES_INVALID = "Files: ⚠ Invalid"

    # State labels
    STATE_LABEL = "Status:"
    STATE_ENABLED = "ENABLED"
    STATE_DISABLED = "DISABLED"
    STATE_ERROR = "ERROR"
    STATE_UNKNOWN = "UNKNOWN"

    # Settings labels
    NULL_DRIVER_LABEL = "Null Driver File:"
    STEAMVR_CONFIG_LABEL = "SteamVR Config File:"

    # Messages
    ADMIN_REQUIRED = "Administrator rights required to modify files.\nRestart with elevation?"
    TOGGLE_SUCCESS = "VR mode toggled successfully!"
    TOGGLE_FAILED = "Failed to toggle VR mode"
    PATHS_SAVED = "Paths saved successfully!"
    PATHS_INVALID = "Invalid file paths. Please check and try again."
