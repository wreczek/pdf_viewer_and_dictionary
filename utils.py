from config import load_config

config = load_config()


def get_status(file_path):
    """TODO"""
    # You might have a function to calculate the status based on the file content or user progress
    # For now, let's use a placeholder.
    return "Placeholder Status"


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
