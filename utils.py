import os
from datetime import datetime


def get_status(file_path):
    # You might have a function to calculate the status based on the file content or user progress
    # For now, let's use a placeholder.
    return "Placeholder Status"


def get_upload_date(file_path):
    try:
        # Get the creation time of the file
        creation_time = os.path.getctime(file_path)
        # Convert the timestamp to a readable format
        upload_date = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
        return upload_date
    except Exception as e:
        # Handle exceptions (e.g., file not found, permission issues)
        print(f"Error getting upload date: {e}")
        return None


def get_access_date(file_path):
    try:
        # Get the last access time of the file
        access_time = os.path.getatime(file_path)
        # Convert the timestamp to a readable format
        upload_date = datetime.fromtimestamp(access_time).strftime("%Y-%m-%d %H:%M:%S")
        return upload_date
    except Exception as e:
        # Handle exceptions (e.g., file not found, permission issues)
        print(f"Error getting upload date: {e}")
        return None
