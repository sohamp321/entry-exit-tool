import face_recognition
import cv2
import numpy as np
import time
import threading

class FaceAuthenticator:
    def __init__(self, database):
        """Initialize the face authenticator with a database connection"""
        self.database = database
        self.known_face_encodings = {}
        self.known_face_ids = []
        self.load_known_faces()

        # Parameters for face recognition
        self.face_detection_model = "hog"  # or "cnn" for better but slower detection
        self.tolerance = 0.6  # Lower is more strict
        self.frame_skip = 3  # Process every nth frame for better performance

        # For smoother video processing
        self.processing_frame = False
        self.last_recognized_student = None
        self.last_message = "No face detected"

        # Camera settings
        self.camera_width = 640  # Lower resolution for better performance
        self.camera_height = 480

    def load_known_faces(self):
        """Load known face encodings from the database"""
        self.known_face_encodings = self.database.get_all_face_encodings()
        self.known_face_ids = list(self.known_face_encodings.keys())

    def register_face(self, frame, student_data):
        """Register a new face in the database"""
        # Detect faces in the frame
        face_locations = face_recognition.face_locations(frame, model=self.face_detection_model)

        if not face_locations:
            return False, "No face detected. Please look at the camera."

        if len(face_locations) > 1:
            return False, "Multiple faces detected. Please ensure only one person is in the frame."

        # Get the face encoding
        face_encoding = face_recognition.face_encodings(frame, face_locations)[0]

        # Add the student to the database
        roll_number = student_data['roll_number']
        name = student_data['name']
        hostel_name = student_data['hostel_name']
        room_number = student_data['room_number']
        contact_number = student_data['contact_number']

        success = self.database.add_student(
            roll_number, name, hostel_name, room_number, contact_number, face_encoding
        )

        if success:
            # Reload known faces
            self.load_known_faces()
            return True, f"Successfully registered {name}"
        else:
            return False, f"Student with roll number {roll_number} already exists"

    def recognize_face(self, frame):
        """Recognize a face in the frame"""
        # If no known faces, return early
        if not self.known_face_ids:
            return None, "No registered faces in the database"

        # Detect faces in the frame
        face_locations = face_recognition.face_locations(frame, model=self.face_detection_model)

        if not face_locations:
            return None, "No face detected"

        if len(face_locations) > 1:
            return None, "Multiple faces detected"

        # Get the face encoding
        face_encoding = face_recognition.face_encodings(frame, face_locations)[0]

        # Compare with known faces
        matches = []
        for student_id, known_encoding in self.known_face_encodings.items():
            # Compare faces
            match = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=self.tolerance)[0]
            if match:
                # Calculate face distance (lower is better)
                face_distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
                matches.append((student_id, face_distance))

        if not matches:
            return None, "Face not recognized"

        # Get the best match (lowest distance)
        best_match = min(matches, key=lambda x: x[1])
        student_id, face_distance = best_match

        # Get student details
        student = self.database.get_student_by_id(student_id)

        if not student:
            return None, "Student not found in database"

        return student, f"Recognized: {student[2]}"  # student[2] is the name

    def process_video_feed(self, frame_callback, stop_event):
        """Process video feed for face recognition"""
        # Initialize webcam
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return "Error: Could not open webcam"

        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        cap.set(cv2.CAP_PROP_FPS, 30)  # Request 30fps if supported

        # For tracking frame rate
        frame_count = 0
        last_time = time.time()
        fps = 0

        # Start a separate thread for face recognition to keep UI responsive
        recognition_thread = None

        while not stop_event.is_set():
            # Read a frame from the webcam
            ret, frame = cap.read()

            if not ret:
                break

            # Always draw face locations for visual feedback
            self.draw_face_locations(frame)

            # Calculate and display FPS
            current_time = time.time()
            if current_time - last_time >= 1.0:  # Update FPS every second
                fps = frame_count / (current_time - last_time)
                frame_count = 0
                last_time = current_time

            # Add FPS display to frame
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Process every nth frame for face recognition
            if frame_count % self.frame_skip == 0 and not self.processing_frame:
                # Set flag to prevent multiple recognition threads
                self.processing_frame = True

                # Make a copy of the frame for processing
                process_frame = frame.copy()

                # Start recognition in a separate thread
                if recognition_thread is not None and recognition_thread.is_alive():
                    recognition_thread.join(0.01)  # Wait briefly for previous thread

                recognition_thread = threading.Thread(
                    target=self._process_frame,
                    args=(process_frame, frame_callback)
                )
                recognition_thread.daemon = True
                recognition_thread.start()

            # Always update the display with the current frame
            frame_callback(frame, self.last_recognized_student, self.last_message)

            frame_count += 1

            # Small delay to reduce CPU usage but keep UI responsive
            time.sleep(0.005)

        # Release the webcam
        cap.release()
        return "Video feed stopped"

    def _process_frame(self, frame, frame_callback):
        """Process a single frame for face recognition (runs in a separate thread)"""
        try:
            # Convert BGR to RGB (face_recognition uses RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect and recognize faces
            student, message = self.recognize_face(rgb_frame)

            # Update the last recognized student and message
            self.last_recognized_student = student
            self.last_message = message
        finally:
            # Clear the processing flag
            self.processing_frame = False

    def draw_face_locations(self, frame):
        """Draw rectangles around detected faces"""
        # Convert BGR to RGB (face_recognition uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame, model=self.face_detection_model)

        # Draw rectangles around faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    def capture_single_frame(self):
        """Capture a single frame from the webcam"""
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return None, "Error: Could not open webcam"

        # Wait for the camera to initialize
        time.sleep(0.5)

        # Read a frame
        ret, frame = cap.read()

        # Release the webcam
        cap.release()

        if not ret:
            return None, "Error: Could not read frame from webcam"

        return frame, "Frame captured successfully"
