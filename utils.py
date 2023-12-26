import os
from datetime import datetime
import yaml
from dateutil.parser import parse


with open("env/main.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)


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
    upload_folder = config.get("UPLOAD_FOLDER", "documents")
    pdf_files = [f for f in os.listdir(upload_folder) if f.endswith('.pdf')]  # todo: env

    return pdf_files


def apply_filters(word_list, selected_file, selected_date, selected_difficulty):
    filtered_list = word_list

    def filter_list(values, filter_, index, func=lambda x: x):
        if filter_:
            return [word
                    for word in values
                    if func(word[index]) == filter_]
        return values

    filtered_list = filter_list(filtered_list, selected_file, 2)
    filtered_list = filter_list(filtered_list, selected_date, 3, lambda x: parse(x).strftime('%Y-%m-%d'))
    filtered_list = filter_list(filtered_list, selected_difficulty, 4)

    return filtered_list
