import pandas as pd
from flask import render_template, jsonify

from app.files import file_manager
from app.words import word_manager, words_bp, config


@words_bp.route('/unfamiliar_words', methods=['GET', 'POST'])
def unfamiliar_words():
    csv_header, word_list = word_manager.read_and_process_csv()
    filtered_and_sorted_word_list = word_manager.apply_filters_and_sort(word_list)
    available_files = file_manager.get_available_files(config.upload_folder)

    return render_template('dictionary.html',
                           filtered_word_list=filtered_and_sorted_word_list,
                           available_files=available_files,
                           csv_header=csv_header,
                           active_page='unfamiliar_words')


@words_bp.route('/unfamiliar_words', methods=['POST'])
def unfamiliar_words_partial():  # TODO: unused
    csv_header, word_list = word_manager.read_and_process_csv()
    filtered_and_sorted_word_list = word_manager.apply_filters_and_sort(word_list)

    # Render the table template with the filtered and sorted word list
    return render_template('dictionary_table.html',
                           filtered_word_list=filtered_and_sorted_word_list,
                           csv_header=csv_header)


@words_bp.route('/delete_word/<word_id>', methods=['DELETE'])
def delete_word(word_id):
    print(f"Received DELETE request for word ID: {word_id}")
    word_id = int(word_id)

    csv_path = config.words_csv_path
    db_csv = pd.read_csv(csv_path)
    db_csv = db_csv.drop(db_csv[db_csv.id == word_id].index)
    db_csv.to_csv(csv_path, index=False)

    return jsonify({'message': 'Word deleted successfully', 'word_id': word_id})


@words_bp.route('/get_updated_content')
def get_updated_content():
    updated_content = word_manager.fetch_updated_content(file_manager)
    return jsonify({'html': updated_content})
