import tkinter as tk
from database import HostelDatabase
from face_auth import FaceAuthenticator
from gui import HostelAuthGUI
import sys
import os

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import face_recognition
        import cv2
        import numpy
        import PIL
    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print("Please install all required dependencies using:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main function to run the application"""
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize database
    db = HostelDatabase()
    
    # Initialize face authenticator
    face_auth = FaceAuthenticator(db)
    
    # Create GUI
    root = tk.Tk()
    app = HostelAuthGUI(root, face_auth, db)
    
    # Set up closing handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
