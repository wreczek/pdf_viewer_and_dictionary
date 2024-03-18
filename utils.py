import os
from datetime import datetime

from config import load_config

config = load_config()


def get_status(file_path):
    """TODO"""
    # You might have a function to calculate the status based on the file content or user progress
    # For now, let's use a placeholder.
    return "Placeholder Status"


def get_upload_date(file_path):
    try:
        creation_time = os.path.getctime(file_path)
        upload_date = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
        return upload_date
    except Exception as e:
        # Handle exceptions (e.g., file not found, permission issues)
        print(f"Error getting upload date: {e}")
        return None


def get_access_date(file_path):
    try:
        access_time = os.path.getatime(file_path)
        upload_date = datetime.fromtimestamp(access_time).strftime("%Y-%m-%d %H:%M:%S")
        return upload_date
    except Exception as e:
        # Handle exceptions (e.g., file not found, permission issues)
        print(f"Error getting upload date: {e}")
        return None


def map_difficulty(difficulty):
    difficulty_mapping = {
        "1": "easy",
        "2": "easy",
        "3": "easy",
        "4": "medium",
        "5": "medium",
        "6": "medium",
        "7": "medium",
        "8": "hard",
        "9": "hard",
        "10": "hard"
    }
    return difficulty_mapping.get(difficulty, difficulty)
