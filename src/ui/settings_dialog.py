import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

from src.core.config_manager import ConfigManager
from src.core.path_detector import PathDetector
from src.utils.validators import FileValidator
from src.ui.styles import Colors, Fonts, Dimensions, Texts


class SettingsDialog(ctk.CTkToplevel):
    """Settings dialog for configuring file paths."""

    def __init__(self, parent, config_manager: ConfigManager):
        """Initialize the settings dialog.

        Args:
            parent: Parent window
            config_manager: ConfigManager instance
        """
        super().__init__(parent)

        self.config_manager = config_manager

        # Setup window
        self.setup_window()

        # Create UI
        self.setup_ui()

        # Load current paths
        self.load_current_paths()

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

    def setup_window(self):
        """Configure the dialog window."""
        self.title(Texts.SETTINGS_TITLE)
        self.geometry(f"{Dimensions.SETTINGS_WIDTH}x{Dimensions.SETTINGS_HEIGHT}")
        self.resizable(False, False)

        # Center on parent
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()

        x = parent_x + (parent_width - Dimensions.SETTINGS_WIDTH) // 2
        y = parent_y + (parent_height - Dimensions.SETTINGS_HEIGHT) // 2

        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        """Create the user interface."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        main_frame.pack(fill="both", expand=True, padx=Dimensions.PADDING, pady=Dimensions.PADDING)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Steam Directory Paths",
            font=(Fonts.FAMILY, Fonts.SIZE_TITLE, "bold"),
            text_color=Colors.TEXT
        )
        title_label.pack(pady=(0, 20))

        # Null driver file section
        null_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        null_frame.pack(fill="x", pady=(0, 15))

        null_label = ctk.CTkLabel(
            null_frame,
            text=Texts.NULL_DRIVER_LABEL,
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL),
            text_color=Colors.TEXT,
            anchor="w"
        )
        null_label.pack(fill="x", pady=(0, 5))

        null_path_frame = ctk.CTkFrame(null_frame, fg_color="transparent")
        null_path_frame.pack(fill="x")

        self.null_driver_entry = ctk.CTkEntry(
            null_path_frame,
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL),
            placeholder_text="Path to null driver default.vrsettings"
        )
        self.null_driver_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        null_browse_button = ctk.CTkButton(
            null_path_frame,
            text=Texts.BROWSE,
            width=80,
            command=lambda: self.browse_file("null_driver"),
            fg_color=Colors.WIDGET_BG,
            hover_color=Colors.BUTTON_HOVER
        )
        null_browse_button.pack(side="right")

        # Validation status for null driver
        self.null_status_label = ctk.CTkLabel(
            null_frame,
            text="",
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL - 1),
            text_color=Colors.TEXT_SECONDARY
        )
        self.null_status_label.pack(fill="x", pady=(5, 0))

        # SteamVR config file section
        steamvr_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        steamvr_frame.pack(fill="x", pady=(0, 15))

        steamvr_label = ctk.CTkLabel(
            steamvr_frame,
            text=Texts.STEAMVR_CONFIG_LABEL,
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL),
            text_color=Colors.TEXT,
            anchor="w"
        )
        steamvr_label.pack(fill="x", pady=(0, 5))

        steamvr_path_frame = ctk.CTkFrame(steamvr_frame, fg_color="transparent")
        steamvr_path_frame.pack(fill="x")

        self.steamvr_config_entry = ctk.CTkEntry(
            steamvr_path_frame,
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL),
            placeholder_text="Path to SteamVR default.vrsettings"
        )
        self.steamvr_config_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        steamvr_browse_button = ctk.CTkButton(
            steamvr_path_frame,
            text=Texts.BROWSE,
            width=80,
            command=lambda: self.browse_file("steamvr_config"),
            fg_color=Colors.WIDGET_BG,
            hover_color=Colors.BUTTON_HOVER
        )
        steamvr_browse_button.pack(side="right")

        # Validation status for SteamVR config
        self.steamvr_status_label = ctk.CTkLabel(
            steamvr_frame,
            text="",
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL - 1),
            text_color=Colors.TEXT_SECONDARY
        )
        self.steamvr_status_label.pack(fill="x", pady=(5, 0))

        # Auto-detect button
        auto_detect_button = ctk.CTkButton(
            main_frame,
            text=Texts.AUTO_DETECT,
            command=self.auto_detect_paths,
            fg_color=Colors.ACCENT,
            hover_color=Colors.BUTTON_HOVER
        )
        auto_detect_button.pack(fill="x", pady=(0, 20))

        # Overall status label
        self.overall_status_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL),
            text_color=Colors.TEXT_SECONDARY
        )
        self.overall_status_label.pack(pady=(0, 20))

        # Button frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", side="bottom")

        cancel_button = ctk.CTkButton(
            button_frame,
            text=Texts.CANCEL,
            command=self.cancel,
            fg_color=Colors.WIDGET_BG,
            hover_color=Colors.BUTTON_HOVER,
            width=100
        )
        cancel_button.pack(side="right", padx=(10, 0))

        save_button = ctk.CTkButton(
            button_frame,
            text=Texts.SAVE,
            command=self.save_settings,
            fg_color=Colors.ACCENT,
            hover_color=Colors.BUTTON_HOVER,
            width=100
        )
        save_button.pack(side="right")

    def load_current_paths(self):
        """Load current paths from config."""
        null_driver = self.config_manager.get_null_driver_path()
        steamvr_config = self.config_manager.get_steamvr_config_path()

        if null_driver:
            self.null_driver_entry.insert(0, null_driver)
        if steamvr_config:
            self.steamvr_config_entry.insert(0, steamvr_config)

        self.validate_paths()

    def browse_file(self, field_name: str):
        """Browse for a file.

        Args:
            field_name: Name of the field ('null_driver' or 'steamvr_config')
        """
        initial_dir = "C:\\Program Files (x86)\\Steam"
        if not os.path.exists(initial_dir):
            initial_dir = "C:\\"

        filename = filedialog.askopenfilename(
            parent=self,
            title="Select VR Settings File",
            initialdir=initial_dir,
            filetypes=[("VR Settings", "*.vrsettings"), ("All Files", "*.*")]
        )

        if filename:
            if field_name == "null_driver":
                self.null_driver_entry.delete(0, "end")
                self.null_driver_entry.insert(0, filename)
            elif field_name == "steamvr_config":
                self.steamvr_config_entry.delete(0, "end")
                self.steamvr_config_entry.insert(0, filename)

            self.validate_paths()

    def auto_detect_paths(self):
        """Auto-detect file paths."""
        detected = PathDetector.auto_detect_all_paths()

        if detected['null_driver']:
            self.null_driver_entry.delete(0, "end")
            self.null_driver_entry.insert(0, detected['null_driver'])

        if detected['steamvr_config']:
            self.steamvr_config_entry.delete(0, "end")
            self.steamvr_config_entry.insert(0, detected['steamvr_config'])

        if detected['null_driver'] and detected['steamvr_config']:
            self.overall_status_label.configure(
                text="✓ Both files detected successfully!",
                text_color=Colors.SUCCESS
            )
        elif detected['steam_dir']:
            self.overall_status_label.configure(
                text="⚠ Steam found but VR files not detected",
                text_color=Colors.WARNING
            )
        else:
            self.overall_status_label.configure(
                text="✗ Steam installation not found",
                text_color=Colors.ERROR
            )

        self.validate_paths()

    def validate_paths(self):
        """Validate entered paths and update status labels."""
        null_driver_path = self.null_driver_entry.get()
        steamvr_config_path = self.steamvr_config_entry.get()

        # Validate null driver
        if null_driver_path:
            valid, error = FileValidator.validate_null_driver_file(null_driver_path)
            if valid:
                self.null_status_label.configure(
                    text="✓ Valid file",
                    text_color=Colors.SUCCESS
                )
            else:
                self.null_status_label.configure(
                    text=f"✗ {error}",
                    text_color=Colors.ERROR
                )
        else:
            self.null_status_label.configure(text="", text_color=Colors.TEXT_SECONDARY)

        # Validate SteamVR config
        if steamvr_config_path:
            valid, error = FileValidator.validate_steamvr_config_file(steamvr_config_path)
            if valid:
                self.steamvr_status_label.configure(
                    text="✓ Valid file",
                    text_color=Colors.SUCCESS
                )
            else:
                self.steamvr_status_label.configure(
                    text=f"✗ {error}",
                    text_color=Colors.ERROR
                )
        else:
            self.steamvr_status_label.configure(text="", text_color=Colors.TEXT_SECONDARY)

        # Overall validation
        if null_driver_path and steamvr_config_path:
            both_valid, _ = FileValidator.validate_both_files(null_driver_path, steamvr_config_path)
            if both_valid:
                self.overall_status_label.configure(
                    text="Status: ✓ Both files valid",
                    text_color=Colors.SUCCESS
                )
                return True
            else:
                self.overall_status_label.configure(
                    text="Status: ✗ Please fix errors above",
                    text_color=Colors.ERROR
                )
                return False
        else:
            self.overall_status_label.configure(
                text="Status: Please configure both paths",
                text_color=Colors.TEXT_SECONDARY
            )
            return False

    def save_settings(self):
        """Save settings and close dialog."""
        null_driver_path = self.null_driver_entry.get()
        steamvr_config_path = self.steamvr_config_entry.get()

        if not null_driver_path or not steamvr_config_path:
            messagebox.showerror("Error", "Please configure both file paths.")
            return

        # Validate both paths
        if not self.validate_paths():
            messagebox.showerror("Error", Texts.PATHS_INVALID)
            return

        # Save to config
        self.config_manager.set_file_paths(null_driver_path, steamvr_config_path)
        success = self.config_manager.save_config()

        if success:
            messagebox.showinfo("Success", Texts.PATHS_SAVED)
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save configuration.")

    def cancel(self):
        """Cancel and close dialog."""
        self.destroy()
