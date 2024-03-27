import csv

from dateutil.parser import parse
from flask import request, render_template

from utils import map_difficulty, config


class WordManager:
    def __init__(self, csv_path):
        self.csv_path = csv_path

    def read_and_process_csv(self):
        """Reads the CSV file, parses dates, and returns the processed word list."""
        csv_header, word_list = self.read_csv(self.csv_path)

        enriched_word_list = self.enrich_word_data_with_formatted_dates(word_list)

        return csv_header, enriched_word_list

    @staticmethod
    def read_csv(csv_path):
        with open(csv_path, encoding='utf-8') as f:
            csv_header, *word_list = list(csv.reader(f))
        return csv_header, word_list

    def enrich_word_data_with_formatted_dates(self, word_list):
        """Processes a list of words, extracting information and formatting dates.

        Args:
            word_list: A list of lists, where each inner list represents a word
                with its details.

        Returns:
            A new list of lists containing the processed words with potentially
            formatted dates.
        """

        return [
            [*inner_list[:3], self.parse_and_format_date(inner_list[3]), *inner_list[4:]]
            if inner_list and len(inner_list) >= 4 else inner_list
            for inner_list in word_list
        ]

    def apply_filters_and_sort(self, word_list):
        selected_file, selected_date, selected_difficulty, sort_by, is_reversed = \
            self.get_filter_values()
        filtered_word_list = self.apply_filters(word_list, selected_file, selected_date,
                                                selected_difficulty)
        filtered_and_sorted_word_list = self.sort_records(sort_by, is_reversed, filtered_word_list)
        return filtered_and_sorted_word_list

    @staticmethod
    def get_filter_values():
        selected_file = request.form.get('file', '')
        selected_date = request.form.get('date', '')
        selected_difficulty = request.form.get('difficulty', '')
        sort_by = request.form.get('sort_by', '-1')
        is_reversed = request.form.get('reverse_sort', 'False')
        return selected_file, selected_date, selected_difficulty, sort_by, is_reversed

    def apply_filters(self, word_list, selected_file, selected_date, selected_difficulty):
        filtered_list = self.filter_list(word_list, selected_file, 2)
        filtered_list = self.filter_list(filtered_list, selected_date, 3,
                                         func=self.parse_and_format_date)
        filtered_list = self.filter_list(filtered_list, selected_difficulty, 4, func=map_difficulty)
        return filtered_list

    @staticmethod
    def filter_list(values, filter_, index, func=lambda x: x):
        if not filter_:
            return values
        return [word for word in values if func(word[index]) == filter_]

    @staticmethod
    def parse_and_format_date(date_str):
        return parse(date_str).strftime('%Y-%m-%d')

    @staticmethod
    def sort_records(sort_by, is_reversed,
                     filtered_word_list):  # todo: nie pamietam ale cos trzeba zrobic
        if sort_by == '-1':
            return filtered_word_list

        _is_reversed = is_reversed == 'on'
        return sorted(filtered_word_list, key=lambda x: x[int(sort_by)].lower(),
                      reverse=_is_reversed)

    def delete_word(self, word_id):
        """TODO: Existing logic for deleting a word from the CSV using pandas"""

    def fetch_updated_content(self, file_manager):
        csv_header, word_list = self.read_and_process_csv()
        filtered_and_sorted_word_list = self.apply_filters_and_sort(word_list)
        available_files = file_manager.get_available_files(config.upload_folder)

        updated_content = render_template('dictionary_table.html',
                                          filtered_word_list=filtered_and_sorted_word_list,
                                          available_files=available_files,
                                          csv_header=csv_header,
                                          active_page='unfamiliar_words')

        return updated_content
