import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import cv2
from PIL import Image, ImageTk
import threading
import time
import datetime
import os

# Import custom styles and widgets
from styles import AppStyles
from custom_widgets import PrimaryButton, SecondaryButton, DangerButton, DefaultButton

# Import NLP summary module
from nlp_summary import ActivitySummarizer

class HostelAuthGUI:
    def __init__(self, root, face_authenticator, database):
        """Initialize the GUI"""
        self.root = root
        self.face_authenticator = face_authenticator
        self.database = database

        # Initialize activity summarizer
        self.activity_summarizer = ActivitySummarizer(database)

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

        # Flag for authentication method
        self.using_voice_auth = False

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

        # Right frame for student information and summaries
        self.right_frame = ttk.Frame(self.main_frame, padding=AppStyles.PADDING_MEDIUM, relief=tk.RIDGE, borderwidth=1)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create a notebook (tabbed interface) for the right frame
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.info_tab = ttk.Frame(self.notebook, padding=AppStyles.PADDING_SMALL)
        self.summary_tab = ttk.Frame(self.notebook, padding=AppStyles.PADDING_SMALL)

        # Add tabs to notebook
        self.notebook.add(self.info_tab, text="Student Info")
        self.notebook.add(self.summary_tab, text="Activity Summary")

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

        # Student info tab
        # Student info frame with a title
        info_title_frame = ttk.Frame(self.info_tab)
        info_title_frame.pack(fill=tk.X, pady=(0, AppStyles.PADDING_SMALL))
        ttk.Label(info_title_frame, text="Student Information", style="Title.TLabel").pack(anchor=tk.W)

        # Student info in a bordered frame
        info_container = ttk.Frame(self.info_tab, relief=tk.SUNKEN, borderwidth=1)
        info_container.pack(fill=tk.BOTH, expand=True, pady=AppStyles.PADDING_SMALL)

        self.student_info_frame = ttk.Frame(info_container, padding=AppStyles.PADDING_MEDIUM)
        self.student_info_frame.pack(fill=tk.BOTH, expand=True)

        # Log section with a separator and title
        ttk.Separator(self.info_tab, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=AppStyles.PADDING_MEDIUM)

        log_title_frame = ttk.Frame(self.info_tab)
        log_title_frame.pack(fill=tk.X, pady=(0, AppStyles.PADDING_SMALL))
        ttk.Label(log_title_frame, text="Recent Activity", style="BlackTitle.TLabel").pack(anchor=tk.W)

        # Log in a bordered frame
        log_container = ttk.Frame(self.info_tab, relief=tk.SUNKEN, borderwidth=1)
        log_container.pack(fill=tk.BOTH, expand=True, pady=AppStyles.PADDING_SMALL)

        self.log_frame = ttk.Frame(log_container, padding=AppStyles.PADDING_SMALL)
        self.log_frame.pack(fill=tk.BOTH, expand=True)

        # Summary tab
        summary_title_frame = ttk.Frame(self.summary_tab)
        summary_title_frame.pack(fill=tk.X, pady=(0, AppStyles.PADDING_SMALL))
        ttk.Label(summary_title_frame, text="Activity Summary", style="Title.TLabel").pack(anchor=tk.W)

        # Summary options frame
        summary_options_frame = ttk.Frame(self.summary_tab)
        summary_options_frame.pack(fill=tk.X, pady=AppStyles.PADDING_SMALL)

        # Radio buttons for summary type
        self.summary_type_var = tk.StringVar(value="student")

        student_summary_radio = ttk.Radiobutton(summary_options_frame, text="Current Student",
                                              variable=self.summary_type_var, value="student",
                                              command=self.refresh_summary)
        student_summary_radio.pack(side=tk.LEFT, padx=AppStyles.PADDING_SMALL)

        hostel_summary_radio = ttk.Radiobutton(summary_options_frame, text="Entire Hostel",
                                             variable=self.summary_type_var, value="hostel",
                                             command=self.refresh_summary)
        hostel_summary_radio.pack(side=tk.LEFT, padx=AppStyles.PADDING_SMALL)

        # Time period dropdown
        time_frame = ttk.Frame(summary_options_frame)
        time_frame.pack(side=tk.RIGHT, padx=AppStyles.PADDING_SMALL)

        ttk.Label(time_frame, text="Time Period:").pack(side=tk.LEFT, padx=(0, AppStyles.PADDING_SMALL))

        self.time_period_var = tk.StringVar(value="7")
        time_period_combo = ttk.Combobox(time_frame, textvariable=self.time_period_var,
                                        values=["1", "7", "30"], width=5)
        time_period_combo.pack(side=tk.LEFT)
        time_period_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_summary())

        # Summary text area in a bordered frame
        summary_container = ttk.Frame(self.summary_tab, relief=tk.SUNKEN, borderwidth=1)
        summary_container.pack(fill=tk.BOTH, expand=True, pady=AppStyles.PADDING_SMALL)

        # Use scrolledtext for the summary
        self.summary_text = scrolledtext.ScrolledText(summary_container, wrap=tk.WORD,
                                                   font=("Helvetica", 11), padx=10, pady=10)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        self.summary_text.config(state=tk.DISABLED)  # Make read-only initially

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

        button_frame3 = ttk.Frame(self.control_frame)
        button_frame3.pack(fill=tk.X, pady=AppStyles.PADDING_SMALL)

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

        # Summary button
        self.summary_button = SecondaryButton(button_frame3, text="Activity Summary",
                                            command=self.show_activity_summary)
        self.summary_button.pack(side=tk.LEFT, padx=AppStyles.PADDING_SMALL, fill=tk.X, expand=True)

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

        # Add log filter controls
        log_filter_frame = ttk.Frame(self.log_frame)
        log_filter_frame.pack(fill=tk.X, pady=(0, AppStyles.PADDING_SMALL))

        # Radio buttons for log filtering
        self.log_filter_var = tk.StringVar(value="current")

        current_student_radio = ttk.Radiobutton(log_filter_frame, text="Current Student",
                                              variable=self.log_filter_var, value="current",
                                              command=self.refresh_logs)
        current_student_radio.pack(side=tk.LEFT, padx=AppStyles.PADDING_SMALL)

        all_logs_radio = ttk.Radiobutton(log_filter_frame, text="All Students",
                                        variable=self.log_filter_var, value="all",
                                        command=self.refresh_logs)
        all_logs_radio.pack(side=tk.LEFT, padx=AppStyles.PADDING_SMALL)

        # Create a treeview for logs with scrollbar
        log_tree_frame = ttk.Frame(self.log_frame)
        log_tree_frame.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(log_tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create treeview with improved styling and more columns
        columns = ("Action", "Timestamp", "Name", "Roll Number", "Hostel", "Room")
        self.log_tree = ttk.Treeview(log_tree_frame, columns=columns, show="headings",
                                    yscrollcommand=scrollbar.set, style="Treeview")

        # Configure column headings and widths
        self.log_tree.heading("Action", text="Action")
        self.log_tree.heading("Timestamp", text="Timestamp")
        self.log_tree.heading("Name", text="Name")
        self.log_tree.heading("Roll Number", text="Roll Number")
        self.log_tree.heading("Hostel", text="Hostel")
        self.log_tree.heading("Room", text="Room")

        # Set column widths and alignment
        self.log_tree.column("Action", width=80, anchor=tk.CENTER)
        self.log_tree.column("Timestamp", width=150)
        self.log_tree.column("Name", width=120)
        self.log_tree.column("Roll Number", width=100, anchor=tk.CENTER)
        self.log_tree.column("Hostel", width=80, anchor=tk.CENTER)
        self.log_tree.column("Room", width=60, anchor=tk.CENTER)

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

            # Refresh logs based on current filter setting
            self.refresh_logs()

            # Enable entry/exit buttons
            self.entry_button.config(state=tk.NORMAL)
            self.exit_button.config(state=tk.NORMAL)
        else:
            # If no student is recognized but we were showing a student before
            if self.current_student is not None:
                self.current_student = None
                self.update_student_info(None)
                self.refresh_logs()  # Update logs based on filter setting

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

    # Track the last log count to prevent unnecessary refreshes
    last_log_count = 0
    last_filter_mode = "current"
    last_student_id = None

    def refresh_logs(self):
        """Refresh logs based on the current filter setting"""
        # Get the current filter setting
        filter_mode = self.log_filter_var.get()
        current_student_id = self.current_student[0] if self.current_student else None

        # Check if we need to refresh based on changes
        refresh_needed = False

        # If filter mode changed, we need to refresh
        if filter_mode != self.__class__.last_filter_mode:
            refresh_needed = True
            self.__class__.last_filter_mode = filter_mode

        # If student changed, we need to refresh
        if current_student_id != self.__class__.last_student_id:
            refresh_needed = True
            self.__class__.last_student_id = current_student_id

        # If no refresh is needed, return early
        if not refresh_needed and not self._is_log_count_changed(filter_mode, current_student_id):
            return

        # Perform the refresh
        if filter_mode == "current" and self.current_student:
            # Show logs for current student only
            self.update_logs(self.current_student[0])
        elif filter_mode == "all" or not self.current_student:
            # Show all logs
            self.show_all_logs()

    def _is_log_count_changed(self, filter_mode, student_id):
        """Check if the log count has changed"""
        if filter_mode == "current" and student_id:
            # Count logs for the current student
            logs = self.database.get_student_logs(student_id)
            current_count = len(logs)
        else:
            # Count all logs
            logs = self.database.get_all_logs()
            current_count = len(logs)

        # Check if count changed
        if current_count != self.__class__.last_log_count:
            self.__class__.last_log_count = current_count
            return True

        return False

    def update_logs(self, student_id):
        """Update the logs display for a student"""
        # Clear existing logs
        self.clear_logs()

        # Get logs for the student
        logs = self.database.get_student_logs(student_id)

        # Add logs to the treeview with all available information
        for log_entry in logs:
            # Unpack the log entry
            if len(log_entry) >= 6:  # New format with more details
                action, timestamp, name, roll_number, hostel, room = log_entry
            elif len(log_entry) >= 2:  # Old format with just action and timestamp
                action, timestamp = log_entry
                name = roll_number = hostel = room = ""
            else:
                continue  # Skip invalid log entries

            # Insert into treeview with all columns
            self.log_tree.insert("", "end", values=(
                action.capitalize(),
                timestamp,
                name,
                roll_number,
                hostel,
                room
            ))

    def show_all_logs(self):
        """Show logs for all students"""
        # Clear existing logs
        self.clear_logs()

        # Get all logs
        logs = self.database.get_all_logs()

        # Add logs to the treeview
        for log_entry in logs:
            # Unpack the log entry
            if len(log_entry) >= 6:  # New format with more details
                action, timestamp, name, roll_number, hostel, room = log_entry
            elif len(log_entry) >= 2:  # Old format with just action and timestamp
                action, timestamp = log_entry
                name = roll_number = hostel = room = ""
            else:
                continue  # Skip invalid log entries

            # Insert into treeview with all columns
            self.log_tree.insert("", "end", values=(
                action.capitalize(),
                timestamp,
                name,
                roll_number,
                hostel,
                room
            ))

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

        # Update logs display based on current filter setting
        self.refresh_logs()

        # Update status
        self.status_label.config(text=f"{action.capitalize()} logged for {student_name}")

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



    # Activity summary methods
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
