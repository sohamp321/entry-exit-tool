"""
Custom widgets for the Hostel Face Authentication System
"""

import tkinter as tk
from tkinter import ttk

class ColorButton(tk.Button):
    """A button with customizable text and background colors"""
    def __init__(self, master=None, text="", bg="#3498db", fg="black", command=None, **kwargs):
        """Initialize the button with custom colors"""
        super().__init__(
            master, 
            text=text,
            bg=bg,
            fg=fg,
            activebackground=self._darken_color(bg),
            activeforeground=fg,
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5,
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            command=command,
            **kwargs
        )
    
    def _darken_color(self, hex_color):
        """Darken a color for the active state"""
        # Convert hex to RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Darken by 20%
        factor = 0.8
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

class PrimaryButton(ColorButton):
    """Blue button for primary actions"""
    def __init__(self, master=None, text="", command=None, **kwargs):
        super().__init__(master, text=text, bg="#3498db", fg="white", command=command, **kwargs)

class SecondaryButton(ColorButton):
    """Green button for secondary actions"""
    def __init__(self, master=None, text="", command=None, **kwargs):
        super().__init__(master, text=text, bg="#2ecc71", fg="white", command=command, **kwargs)

class DangerButton(ColorButton):
    """Red button for dangerous actions"""
    def __init__(self, master=None, text="", command=None, **kwargs):
        super().__init__(master, text=text, bg="#e74c3c", fg="white", command=command, **kwargs)

class DefaultButton(ColorButton):
    """Gray button with black text for default actions"""
    def __init__(self, master=None, text="", command=None, **kwargs):
        super().__init__(master, text=text, bg="#f0f0f0", fg="black", command=command, **kwargs)
