"""
Voice authentication and activity summary methods for the GUI.
These will be added to the HostelAuthGUI class.
"""

import tkinter as tk
from tkinter import messagebox
import threading

def start_voice_authentication(self):
    """Start voice authentication as a fallback method"""
    # Only allow voice authentication when camera is running but no face is detected
    if not self.video_running:
        messagebox.showinfo("Voice Authentication", "Please start the camera first.")
        return

    if self.current_student:
        messagebox.showinfo("Voice Authentication", "Face already recognized. Voice authentication not needed.")
        return

    # Set flag to indicate we're using voice authentication
    self.using_voice_auth = True

    # Disable buttons during voice authentication
    self.voice_auth_button.config(state=tk.DISABLED)
    self.start_button.config(state=tk.DISABLED)
    self.register_button.config(state=tk.DISABLED)

    # Update status
    self.status_label.config(text="Starting voice authentication...")

    # Start voice authentication in a separate thread
    threading.Thread(target=self._perform_voice_authentication, daemon=True).start()

def _perform_voice_authentication(self):
    """Perform voice authentication in a background thread"""
    try:
        # Attempt to authenticate by voice
        student = self.voice_authenticator.authenticate_by_voice()

        # Update UI in the main thread
        self.root.after(0, lambda: self._handle_voice_auth_result(student))
    except Exception as e:
        # Handle any errors
        self.root.after(0, lambda: self._handle_voice_auth_error(str(e)))

def _handle_voice_auth_result(self, student):
    """Handle the result of voice authentication"""
    # Re-enable buttons
    self.voice_auth_button.config(state=tk.NORMAL)
    self.start_button.config(state=tk.NORMAL)
    self.register_button.config(state=tk.NORMAL)

    if student:
        # Authentication successful
        self.current_student = student
        self.update_student_info(student)
        self.refresh_logs()

        # Enable entry/exit buttons
        self.entry_button.config(state=tk.NORMAL)
        self.exit_button.config(state=tk.NORMAL)

        # Update status
        self.status_label.config(text=f"Voice authentication successful: {student[2]}")
    else:
        # Authentication failed
        self.status_label.config(text="Voice authentication failed")

    # Reset flag
    self.using_voice_auth = False

def _handle_voice_auth_error(self, error_message):
    """Handle errors during voice authentication"""
    # Re-enable buttons
    self.voice_auth_button.config(state=tk.NORMAL)
    self.start_button.config(state=tk.NORMAL)
    self.register_button.config(state=tk.NORMAL)

    # Update status
    self.status_label.config(text=f"Voice authentication error: {error_message}")

    # Show error message
    messagebox.showerror("Voice Authentication Error", f"An error occurred: {error_message}")

    # Reset flag
    self.using_voice_auth = False

def show_activity_summary(self):
    """Show the activity summary tab"""
    # Switch to the summary tab
    self.notebook.select(self.summary_tab)

    # Refresh the summary
    self.refresh_summary()

def refresh_summary(self):
    """Refresh the activity summary based on current settings"""
    # Get the summary type and time period
    summary_type = self.summary_type_var.get()
    try:
        days = int(self.time_period_var.get())
    except ValueError:
        days = 7  # Default to 7 days if invalid value

    # Clear the current summary
    self.summary_text.config(state=tk.NORMAL)
    self.summary_text.delete(1.0, tk.END)

    # Generate the appropriate summary
    if summary_type == "student":
        if self.current_student:
            summary = self.activity_summarizer.generate_student_summary(self.current_student[0], days)
        else:
            summary = "No student currently recognized. Please authenticate a student first."
    else:  # hostel summary
        # Get the hostel name from the current student, or None for all hostels
        hostel_name = self.current_student[3] if self.current_student else None
        summary = self.activity_summarizer.generate_hostel_summary(hostel_name, days)

    # Display the summary
    self.summary_text.insert(tk.END, summary)
    self.summary_text.config(state=tk.DISABLED)  # Make read-only again
