import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import cv2
from PIL import Image, ImageTk
import threading
import time
import datetime
import os

# Import custom styles and widgets
from styles import AppStyles
from custom_widgets import PrimaryButton, SecondaryButton, DangerButton, DefaultButton

class HostelAuthGUI:
    def __init__(self, root, face_authenticator, database):
        """Initialize the GUI"""
        self.root = root
        self.face_authenticator = face_authenticator
        self.database = database

        # Set window title and size
        self.root.title("Hostel Face Authentication System")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)

        # Apply custom styles
        self.style = AppStyles.apply_styles(root)

        # Set icon if available
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except Exception:
            pass  # Ignore if icon is not available

        # Create a stop event for the video feed
        self.stop_event = threading.Event()

        # Create main frames
        self.create_frames()

        # Create widgets
        self.create_widgets()

        # Initialize video feed
        self.video_running = False
        self.register_video_running = False
        self.current_student = None
        self.captured_frame = None

        # Start with the main screen
        self.show_main_screen()

    def create_frames(self):
        """Create the main frames for the GUI"""
        # Main container frame
        self.main_frame = ttk.Frame(self.root, padding=AppStyles.PADDING_LARGE)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for video feed and controls
        self.left_frame = ttk.Frame(self.main_frame, padding=AppStyles.PADDING_MEDIUM, relief=tk.RIDGE, borderwidth=1)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, AppStyles.PADDING_MEDIUM))

        # Right frame for student information
        self.right_frame = ttk.Frame(self.main_frame, padding=AppStyles.PADDING_MEDIUM, relief=tk.RIDGE, borderwidth=1)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Video frame with a title
        video_title_frame = ttk.Frame(self.left_frame)
        video_title_frame.pack(fill=tk.X, pady=(0, AppStyles.PADDING_SMALL))
        ttk.Label(video_title_frame, text="Camera Feed", style="Title.TLabel").pack(anchor=tk.W)

        # Video frame with a border
        video_container = ttk.Frame(self.left_frame, relief=tk.SUNKEN, borderwidth=1)
        video_container.pack(fill=tk.BOTH, expand=True, pady=AppStyles.PADDING_SMALL)

        self.video_frame = ttk.Frame(video_container, padding=AppStyles.PADDING_SMALL)
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        # Control frame with a separator
        ttk.Separator(self.left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=AppStyles.PADDING_MEDIUM)

        control_title_frame = ttk.Frame(self.left_frame)
        control_title_frame.pack(fill=tk.X, pady=(0, AppStyles.PADDING_SMALL))
        ttk.Label(control_title_frame, text="Controls", style="Title.TLabel").pack(anchor=tk.W)

        self.control_frame = ttk.Frame(self.left_frame, padding=AppStyles.PADDING_SMALL)
        self.control_frame.pack(fill=tk.X, pady=AppStyles.PADDING_SMALL)

        # Student info frame with a title
        info_title_frame = ttk.Frame(self.right_frame)
        info_title_frame.pack(fill=tk.X, pady=(0, AppStyles.PADDING_SMALL))
        ttk.Label(info_title_frame, text="Student Information", style="Title.TLabel").pack(anchor=tk.W)

        # Student info in a bordered frame
        info_container = ttk.Frame(self.right_frame, relief=tk.SUNKEN, borderwidth=1)
        info_container.pack(fill=tk.BOTH, expand=True, pady=AppStyles.PADDING_SMALL)

        self.student_info_frame = ttk.Frame(info_container, padding=AppStyles.PADDING_MEDIUM)
        self.student_info_frame.pack(fill=tk.BOTH, expand=True)

        # Log frame with a separator and title
        ttk.Separator(self.right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=AppStyles.PADDING_MEDIUM)

        log_title_frame = ttk.Frame(self.right_frame)
        log_title_frame.pack(fill=tk.X, pady=(0, AppStyles.PADDING_SMALL))
        ttk.Label(log_title_frame, text="Recent Activity", style="Title.TLabel").pack(anchor=tk.W)

        # Log in a bordered frame
        log_container = ttk.Frame(self.right_frame, relief=tk.SUNKEN, borderwidth=1)
        log_container.pack(fill=tk.BOTH, expand=True, pady=AppStyles.PADDING_SMALL)

        self.log_frame = ttk.Frame(log_container, padding=AppStyles.PADDING_SMALL)
        self.log_frame.pack(fill=tk.BOTH, expand=True)

    def create_widgets(self):
        """Create widgets for the GUI"""
        # Video label with a black background for better visibility
        video_bg = ttk.Frame(self.video_frame, style="Video.TFrame")
        video_bg.pack(fill=tk.BOTH, expand=True)
        self.style.configure("Video.TFrame", background="black")

        self.video_label = ttk.Label(video_bg)
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Status label with a distinctive style
        self.status_label = ttk.Label(self.video_frame, text="Camera not started", style="Header.TLabel")
        self.status_label.pack(pady=AppStyles.PADDING_SMALL, anchor=tk.CENTER)

        # Control buttons with improved layout and styles
        button_frame1 = ttk.Frame(self.control_frame)
        button_frame1.pack(fill=tk.X, pady=AppStyles.PADDING_SMALL)

        button_frame2 = ttk.Frame(self.control_frame)
        button_frame2.pack(fill=tk.X, pady=AppStyles.PADDING_SMALL)

        # Camera control buttons - using custom buttons with explicit colors
        self.start_button = PrimaryButton(button_frame1, text="Start Camera", command=self.start_video)
        self.start_button.pack(side=tk.LEFT, padx=AppStyles.PADDING_SMALL, fill=tk.X, expand=True)

        self.stop_button = PrimaryButton(button_frame1, text="Stop Camera", command=self.stop_video)
        self.stop_button.pack(side=tk.LEFT, padx=AppStyles.PADDING_SMALL, fill=tk.X, expand=True)
        self.stop_button.config(state=tk.DISABLED)

        self.register_button = SecondaryButton(button_frame1, text="Register New Student", command=self.show_register_screen)
        self.register_button.pack(side=tk.LEFT, padx=AppStyles.PADDING_SMALL, fill=tk.X, expand=True)

        # Entry/Exit buttons
        self.entry_button = SecondaryButton(button_frame2, text="Log Entry", command=lambda: self.log_entry_exit("entry"))
        self.entry_button.pack(side=tk.LEFT, padx=AppStyles.PADDING_SMALL, fill=tk.X, expand=True)
        self.entry_button.config(state=tk.DISABLED)

        self.exit_button = DangerButton(button_frame2, text="Log Exit", command=lambda: self.log_entry_exit("exit"))
        self.exit_button.pack(side=tk.LEFT, padx=AppStyles.PADDING_SMALL, fill=tk.X, expand=True)
        self.exit_button.config(state=tk.DISABLED)

        # Student info - title already added in create_frames
        self.info_frame = ttk.Frame(self.student_info_frame)
        self.info_frame.pack(fill=tk.BOTH, expand=True, pady=AppStyles.PADDING_SMALL)

        # Create labels for student info with consistent styling
        self.info_labels = {}
        fields = ["Name", "Roll Number", "Hostel", "Room Number", "Contact"]

        # Configure grid for better alignment
        self.info_frame.columnconfigure(0, weight=1)
        self.info_frame.columnconfigure(1, weight=2)

        for i, field in enumerate(fields):
            # Label with field name
            field_label = ttk.Label(self.info_frame, text=f"{field}:", style="Header.TLabel")
            field_label.grid(row=i, column=0, sticky=tk.W, pady=AppStyles.PADDING_SMALL)

            # Label for value
            value_label = ttk.Label(self.info_frame, text="", style="TLabel")
            value_label.grid(row=i, column=1, sticky=tk.W, pady=AppStyles.PADDING_SMALL, padx=AppStyles.PADDING_MEDIUM)

            # Store reference
            self.info_labels[field.lower().replace(" ", "_")] = value_label

        # Log section - title already added in create_frames

        # Create a treeview for logs with scrollbar
        log_tree_frame = ttk.Frame(self.log_frame)
        log_tree_frame.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(log_tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create treeview with improved styling
        self.log_tree = ttk.Treeview(log_tree_frame, columns=("Action", "Timestamp"), show="headings",
                                    yscrollcommand=scrollbar.set, style="Treeview")
        self.log_tree.heading("Action", text="Action")
        self.log_tree.heading("Timestamp", text="Timestamp")
        self.log_tree.column("Action", width=100, anchor=tk.CENTER)
        self.log_tree.column("Timestamp", width=200)
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbar
        scrollbar.config(command=self.log_tree.yview)

        # Register screen widgets with improved layout
        self.register_frame = ttk.Frame(self.root, padding=AppStyles.PADDING_LARGE)

        # Title for registration screen
        title_frame = ttk.Frame(self.register_frame)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, AppStyles.PADDING_LARGE))
        ttk.Label(title_frame, text="Register New Student", style="Title.TLabel").pack(anchor=tk.W)

        # Create a two-column layout
        left_column = ttk.Frame(self.register_frame, padding=AppStyles.PADDING_MEDIUM)
        left_column.grid(row=1, column=0, sticky=tk.NSEW, padx=(0, AppStyles.PADDING_MEDIUM))

        right_column = ttk.Frame(self.register_frame, padding=AppStyles.PADDING_MEDIUM)
        right_column.grid(row=1, column=1, sticky=tk.NSEW)

        # Configure grid weights
        self.register_frame.columnconfigure(0, weight=1)
        self.register_frame.columnconfigure(1, weight=1)
        self.register_frame.rowconfigure(1, weight=1)

        # Form section title
        form_title_frame = ttk.Frame(left_column)
        form_title_frame.pack(fill=tk.X, pady=(0, AppStyles.PADDING_SMALL))
        ttk.Label(form_title_frame, text="Student Details", style="Title.TLabel").pack(anchor=tk.W)

        # Form container with border
        form_container = ttk.Frame(left_column, relief=tk.SUNKEN, borderwidth=1)
        form_container.pack(fill=tk.BOTH, expand=True, pady=AppStyles.PADDING_SMALL)

        form_frame = ttk.Frame(form_container, padding=AppStyles.PADDING_MEDIUM)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Create entry fields for registration with improved styling
        self.register_entries = {}
        register_fields = [
            ("Roll Number", "roll_number"),
            ("Name", "name"),
            ("Hostel Name", "hostel_name"),
            ("Room Number", "room_number"),
            ("Contact Number", "contact_number")
        ]

        # Configure form grid
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=2)

        for i, (label_text, field_name) in enumerate(register_fields):
            # Label with field name
            field_label = ttk.Label(form_frame, text=f"{label_text}:", style="Header.TLabel")
            field_label.grid(row=i, column=0, sticky=tk.W, pady=AppStyles.PADDING_SMALL)

            # Entry field
            entry_field = ttk.Entry(form_frame, width=30)
            entry_field.grid(row=i, column=1, sticky=tk.EW, pady=AppStyles.PADDING_SMALL, padx=AppStyles.PADDING_SMALL)

            # Store reference
            self.register_entries[field_name] = entry_field

        # Register buttons with improved styling
        self.register_control_frame = ttk.Frame(left_column, padding=AppStyles.PADDING_SMALL)
        self.register_control_frame.pack(fill=tk.X, pady=AppStyles.PADDING_MEDIUM)

        self.capture_button = PrimaryButton(self.register_control_frame, text="Capture Face",
                                       command=self.capture_face)
        self.capture_button.pack(side=tk.LEFT, padx=AppStyles.PADDING_SMALL, fill=tk.X, expand=True)

        self.save_button = SecondaryButton(self.register_control_frame, text="Save",
                                    command=self.save_registration)
        self.save_button.pack(side=tk.LEFT, padx=AppStyles.PADDING_SMALL, fill=tk.X, expand=True)

        self.cancel_button = DangerButton(self.register_control_frame, text="Cancel",
                                      command=self.show_main_screen)
        self.cancel_button.pack(side=tk.LEFT, padx=AppStyles.PADDING_SMALL, fill=tk.X, expand=True)

        # Video section title
        video_title_frame = ttk.Frame(right_column)
        video_title_frame.pack(fill=tk.X, pady=(0, AppStyles.PADDING_SMALL))
        ttk.Label(video_title_frame, text="Camera Feed", style="Title.TLabel").pack(anchor=tk.W)

        # Video container with border
        video_container = ttk.Frame(right_column, relief=tk.SUNKEN, borderwidth=1)
        video_container.pack(fill=tk.BOTH, expand=True, pady=AppStyles.PADDING_SMALL)

        self.register_video_frame = ttk.Frame(video_container, padding=AppStyles.PADDING_SMALL)
        self.register_video_frame.pack(fill=tk.BOTH, expand=True)

        # Video label with black background
        video_bg = ttk.Frame(self.register_video_frame, style="Video.TFrame")
        video_bg.pack(fill=tk.BOTH, expand=True)

        self.register_video_label = ttk.Label(video_bg)
        self.register_video_label.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Status label with improved styling
        self.register_status_label = ttk.Label(self.register_video_frame,
                                             text="Starting camera...",
                                             style="Header.TLabel")
        self.register_status_label.pack(pady=AppStyles.PADDING_SMALL, anchor=tk.CENTER)

    def show_main_screen(self):
        """Show the main screen"""
        # Stop registration video if running
        if hasattr(self, 'register_video_running') and self.register_video_running:
            self.stop_register_video()

        self.register_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Reset current student
        self.current_student = None
        self.update_student_info(None)
        self.clear_logs()

    def show_register_screen(self):
        """Show the registration screen"""
        # Stop video if running
        if self.video_running:
            self.stop_video()

        self.main_frame.pack_forget()
        self.register_frame.pack(fill=tk.BOTH, expand=True)

        # Clear entry fields
        for entry in self.register_entries.values():
            entry.delete(0, tk.END)

        # Clear register video label
        self.register_video_label.config(image="")
        self.register_status_label.config(text="Starting camera...")

        # Reset captured face
        self.captured_frame = None

        # Start registration camera feed
        self.start_register_video()

    def start_video(self):
        """Start the video feed"""
        if not self.video_running:
            self.video_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Reset stop event
            self.stop_event.clear()

            # Start video in a separate thread
            self.video_thread = threading.Thread(target=self.video_loop)
            self.video_thread.daemon = True
            self.video_thread.start()

    def stop_video(self):
        """Stop the video feed"""
        if self.video_running:
            self.stop_event.set()
            self.video_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.entry_button.config(state=tk.DISABLED)
            self.exit_button.config(state=tk.DISABLED)

            # Clear video label
            self.video_label.config(image="")
            self.status_label.config(text="Camera stopped")

    def video_loop(self):
        """Process video feed in a loop"""
        self.face_authenticator.process_video_feed(self.update_frame, self.stop_event)

    def update_frame(self, frame, student, message):
        """Update the video frame and recognition results"""
        # Convert frame to ImageTk format
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        photo = ImageTk.PhotoImage(image=image)

        # Update video label
        self.video_label.config(image=photo)
        self.video_label.image = photo  # Keep a reference

        # Update status
        self.status_label.config(text=message)

        # Update student info if recognized
        if student:
            self.current_student = student
            self.update_student_info(student)
            self.update_logs(student[0])  # student[0] is the ID

            # Enable entry/exit buttons
            self.entry_button.config(state=tk.NORMAL)
            self.exit_button.config(state=tk.NORMAL)
        else:
            # Disable entry/exit buttons if no student recognized
            self.entry_button.config(state=tk.DISABLED)
            self.exit_button.config(state=tk.DISABLED)

    def update_student_info(self, student):
        """Update the student information display"""
        if student:
            # student format: (id, roll_number, name, hostel_name, room_number, contact_number)
            self.info_labels["name"].config(text=student[2])
            self.info_labels["roll_number"].config(text=student[1])
            self.info_labels["hostel"].config(text=student[3])
            self.info_labels["room_number"].config(text=student[4])
            self.info_labels["contact"].config(text=student[5])
        else:
            # Clear info
            for label in self.info_labels.values():
                label.config(text="")

    def update_logs(self, student_id):
        """Update the logs display for a student"""
        # Clear existing logs
        self.clear_logs()

        # Get logs for the student
        logs = self.database.get_student_logs(student_id)

        # Add logs to the treeview
        for action, timestamp in logs:
            self.log_tree.insert("", "end", values=(action.capitalize(), timestamp))

    def clear_logs(self):
        """Clear the logs display"""
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

    def log_entry_exit(self, action):
        """Log an entry or exit for the current student"""
        if not self.current_student:
            messagebox.showerror("Error", "No student recognized")
            return

        student_id = self.current_student[0]
        student_name = self.current_student[2]

        # Log the action
        self.database.log_entry_exit(student_id, action)

        # Update logs display
        self.update_logs(student_id)

        # Show confirmation
        messagebox.showinfo("Success", f"{action.capitalize()} logged for {student_name}")

    def start_register_video(self):
        """Start the registration video feed"""
        if not self.register_video_running:
            self.register_video_running = True

            # Create a separate stop event for registration video
            self.register_stop_event = threading.Event()
            self.register_stop_event.clear()

            # Flag for frame capture
            self.capture_requested = False
            self.current_frame = None

            # Start video in a separate thread
            self.register_video_thread = threading.Thread(target=self.register_video_loop)
            self.register_video_thread.daemon = True
            self.register_video_thread.start()

    def stop_register_video(self):
        """Stop the registration video feed"""
        if self.register_video_running:
            self.register_stop_event.set()
            self.register_video_running = False

    def register_video_loop(self):
        """Process video feed for registration"""
        # Initialize webcam
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            self.register_status_label.config(text="Error: Could not open webcam")
            return

        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.face_authenticator.camera_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.face_authenticator.camera_height)
        cap.set(cv2.CAP_PROP_FPS, 30)  # Request 30fps if supported

        # For tracking frame rate
        frame_count = 0
        last_time = time.time()
        fps = 0

        while not self.register_stop_event.is_set():
            # Read a frame from the webcam
            ret, frame = cap.read()

            if not ret:
                break

            # Draw face locations for visual feedback
            self.face_authenticator.draw_face_locations(frame)

            # Calculate and display FPS
            current_time = time.time()
            if current_time - last_time >= 1.0:  # Update FPS every second
                fps = frame_count / (current_time - last_time)
                frame_count = 0
                last_time = current_time

            # Add FPS display to frame
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Store the current frame for capture if requested
            self.current_frame = frame.copy()

            # Check if capture was requested
            if self.capture_requested:
                self.captured_frame = self.current_frame.copy()
                self.capture_requested = False

            # Update the display
            self.update_register_frame(frame)

            frame_count += 1

            # Small delay to reduce CPU usage but keep UI responsive
            time.sleep(0.005)

        # Release the webcam
        cap.release()

    def update_register_frame(self, frame):
        """Update the registration video frame"""
        # Convert frame to ImageTk format
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        photo = ImageTk.PhotoImage(image=image)

        # Update video label
        self.register_video_label.config(image=photo)
        self.register_video_label.image = photo  # Keep a reference

        if not self.captured_frame:
            self.register_status_label.config(text="Look at the camera and click 'Capture Face'")

    def capture_face(self):
        """Capture a face for registration using the current frame"""
        if not self.register_video_running:
            messagebox.showerror("Error", "Camera is not running")
            return

        # Get the current frame from the video feed
        # We'll use a flag to request a frame capture
        self.capture_requested = True

        # Wait briefly for the frame to be captured
        # This will be filled by the register_video_loop
        self.captured_frame = None

        # Try to get a frame for up to 1 second
        start_time = time.time()
        while self.captured_frame is None and time.time() - start_time < 1.0:
            time.sleep(0.1)

        if self.captured_frame is None:
            messagebox.showerror("Error", "Could not capture frame")
            return

        # Stop the video feed
        self.stop_register_video()

        # Display the captured frame
        image = cv2.cvtColor(self.captured_frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        photo = ImageTk.PhotoImage(image=image)

        self.register_video_label.config(image=photo)
        self.register_video_label.image = photo  # Keep a reference

        self.register_status_label.config(text="Face captured. Click 'Save' to register.")

    def save_registration(self):
        """Save the registration information"""
        if self.captured_frame is None:
            messagebox.showerror("Error", "No face captured. Please capture a face first.")
            return

        # Get student data from entry fields
        student_data = {}
        for field, entry in self.register_entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Error", f"{field.replace('_', ' ').title()} cannot be empty")
                return
            student_data[field] = value

        # Register the face
        success, message = self.face_authenticator.register_face(self.captured_frame, student_data)

        if success:
            messagebox.showinfo("Success", message)
            self.show_main_screen()
        else:
            messagebox.showerror("Error", message)

    def on_closing(self):
        """Handle window closing"""
        # Stop videos if running
        if self.video_running:
            self.stop_video()

        if hasattr(self, 'register_video_running') and self.register_video_running:
            self.stop_register_video()

        # Close database connection
        self.database.close()

        # Destroy the window
        self.root.destroy()
