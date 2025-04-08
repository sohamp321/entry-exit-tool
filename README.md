# Hostel Face Authentication System

A face recognition-based authentication system for hostel management. This system authenticates residents using facial recognition and tracks information like entry/exit times, hostel details, and personal information.

## Features

- **Face Recognition**: Authenticate students using facial recognition
- **Student Registration**: Register new students with their details and face
- **Entry/Exit Logging**: Log entry and exit times for students
- **Student Information**: Display student details including name, roll number, hostel, room number, and contact
- **Activity Log**: View recent entry/exit activity for each student

## Requirements

- Python 3.6+
- Required libraries (install using `pip install -r requirements.txt`):
  - face_recognition
  - opencv-python
  - numpy
  - pillow

## Installation

1. Clone the repository or download the source code
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```

## Usage

### Main Screen

The main screen consists of two sections:
- **Left Section**: Camera feed and control buttons
- **Right Section**: Student information and activity log

### Controls

- **Start Camera**: Start the webcam feed for face recognition
- **Stop Camera**: Stop the webcam feed
- **Register New Student**: Open the registration screen
- **Log Entry**: Log an entry for the recognized student
- **Log Exit**: Log an exit for the recognized student

### Registration

To register a new student:
1. Click on "Register New Student"
2. The camera will start automatically, showing a live feed
3. Fill in the student details (Roll Number, Name, Hostel Name, Room Number, Contact Number)
4. Click "Capture Face" to take a photo
5. Click "Save" to register the student
6. Click "Cancel" to return to the main screen without registering

## Project Structure

- `main.py`: Main application entry point
- `database.py`: JSON-based data storage and operations
- `face_auth.py`: Face recognition and authentication logic
- `gui.py`: GUI interface for the application
- `utils.py`: Utility functions
- `requirements.txt`: Dependencies list

## How It Works

1. The system captures video from the webcam
2. Face detection is performed on each frame
3. If a face is detected, it is compared with the registered faces in the database
4. If a match is found, the student information is displayed
5. The user can then log entry or exit for the recognized student

## Notes

- The system uses a simple JSON file (`hostel_data.json`) to store student information and logs
- Face encodings are stored in the JSON file for recognition
- The system is designed for use at a hostel desk for monitoring student entry and exit
- All data is stored locally, making it suitable for small-scale deployments
