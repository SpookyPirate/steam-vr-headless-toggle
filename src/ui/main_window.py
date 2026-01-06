import customtkinter as ctk
from tkinter import messagebox
import sys

from src.core.state_manager import StateManager, ToggleState
from src.core.config_manager import ConfigManager
from src.core.controller_manager import ControllerManager
from src.core.path_detector import PathDetector
from src.utils.validators import FileValidator
from src.utils.admin_utils import is_admin, needs_admin_for_files, request_admin_elevation
from src.ui.styles import Colors, Fonts, Dimensions, Texts
from pathlib import Path
import threading


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Initialize managers
        self.config_manager = ConfigManager()
        self.state_manager = None
        self.controller_manager = None

        # Setup window
        self.setup_window()

        # Initialize file paths
        self.init_file_paths()

        # Create UI
        self.setup_ui()

        # Initial status update
        self.update_status()

    def setup_window(self):
        """Configure the main window."""
        self.title(Texts.MAIN_TITLE)
        self.geometry(f"{Dimensions.MAIN_WINDOW_WIDTH}x{Dimensions.MAIN_WINDOW_HEIGHT}")
        self.resizable(False, False)

        # Set window icon
        try:
            icon_path = Path(__file__).parent.parent.parent / "ui-photos" / "steamvr-headless-toggle-icon.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Center window on screen
        self.center_window()

    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def init_file_paths(self):
        """Initialize and validate file paths."""
        null_driver = self.config_manager.get_null_driver_path()
        steamvr_config = self.config_manager.get_steamvr_config_path()
        steamvr_root = self.config_manager.get_steamvr_root_path()

        # Auto-detect if paths are not set
        if not null_driver or not steamvr_config:
            detected = PathDetector.auto_detect_all_paths()
            if detected['null_driver'] and detected['steamvr_config']:
                null_driver = detected['null_driver']
                steamvr_config = detected['steamvr_config']
                self.config_manager.set_file_paths(null_driver, steamvr_config)
                self.config_manager.save_config()

        # Derive SteamVR root from config path if not already set
        if not steamvr_root and steamvr_config:
            steamvr_root = str(Path(steamvr_config).parent.parent.parent)
            self.config_manager.set_steamvr_root_path(steamvr_root)
            self.config_manager.save_config()

        # Initialize controller manager if SteamVR root is available
        if steamvr_root:
            self.controller_manager = ControllerManager(steamvr_root)

        # Initialize state manager if paths are valid
        if null_driver and steamvr_config:
            backup_dir = self.config_manager.get_backup_directory()
            enable_controllers = self.config_manager.are_virtual_controllers_enabled()
            controller_count = self.config_manager.get_controller_count()

            self.state_manager = StateManager(
                null_driver,
                steamvr_config,
                backup_dir,
                controller_manager=self.controller_manager,
                enable_controllers=enable_controllers and self.config_manager.should_auto_enable_controllers(),
                controller_count=controller_count
            )

    def setup_ui(self):
        """Create the user interface."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        main_frame.pack(fill="both", expand=True, padx=Dimensions.PADDING, pady=Dimensions.PADDING)

        # Status label (larger heading)
        status_title_label = ctk.CTkLabel(
            main_frame,
            text=Texts.STATE_LABEL,
            font=(Fonts.FAMILY, Fonts.SIZE_TITLE, "bold"),
            text_color=Colors.TEXT
        )
        status_title_label.pack(pady=(0, 5))

        # Status indicator (colored text without dot)
        self.status_label = ctk.CTkLabel(
            main_frame,
            text=Texts.STATE_DISABLED,
            font=(Fonts.FAMILY, Fonts.SIZE_LARGE + 2, "bold"),
            text_color=Colors.ERROR
        )
        self.status_label.pack(pady=(0, 5))

        # Files detected label
        self.files_label = ctk.CTkLabel(
            main_frame,
            text=Texts.FILES_NOT_FOUND,
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL),
            text_color=Colors.TEXT_SECONDARY
        )
        self.files_label.pack(pady=(0, 20))

        # Toggle button with padding
        self.toggle_button = ctk.CTkButton(
            main_frame,
            text=Texts.ENABLE_VR,
            font=(Fonts.FAMILY, Fonts.SIZE_BUTTON, "bold"),
            height=Dimensions.BUTTON_HEIGHT,
            command=self.on_toggle_clicked,
            fg_color=Colors.ACCENT,
            hover_color=Colors.BUTTON_HOVER
        )
        self.toggle_button.pack(fill="x", padx=15, pady=(0, 15))

        # Virtual Controllers section
        controllers_frame = ctk.CTkFrame(main_frame, fg_color=Colors.WIDGET_BG, corner_radius=10)
        controllers_frame.pack(fill="x", padx=15, pady=(0, 0))

        # Controllers header
        controllers_header = ctk.CTkLabel(
            controllers_frame,
            text="Virtual Controllers",
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL, "bold"),
            text_color=Colors.TEXT
        )
        controllers_header.pack(pady=(10, 5), padx=10, anchor="w")

        # Enable controllers checkbox
        self.controllers_enabled_var = ctk.BooleanVar(value=self.config_manager.are_virtual_controllers_enabled())
        self.controllers_checkbox = ctk.CTkCheckBox(
            controllers_frame,
            text="Enable virtual controllers with headless mode",
            variable=self.controllers_enabled_var,
            command=self.on_controllers_toggle,
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL - 1),
            text_color=Colors.TEXT_SECONDARY
        )
        self.controllers_checkbox.pack(pady=(0, 10), padx=10, anchor="w")

        # Controller count controls
        count_frame = ctk.CTkFrame(controllers_frame, fg_color="transparent")
        count_frame.pack(fill="x", padx=10, pady=(0, 10))

        count_label = ctk.CTkLabel(
            count_frame,
            text="Controller Count:",
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL - 1),
            text_color=Colors.TEXT_SECONDARY
        )
        count_label.pack(side="left", padx=(0, 10))

        self.controller_count_var = ctk.IntVar(value=self.config_manager.get_controller_count())
        self.controller_count_label = ctk.CTkLabel(
            count_frame,
            text=str(self.controller_count_var.get()),
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL, "bold"),
            text_color=Colors.ACCENT,
            width=30
        )
        self.controller_count_label.pack(side="right")

        self.controller_slider = ctk.CTkSlider(
            count_frame,
            from_=0,
            to=4,
            number_of_steps=4,
            variable=self.controller_count_var,
            command=self.on_controller_count_changed
        )
        self.controller_slider.pack(side="right", fill="x", expand=True, padx=(0, 10))

        # Settings button (bottom right)
        settings_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        settings_frame.pack(fill="x", side="bottom")

        self.settings_button = ctk.CTkButton(
            settings_frame,
            text=Texts.SETTINGS,
            font=(Fonts.FAMILY, 16),
            width=Dimensions.ICON_BUTTON_SIZE,
            height=Dimensions.ICON_BUTTON_SIZE,
            command=self.on_settings_clicked,
            fg_color=Colors.WIDGET_BG,
            hover_color=Colors.BUTTON_HOVER
        )
        self.settings_button.pack(side="right")

    def update_status(self):
        """Update status indicator and button state."""
        if not self.state_manager:
            self.status_label.configure(text=Texts.STATE_ERROR, text_color=Colors.ERROR)
            self.files_label.configure(text=Texts.FILES_NOT_FOUND)
            self.toggle_button.configure(state="disabled")
            return

        # Verify files
        valid, error = self.state_manager.verify_files()

        if not valid:
            self.status_label.configure(text=Texts.STATE_ERROR, text_color=Colors.ERROR)
            self.files_label.configure(text=Texts.FILES_INVALID)
            self.toggle_button.configure(state="disabled")
            return

        # Get current state
        current_state = self.state_manager.get_current_state()

        # Update status label with colored text (no dots)
        if current_state == ToggleState.ENABLED:
            self.status_label.configure(text=Texts.STATE_ENABLED, text_color=Colors.SUCCESS)
            self.toggle_button.configure(text=Texts.DISABLE_VR)
        elif current_state == ToggleState.DISABLED:
            self.status_label.configure(text=Texts.STATE_DISABLED, text_color=Colors.ERROR)
            self.toggle_button.configure(text=Texts.ENABLE_VR)
        elif current_state == ToggleState.UNKNOWN:
            self.status_label.configure(text=Texts.STATE_UNKNOWN, text_color=Colors.WARNING)
            self.toggle_button.configure(text=Texts.ENABLE_VR)
        else:
            self.status_label.configure(text=Texts.STATE_ERROR, text_color=Colors.ERROR)
            self.toggle_button.configure(state="disabled")
            return

        # Update files label
        self.files_label.configure(text=Texts.FILES_DETECTED)
        self.toggle_button.configure(state="normal")

    def on_toggle_clicked(self):
        """Handle toggle button click."""
        if not self.state_manager:
            messagebox.showerror("Error", "Configuration not set. Please configure file paths in settings.")
            self.on_settings_clicked()
            return

        # Check if admin privileges are needed
        files = [self.state_manager.null_driver_path, self.state_manager.steamvr_config_path]
        if needs_admin_for_files(files) and not is_admin():
            response = messagebox.askyesno(
                "Administrator Required",
                Texts.ADMIN_REQUIRED
            )
            if response:
                if request_admin_elevation():
                    sys.exit()
            return

        # Perform toggle
        self.toggle_button.configure(state="disabled")
        self.update()

        success, error, new_state = self.state_manager.toggle()

        if success:
            # Update config with new state
            self.config_manager.set_last_state(new_state.value)
            self.config_manager.save_config()

            # Update UI
            self.update_status()

            # Show success message
            if new_state == ToggleState.ENABLED:
                messagebox.showinfo("Success", "Headless mode enabled successfully!")
            else:
                messagebox.showinfo("Success", "Headless mode disabled successfully!")
        else:
            messagebox.showerror("Error", f"Failed to toggle headless mode:\n\n{error}")
            self.toggle_button.configure(state="normal")
            self.update_status()

    def on_settings_clicked(self):
        """Handle settings button click."""
        from src.ui.settings_dialog import SettingsDialog

        dialog = SettingsDialog(self, self.config_manager)
        dialog.wait_window()

        # Reinitialize after settings change
        self.init_file_paths()
        self.update_status()

    def show_error_dialog(self, message: str):
        """Show error dialog.

        Args:
            message: Error message to display
        """
        messagebox.showerror("Error", message)

    def show_success_dialog(self, message: str):
        """Show success dialog.

        Args:
            message: Success message to display
        """
        messagebox.showinfo("Success", message)

    def on_controllers_toggle(self):
        """Handle virtual controllers checkbox toggle."""
        enabled = self.controllers_enabled_var.get()

        self.config_manager.set_virtual_controllers_enabled(enabled)
        self.config_manager.save_config()

        # Update state manager if it exists
        if self.state_manager:
            self.state_manager.enable_controllers = enabled and self.config_manager.should_auto_enable_controllers()

    def on_controller_count_changed(self, value):
        """Handle controller count slider change.

        Args:
            value: New slider value
        """
        count = int(value)
        self.controller_count_label.configure(text=str(count))
        self.config_manager.set_controller_count(count)
        self.config_manager.save_config()

        # Update state manager if it exists
        if self.state_manager:
            self.state_manager.controller_count = count

