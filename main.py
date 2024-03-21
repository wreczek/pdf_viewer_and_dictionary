import os
from datetime import datetime

import pandas as pd
from flask import (
    jsonify, request, render_template, send_from_directory, url_for
)

from app.app_factory import create_app, login_manager
from app.files.file_manager import FileManager
from app.models import User
from app.word_manager.word_manager import WordManager
from utils import config

app = create_app()

WORDS_CSV_PATH = config.words_csv_path

word_manager = WordManager(WORDS_CSV_PATH)
file_manager = FileManager(app.upload_folder)


@login_manager.user_loader
def load_user(user_id):
    print(f'Loading user with ID: {user_id}')
    return User.query.get(int(user_id))


@app.route('/unfamiliar_words', methods=['GET', 'POST'])
def unfamiliar_words():
    csv_header, word_list = word_manager.read_and_process_csv()
    filtered_and_sorted_word_list = word_manager.apply_filters_and_sort(word_list)
    available_files = file_manager.get_available_files()

    return render_template('dictionary.html',
                           filtered_word_list=filtered_and_sorted_word_list,
                           available_files=available_files,
                           csv_header=csv_header,
                           active_page='unfamiliar_words')


@app.route('/unfamiliar_words', methods=['POST'])
def unfamiliar_words_partial():
    csv_header, word_list = word_manager.read_and_process_csv()
    filtered_and_sorted_word_list = word_manager.apply_filters_and_sort(word_list)

    # Render the table template with the filtered and sorted word list
    return render_template('dictionary_table.html',
                           filtered_word_list=filtered_and_sorted_word_list,
                           csv_header=csv_header)


@app.route('/pdf/<path:filename>')
def pdf(filename):
    return send_from_directory(app.upload_folder, filename)


@app.route('/file_list/<path:filename>')
def pdf_viewer(filename):
    pdf_path = url_for('pdf', filename=filename)

    # Retrieve the last stored position from localStorage
    last_position = request.cookies.get(f'last_position_{filename}')

    # Update access time
    file_path = os.path.join(app.upload_folder, filename)
    current_time = datetime.now().timestamp()

    # Update the access time of the file
    os.utime(file_path, (current_time, current_time))

    return render_template('pdf_viewer.html',
                           file_name=filename,
                           current_file=filename,
                           pdf_path=pdf_path,
                           last_position=last_position,  # Pass last_position to the template
                           active_page='pdf_viewer')


@app.route('/delete_word/<word_id>', methods=['DELETE'])
def delete_word(word_id):
    print(f"Received DELETE request for word ID: {word_id}")
    word_id = int(word_id)

    db_csv = pd.read_csv(WORDS_CSV_PATH)
    db_csv = db_csv.drop(db_csv[db_csv.id == word_id].index)
    db_csv.to_csv(WORDS_CSV_PATH, index=False)

    return jsonify({'message': 'Word deleted successfully', 'word_id': word_id})


@app.route('/get_updated_content')
def get_updated_content():
    updated_content = word_manager.fetch_updated_content(file_manager)
    return jsonify({'html': updated_content})


if __name__ == "__main__":
    app.run(debug=True)

#  TODO:
#   1. dodac archiwum? tam trafiaja usuniete slowa, a z archiwum mozna je juz usunac na zawsze
#   2. details button - dodac funkcjonalnosc z planu
#   3. być może apply filter nie powinien odświeżać całej strony tylko samą tabelkę?
#   4. ogarnac zmiany z 3 commitami wstecz (slim vs no slim, czemu nie dziala, co powinno dzialac)
#       commit 47e...
#   5. Dodac Word model, ORM i usuwanie dodawanie etc. przez ten model
#   6. Add list_words endpoint with pagination
#   7. Dodac informacje po nieudanym dodawaniu pliku dlaczego (np jpg)
#   8. Usuwanie plikow z listy Files (i moze jakies inne manipulacje?) np. archive
#   9. zastapic usuwanie przenoszeniem do kosza ...
