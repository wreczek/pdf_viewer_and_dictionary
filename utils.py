import os
from datetime import datetime
from dateutil.parser import parse

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


def get_available_files():
    pdf_files = [f for f in os.listdir(config.upload_folder) if f.endswith('.pdf')]

    return pdf_files


def apply_filters(word_list, selected_file, selected_date, selected_difficulty):
    filtered_list = word_list

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

    def map_difficulty(difficulty):
        return difficulty_mapping.get(difficulty, difficulty)

    def filter_list(values, filter_, index, func=lambda x: x):
        if not filter_:
            return values

        return [word
                for word in values
                if func(word[index]) == filter_]

    filtered_list = filter_list(filtered_list, selected_file, 2)
    filtered_list = filter_list(filtered_list, selected_date, 3,
                                lambda x: parse(x).strftime('%Y-%m-%d'))
    filtered_list = filter_list(filtered_list, selected_difficulty, 4,
                                lambda x: map_difficulty(x))

    return filtered_list


def sort_records(sort_by, is_reversed, filtered_word_list):
    if is_reversed == 'on':
        is_reversed = True
    else:
        is_reversed = False

    if sort_by == '-1':
        filtered_and_sorted_word_list = filtered_word_list
    else:
        filtered_and_sorted_word_list = sorted(filtered_word_list,
                                               key=lambda x: x[int(sort_by)].lower(),
                                               reverse=is_reversed)
    return filtered_and_sorted_word_list
