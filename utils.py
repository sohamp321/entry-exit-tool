import os
import cv2
import datetime

def ensure_directory_exists(directory):
    """Ensure that a directory exists, create it if it doesn't"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_image(image, directory, filename=None):
    """Save an image to a directory"""
    ensure_directory_exists(directory)
    
    if filename is None:
        # Generate a filename based on timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.jpg"
    
    filepath = os.path.join(directory, filename)
    cv2.imwrite(filepath, image)
    
    return filepath

def resize_image(image, width=None, height=None):
    """Resize an image while maintaining aspect ratio"""
    # Get original dimensions
    (h, w) = image.shape[:2]
    
    # If both width and height are None, return original image
    if width is None and height is None:
        return image
    
    # Calculate aspect ratio
    if width is None:
        # Calculate width based on height
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        # Calculate height based on width
        r = width / float(w)
        dim = (width, int(h * r))
    
    # Resize the image
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    
    return resized

def draw_text(image, text, position, font_scale=0.7, color=(0, 255, 0), thickness=2):
    """Draw text on an image"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, text, position, font, font_scale, color, thickness)
    
    return image

def format_timestamp(timestamp_str):
    """Format a timestamp string for display"""
    try:
        dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %Y %I:%M %p")
    except ValueError:
        return timestamp_str

def get_time_difference(timestamp1, timestamp2):
    """Get the time difference between two timestamps in hours and minutes"""
    try:
        dt1 = datetime.datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S")
        dt2 = datetime.datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
        
        # Calculate difference in seconds
        diff_seconds = abs((dt2 - dt1).total_seconds())
        
        # Convert to hours and minutes
        hours = int(diff_seconds // 3600)
        minutes = int((diff_seconds % 3600) // 60)
        
        return f"{hours}h {minutes}m"
    except ValueError:
        return "Unknown"
