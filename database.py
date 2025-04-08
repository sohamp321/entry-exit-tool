import os
import json
import datetime
import pickle
import threading
import base64

class HostelDatabase:
    def __init__(self, db_path="hostel_data.json"):
        """Initialize the database"""
        self.db_path = db_path
        self.lock = threading.RLock()  # Reentrant lock for thread safety

        # Initialize data structure
        self.data = {
            "students": [],
            "logs": []
        }

        # Load existing data if file exists
        self.load_data()

    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.db_path):
            try:
                with self.lock:
                    with open(self.db_path, 'r') as f:
                        data = json.load(f)

                        # Convert face encodings back from base64
                        for student in data.get('students', []):
                            if 'face_encoding' in student:
                                face_encoding_bytes = base64.b64decode(student['face_encoding'])
                                student['face_encoding'] = pickle.loads(face_encoding_bytes)

                        self.data = data
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading database: {e}")
                # Initialize with empty data if file is corrupted
                self.data = {"students": [], "logs": []}

    def save_data(self):
        """Save data to JSON file"""
        with self.lock:
            # Create a copy of the data for serialization
            data_copy = {
                "students": [],
                "logs": self.data["logs"].copy()
            }

            # Convert face encodings to base64 for JSON serialization
            for student in self.data["students"]:
                student_copy = student.copy()
                if 'face_encoding' in student_copy:
                    face_encoding_bytes = pickle.dumps(student_copy['face_encoding'])
                    student_copy['face_encoding'] = base64.b64encode(face_encoding_bytes).decode('utf-8')
                data_copy["students"].append(student_copy)

            # Save to file
            with open(self.db_path, 'w') as f:
                json.dump(data_copy, f, indent=2)

    def close(self):
        """Save data before closing"""
        self.save_data()

    def add_student(self, roll_number, name, hostel_name, room_number, contact_number, face_encoding):
        """Add a new student to the database"""
        with self.lock:
            # Check if roll number already exists
            for student in self.data["students"]:
                if student["roll_number"] == roll_number:
                    return False

            # Generate a unique ID
            student_id = 1
            if self.data["students"]:
                student_id = max(student["id"] for student in self.data["students"]) + 1

            # Create student record
            student = {
                "id": student_id,
                "roll_number": roll_number,
                "name": name,
                "hostel_name": hostel_name,
                "room_number": room_number,
                "contact_number": contact_number,
                "face_encoding": face_encoding,
                "registration_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Add to students list
            self.data["students"].append(student)

            # Save changes
            self.save_data()

            return True

    def get_all_students(self):
        """Get all students from the database"""
        with self.lock:
            # Convert to the same format as the SQLite version for compatibility
            return [
                (s["id"], s["roll_number"], s["name"], s["hostel_name"], s["room_number"], s["contact_number"])
                for s in self.data["students"]
            ]

    def get_student_by_id(self, student_id):
        """Get student details by ID"""
        with self.lock:
            for student in self.data["students"]:
                if student["id"] == student_id:
                    # Return in the same format as the SQLite version
                    return (
                        student["id"],
                        student["roll_number"],
                        student["name"],
                        student["hostel_name"],
                        student["room_number"],
                        student["contact_number"]
                    )
            return None

    def get_student_by_roll_number(self, roll_number):
        """Get student details by roll number"""
        with self.lock:
            for student in self.data["students"]:
                if student["roll_number"] == roll_number:
                    # Return in the same format as the SQLite version
                    return (
                        student["id"],
                        student["roll_number"],
                        student["name"],
                        student["hostel_name"],
                        student["room_number"],
                        student["contact_number"]
                    )
            return None

    def get_all_face_encodings(self):
        """Get all face encodings for recognition"""
        with self.lock:
            encodings = {}
            for student in self.data["students"]:
                encodings[student["id"]] = student["face_encoding"]
            return encodings

    def log_entry_exit(self, student_id, action):
        """Log entry or exit for a student"""
        if action not in ['entry', 'exit']:
            raise ValueError("Action must be 'entry' or 'exit'")

        with self.lock:
            # Get student details for the log
            student = None
            for s in self.data["students"]:
                if s["id"] == student_id:
                    student = s
                    break

            if not student:
                raise ValueError(f"Student with ID {student_id} not found")

            # Generate a unique ID for the log
            log_id = 1
            if self.data["logs"]:
                log_id = max(log["id"] for log in self.data["logs"]) + 1

            # Create log entry with more information
            log = {
                "id": log_id,
                "student_id": student_id,
                "student_name": student["name"],
                "roll_number": student["roll_number"],
                "hostel_name": student["hostel_name"],
                "room_number": student["room_number"],
                "action": action,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Add to logs list
            self.data["logs"].append(log)

            # Save changes
            self.save_data()

    def get_student_logs(self, student_id, limit=10):
        """Get recent entry/exit logs for a student"""
        with self.lock:
            # Filter logs for the student
            student_logs = [log for log in self.data["logs"] if log["student_id"] == student_id]

            # Sort by timestamp (descending)
            student_logs.sort(key=lambda x: x["timestamp"], reverse=True)

            # Limit the number of logs
            student_logs = student_logs[:limit]

            # Return more detailed log information
            return [(log["action"], log["timestamp"],
                    log.get("student_name", ""),
                    log.get("roll_number", ""),
                    log.get("hostel_name", ""),
                    log.get("room_number", "")) for log in student_logs]

    def get_all_logs(self, limit=50):
        """Get all logs for all students"""
        with self.lock:
            # Make a copy of all logs
            all_logs = self.data["logs"].copy()

            # Sort by timestamp (descending)
            all_logs.sort(key=lambda x: x["timestamp"], reverse=True)

            # Limit the number of logs
            all_logs = all_logs[:limit]

            # Return detailed log information
            return [(log["action"], log["timestamp"],
                    log.get("student_name", ""),
                    log.get("roll_number", ""),
                    log.get("hostel_name", ""),
                    log.get("room_number", "")) for log in all_logs]

    def delete_student(self, student_id):
        """Delete a student from the database"""
        with self.lock:
            # Remove student
            self.data["students"] = [s for s in self.data["students"] if s["id"] != student_id]

            # Remove associated logs
            self.data["logs"] = [log for log in self.data["logs"] if log["student_id"] != student_id]

            # Save changes
            self.save_data()
