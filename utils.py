import csv
import os
from datetime import datetime

from dateutil.parser import parse
from flask import request

from config import load_config

config = load_config()


def get_status(file_path):
    """TODO"""
    # You might have a function to calculate the status based on the file content or user progress
    # For now, let's use a placeholder.
    return "Placeholder Status"


def read_and_process_csv(csv_path):
    """Reads the CSV file, parses dates, and returns the processed word list."""
    csv_header, word_list = read_csv(csv_path)

    enriched_word_list = enrich_word_data_with_formatted_dates(word_list)

    return csv_header, enriched_word_list


def read_csv(csv_path):
    with open(csv_path, encoding='utf-8') as f:
        csv_header, *word_list = list(csv.reader(f))
    return csv_header, word_list


def enrich_word_data_with_formatted_dates(word_list):
    """Processes a list of words, extracting information and formatting dates.

    Args:
        word_list: A list of lists, where each inner list represents a word
            with its details.

    Returns:
        A new list of lists containing the processed words with potentially
        formatted dates.
    """

    return [
        [*inner_list[:3], parse_and_format_date(inner_list[3]), *inner_list[4:]]
        if inner_list and len(inner_list) >= 4 else inner_list
        for inner_list in word_list
    ]


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


def parse_and_format_date(date_str):
    return parse(date_str).strftime('%Y-%m-%d')


def filter_list(values, filter_, index, func=lambda x: x):
    if not filter_:
        return values
    return [word for word in values if func(word[index]) == filter_]


def apply_filters(word_list, selected_file, selected_date, selected_difficulty):
    filtered_list = filter_list(word_list, selected_file, 2)
    filtered_list = filter_list(filtered_list, selected_date, 3, func=parse_and_format_date)
    filtered_list = filter_list(filtered_list, selected_difficulty, 4, func=map_difficulty)
    return filtered_list


def sort_records(sort_by, is_reversed, filtered_word_list):#todo
    if sort_by == '-1':
        return filtered_word_list

    _is_reversed = is_reversed == 'on'
    return sorted(filtered_word_list, key=lambda x: x[int(sort_by)].lower(), reverse=_is_reversed)


def get_filter_values():
    selected_file = request.form.get('file', '')
    selected_date = request.form.get('date', '')
    selected_difficulty = request.form.get('difficulty', '')
    sort_by = request.form.get('sort_by', '-1')
    is_reversed = request.form.get('reverse_sort', 'False')
    return selected_file, selected_date, selected_difficulty, sort_by, is_reversed


def apply_filters_and_sort(word_list):
    selected_file, selected_date, selected_difficulty, sort_by, is_reversed = get_filter_values()
    filtered_word_list = apply_filters(word_list, selected_file, selected_date, selected_difficulty)
    filtered_and_sorted_word_list = sort_records(sort_by, is_reversed, filtered_word_list)
    return filtered_and_sorted_word_list
