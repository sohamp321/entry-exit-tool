"""
Voice authentication module for hostel management system.
Provides fallback authentication when face recognition fails.
"""

import speech_recognition as sr
import pyttsx3
import threading
import time
import re
import tkinter as tk

# Import the voice recognition dialog
from voice_recognition_dialog import VoiceRecognitionDialog

class VoiceAuthenticator:
    def __init__(self, database):
        """Initialize the voice authenticator with a database connection"""
        self.database = database
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()

        # Configure voice properties
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

        # Get available voices
        voices = self.engine.getProperty('voices')
        # Set a female voice if available
        for voice in voices:
            if 'female' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

        # For thread safety
        self.speak_lock = threading.Lock()
        self.listen_lock = threading.Lock()

        # Patterns for recognition
        self.roll_pattern = re.compile(r'\b[a-zA-Z]\d{7}\b')  # e.g., B20CS001

    def speak(self, text):
        """Speak the given text"""
        with self.speak_lock:
            self.engine.say(text)
            self.engine.runAndWait()

    def listen(self, prompt=None, timeout=5, phrase_time_limit=5, root=None):
        """Listen for speech and convert to text with visual feedback"""
        if prompt:
            self.speak(prompt)

        # If no root window is provided, we can't show the dialog
        if root is None:
            return self._listen_without_dialog(timeout, phrase_time_limit)

        # Use the dialog for visual feedback
        result = [None]  # Use a list to store the result from the callback

        def recognition_callback(dialog):
            # Start a thread to perform the recognition
            threading.Thread(target=lambda: self._perform_recognition_with_dialog(
                dialog, timeout, phrase_time_limit, result
            ), daemon=True).start()

        # Show the dialog and wait for it to close
        VoiceRecognitionDialog.show_dialog(root, recognition_callback)

        # Return the result
        return result[0]

    def _listen_without_dialog(self, timeout, phrase_time_limit):
        """Listen for speech without visual feedback"""
        with self.listen_lock:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                try:
                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

                    # Convert speech to text
                    text = self.recognizer.recognize_google(audio)
                    return text.lower()
                except sr.WaitTimeoutError:
                    return None
                except sr.UnknownValueError:
                    return None
                except sr.RequestError:
                    return None

    def _perform_recognition_with_dialog(self, dialog, timeout, phrase_time_limit, result_container):
        """Perform speech recognition with visual feedback"""
        with self.listen_lock:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                dialog.update_recognition_text("Listening...")

                try:
                    # Configure the recognizer for continuous recognition
                    self.recognizer.pause_threshold = 0.8
                    self.recognizer.dynamic_energy_threshold = True

                    # Start listening
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

                    # Update dialog to show processing
                    dialog.update_recognition_text("Processing your speech...")

                    # Convert speech to text
                    text = self.recognizer.recognize_google(audio)
                    text_lower = text.lower()

                    # Update dialog with the recognized text
                    dialog.update_recognition_text(f"Recognized: {text}")

                    # Store the result
                    result_container[0] = text_lower

                    # Set the final result in the dialog
                    dialog.set_final_result(text_lower)

                except sr.WaitTimeoutError:
                    dialog.update_recognition_text("Timeout - no speech detected")
                    dialog.set_final_result(None)
                except sr.UnknownValueError:
                    dialog.update_recognition_text("Could not understand audio")
                    dialog.set_final_result(None)
                except sr.RequestError as e:
                    dialog.update_recognition_text(f"Error: {str(e)}")
                    dialog.set_final_result(None)
                except Exception as e:
                    dialog.update_recognition_text(f"Unexpected error: {str(e)}")
                    dialog.set_final_result(None)

    def authenticate_by_voice(self, root=None):
        """Authenticate a student by voice"""
        # First, ask for name or roll number
        self.speak("Face recognition failed. Please state your name or roll number for authentication.")

        # Try up to 3 times
        for attempt in range(3):
            response = self.listen(prompt=None if attempt > 0 else "Speak clearly after the beep.",
                                timeout=10, root=root)

            if not response:
                if attempt < 2:
                    self.speak("I didn't catch that. Please try again.")
                continue

            # Check if response contains a roll number
            roll_match = self.roll_pattern.search(response)
            if roll_match:
                roll_number = roll_match.group(0)
                student = self.database.get_student_by_roll_number(roll_number)
                if student:
                    self.speak(f"Authentication successful. Welcome, {student[2]}.")
                    return student
                else:
                    if attempt < 2:
                        self.speak(f"No student found with roll number {roll_number}. Please try again.")
            else:
                # Try to match by name
                # Get all students
                students = self.database.get_all_students()

                # Check if any student name is in the response
                for student in students:
                    # student format: (id, roll_number, name, hostel_name, room_number, contact_number)
                    name = student[2].lower()
                    if name in response:
                        self.speak(f"Authentication successful. Welcome, {student[2]}.")
                        return student

                if attempt < 2:
                    self.speak("I couldn't find your record. Please state your full name or roll number.")

        self.speak("Authentication failed. Please try again later or contact hostel administration.")
        return None

    def confirm_action(self, action, student_name):
        """Confirm an entry or exit action by voice"""
        confirmation = self.listen(f"Confirming {action} for {student_name}. Say yes to confirm or no to cancel.")

        if confirmation and ("yes" in confirmation or "confirm" in confirmation):
            self.speak(f"{action.capitalize()} confirmed.")
            return True
        else:
            self.speak("Action cancelled.")
            return False
