"""
Voice recognition dialog for displaying real-time speech recognition results.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time

class VoiceRecognitionDialog:
    def __init__(self, parent, title="Voice Recognition"):
        """Initialize the voice recognition dialog"""
        self.parent = parent
        self.title = title
        
        # Create a new top-level window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x300")
        self.dialog.resizable(True, True)
        
        # Make it modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog on the parent window
        self.center_on_parent()
        
        # Create the widgets
        self.create_widgets()
        
        # Variables for tracking recognition
        self.recognition_active = False
        self.recognition_text = ""
        self.final_result = None
        
        # Start with listening animation
        self.start_listening_animation()
    
    def center_on_parent(self):
        """Center the dialog on the parent window"""
        parent = self.parent
        
        # Get parent geometry
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Calculate position
        width = 500
        height = 300
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        # Set geometry
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create the dialog widgets"""
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = ttk.Label(main_frame, text="Listening...", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 20))
        self.title_label = title_label
        
        # Instruction label
        instruction_label = ttk.Label(main_frame, 
                                     text="Please speak clearly into your microphone.",
                                     font=("Helvetica", 12))
        instruction_label.pack(pady=(0, 20))
        
        # Animation frame
        animation_frame = ttk.Frame(main_frame)
        animation_frame.pack(fill=tk.X, pady=10)
        
        # Create animation dots
        self.dots = []
        for i in range(5):
            dot = ttk.Label(animation_frame, text="●", font=("Helvetica", 24))
            dot.pack(side=tk.LEFT, padx=10)
            self.dots.append(dot)
        
        # Recognition text frame with border
        text_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Recognition text display
        self.recognition_label = ttk.Label(text_frame, 
                                          text="Waiting for speech...",
                                          font=("Helvetica", 12),
                                          wraplength=450)
        self.recognition_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Cancel button
        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel)
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def start_listening_animation(self):
        """Start the listening animation"""
        self.recognition_active = True
        self.animate_dots()
    
    def animate_dots(self):
        """Animate the dots to indicate listening"""
        if not self.recognition_active:
            return
        
        # Colors for the animation
        colors = ["#cccccc", "#999999", "#666666", "#333333", "#000000"]
        
        # Animate each dot with a delay
        for i, dot in enumerate(self.dots):
            self.dialog.after(i * 200, lambda d=dot, c=colors[0]: d.config(foreground=c))
        
        # Rotate colors
        colors = colors[1:] + [colors[0]]
        
        # Schedule next animation frame
        self.dialog.after(1000, self.animate_dots)
    
    def update_recognition_text(self, text):
        """Update the recognition text display"""
        self.recognition_text = text
        self.recognition_label.config(text=text if text else "Waiting for speech...")
    
    def set_final_result(self, result):
        """Set the final recognition result and close the dialog"""
        self.final_result = result
        self.recognition_active = False
        self.dialog.after(1000, self.dialog.destroy)
    
    def cancel(self):
        """Cancel the recognition and close the dialog"""
        self.recognition_active = False
        self.final_result = None
        self.dialog.destroy()
    
    @staticmethod
    def show_dialog(parent, callback=None):
        """Show the voice recognition dialog and return the result"""
        dialog = VoiceRecognitionDialog(parent)
        
        # If a callback is provided, call it with the dialog
        if callback:
            callback(dialog)
        
        # Wait for the dialog to close
        parent.wait_window(dialog.dialog)
        
        # Return the final result
        return dialog.final_result
