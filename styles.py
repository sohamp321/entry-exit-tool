"""
Styles for the Hostel Face Authentication System GUI
"""

import tkinter as tk
from tkinter import ttk
import os

class AppStyles:
    """Class to manage application styles"""

    # Colors
    PRIMARY_COLOR = "#3498db"  # Blue
    SECONDARY_COLOR = "#2ecc71"  # Green
    ACCENT_COLOR = "#e74c3c"  # Red
    BG_COLOR = "#f5f5f5"  # Light gray
    TEXT_COLOR = "#2c3e50"  # Dark blue/gray
    LIGHT_TEXT_COLOR = "#7f8c8d"  # Light gray text

    # Fonts
    TITLE_FONT = ("Helvetica", 16, "bold")
    HEADER_FONT = ("Helvetica", 14, "bold")
    NORMAL_FONT = ("Helvetica", 12)
    SMALL_FONT = ("Helvetica", 10)

    # Padding
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 15

    @staticmethod
    def apply_styles(root):
        """Apply styles to the application"""
        style = ttk.Style()

        # Configure the theme based on OS
        try:
            if os.name == 'nt':  # Windows
                style.theme_use('vista')
            else:
                style.theme_use('clam')
        except tk.TclError:
            # Fallback to default theme if the specified theme is not available
            available_themes = style.theme_names()
            if 'clam' in available_themes:
                style.theme_use('clam')
            elif len(available_themes) > 0:
                style.theme_use(available_themes[0])

        # Configure colors
        style.configure(".",
                        background=AppStyles.BG_COLOR,
                        foreground=AppStyles.TEXT_COLOR,
                        font=AppStyles.NORMAL_FONT)

        # Configure frames
        style.configure("TFrame", background=AppStyles.BG_COLOR)

        # Configure labels
        style.configure("TLabel",
                        background=AppStyles.BG_COLOR,
                        foreground=AppStyles.TEXT_COLOR,
                        font=AppStyles.NORMAL_FONT)

        # Configure title labels
        style.configure("Title.TLabel",
                        font=AppStyles.TITLE_FONT,
                        foreground="black")

        # Configure header labels
        style.configure("Header.TLabel",
                        font=AppStyles.HEADER_FONT,
                        foreground=AppStyles.TEXT_COLOR)

        # Configure black title labels
        style.configure("BlackTitle.TLabel",
                        font=AppStyles.TITLE_FONT,
                        foreground="black")

        # Configure buttons - default style with black text for better visibility
        style.configure("TButton",
                        background=AppStyles.BG_COLOR,
                        foreground="black",
                        font=AppStyles.NORMAL_FONT,
                        padding=5)

        # Configure primary buttons - blue with white text
        style.configure("Primary.TButton",
                        background=AppStyles.PRIMARY_COLOR,
                        foreground="white")

        # Configure secondary buttons - green with white text
        style.configure("Secondary.TButton",
                        background=AppStyles.SECONDARY_COLOR,
                        foreground="white")

        # Configure danger buttons - red with white text
        style.configure("Danger.TButton",
                        background=AppStyles.ACCENT_COLOR,
                        foreground="white")

        # Configure entries
        style.configure("TEntry",
                        fieldbackground="white",
                        foreground=AppStyles.TEXT_COLOR,
                        padding=5)

        # Configure treeview
        style.configure("Treeview",
                        background="white",
                        foreground=AppStyles.TEXT_COLOR,
                        rowheight=25,
                        fieldbackground="white")

        style.configure("Treeview.Heading",
                        font=AppStyles.NORMAL_FONT,
                        background=AppStyles.PRIMARY_COLOR,
                        foreground="white")

        # Map states to styles for different button types
        # Default buttons
        style.map("TButton",
                  background=[('active', '#cccccc'), ('pressed', '#999999')],
                  foreground=[('active', 'black'), ('pressed', 'black')])

        # Primary buttons (blue)
        style.map("Primary.TButton",
                  background=[('active', '#2980b9'), ('pressed', '#1c638e')],  # Darker blue when active/pressed
                  foreground=[('active', 'white'), ('pressed', 'white')])

        # Secondary buttons (green)
        style.map("Secondary.TButton",
                  background=[('active', '#27ae60'), ('pressed', '#1e8449')],  # Darker green when active/pressed
                  foreground=[('active', 'white'), ('pressed', 'white')])

        # Danger buttons (red)
        style.map("Danger.TButton",
                  background=[('active', '#c0392b'), ('pressed', '#922b21')],  # Darker red when active/pressed
                  foreground=[('active', 'white'), ('pressed', 'white')])

        style.map("Treeview",
                  background=[('selected', AppStyles.PRIMARY_COLOR)],
                  foreground=[('selected', 'white')])

        # Set root background
        root.configure(background=AppStyles.BG_COLOR)

        return style
