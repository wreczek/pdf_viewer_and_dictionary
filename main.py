import csv
import os

import pandas as pd
from flask import (
    jsonify, redirect, request, render_template, send_from_directory, url_for, flash
)
from werkzeug.utils import secure_filename

from app.app_factory import create_app, login_manager
from app.models import User
from utils import (
    apply_filters, get_access_date, get_available_files, get_status, get_upload_date, sort_records,
    parse_and_format_date, config
)

app = create_app()

WORDS_CSV_PATH = config.words_csv_path

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    print(f'Loading user with ID: {user_id}')
    return User.query.get(int(user_id))


@app.route('/')  # TODO: usunac bo blueprint
def index():
    return render_template("home.html", active_page='index')


@app.route('/unfamiliar_words', methods=['GET', 'POST'])
def unfamiliar_words():
    with open(WORDS_CSV_PATH, encoding='utf-8') as f:
        csv_header, *word_list = list(csv.reader(f))

    word_list = [
        [*inner_list[:3], parse_and_format_date(inner_list[3]), *inner_list[4:]]
        if inner_list and len(inner_list) >= 4 else inner_list
        for inner_list in word_list]

    selected_file = request.form.get('file', '')
    selected_date = request.form.get('date', '')
    selected_difficulty = request.form.get('difficulty', '')
    sort_by = request.form.get('sort_by', '-1')
    is_reversed = request.form.get('reverse_sort', 'False')

    filtered_word_list = apply_filters(word_list, selected_file, selected_date, selected_difficulty)
    filtered_and_sorted_word_list = sort_records(sort_by, is_reversed, filtered_word_list)
    available_files = get_available_files()

    return render_template('dictionary.html',
                           filtered_word_list=filtered_and_sorted_word_list,
                           available_files=available_files,
                           csv_header=csv_header,
                           active_page='unfamiliar_words')


@app.route('/unfamiliar_words', methods=['POST'])
def unfamiliar_words_partial():
    with open(WORDS_CSV_PATH, encoding='utf-8') as f:
        csv_header, *word_list = list(csv.reader(f))

    selected_file = request.form.get('file', '')
    selected_date = request.form.get('date', '')
    selected_difficulty = request.form.get('difficulty', '')
    sort_by = request.form.get('sort_by', '-1')
    is_reversed = request.form.get('reverse_sort', 'False')

    filtered_word_list = apply_filters(word_list, selected_file, selected_date, selected_difficulty)
    filtered_and_sorted_word_list = sort_records(sort_by, is_reversed, filtered_word_list)

    # Render the table template with the filtered and sorted word list
    return render_template('dictionary_table.html',
                           filtered_word_list=filtered_and_sorted_word_list,
                           csv_header=csv_header)


@app.route('/pdf/<path:filename>')
def pdf(filename):
    return send_from_directory(app.upload_folder, filename)


@app.route('/file_list')
def file_list():
    pdf_files_info = []

    for pdf_file in get_available_files():
        file_path = os.path.join(app.upload_folder, pdf_file)
        status = get_status(file_path)
        upload_date = get_upload_date(file_path)
        access_date = get_access_date(file_path)

        pdf_files_info.append({
            'name': pdf_file,
            'upload_date': upload_date,
            'access_date': access_date,
            'status': status
        })

    pdf_files_info.sort(key=lambda x: x['access_date'], reverse=True)

    return render_template('file_list.html',
                           pdf_files_info=pdf_files_info,
                           active_page='file_list')


@app.route('/file_list/<path:filename>')
def pdf_viewer(filename):
    pdf_path = url_for('pdf', filename=filename)

    # Retrieve the last stored position from localStorage
    last_position = request.cookies.get(f'last_position_{filename}')

    return render_template('pdf_viewer.html',
                           file_name=filename,
                           current_file=filename,
                           pdf_path=pdf_path,
                           last_position=last_position,  # Pass last_position to the template
                           active_page='pdf_viewer')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            try:
                filename = secure_filename(file.filename)
                if allowed_file(filename):
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('File type is not allowed.', 'danger')
                    return redirect(request.url)
            except Exception as e:
                flash(str(e), 'danger')
                return redirect(request.url)
            flash('File successfully uploaded!', 'success')
            return redirect(url_for('file_list'))
        else:
            flash('No selected file.', 'danger')
            return redirect(request.url)
    return render_template('upload.html', active_page='upload_file')


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
    updated_content = fetch_updated_content()
    return jsonify({'html': updated_content})


def fetch_updated_content():
    with open(WORDS_CSV_PATH, encoding='utf-8') as f:
        csv_header, *word_list = list(csv.reader(f))

    selected_file = request.form.get('file', '')
    selected_date = request.form.get('date', '')
    selected_difficulty = request.form.get('difficulty', '')
    sort_by = request.form.get('sort_by', '-1')
    is_reversed = request.form.get('reverse_sort', 'False')

    filtered_word_list = apply_filters(word_list, selected_file, selected_date, selected_difficulty)
    filtered_and_sorted_word_list = sort_records(sort_by, is_reversed, filtered_word_list)
    available_files = get_available_files()

    updated_content = render_template('dictionary_table.html',
                                      filtered_word_list=filtered_and_sorted_word_list,
                                      available_files=available_files,
                                      csv_header=csv_header,
                                      active_page='unfamiliar_words')

    return updated_content


if __name__ == "__main__":
    app.run(debug=True)

#  TODO: 1. upload date to inna data (wydaje sie ze access date przy uploadzie jest ok)
#   2. dodac archiwum? tam trafiaja usuniete slowa, a z archiwum mozna je juz usunac na zawsze
#   3. naprawić details przycisk
#   4. być może apply filter nie powinien odświeżać całej strony tylko samą tabelkę?
#   5. ogarnac zmiany z 3 commitami wstecz (slim vs no slim, czemu nie dziala, co powinno dzialac)
#       commit 47e...
#   6. Dodac Word model, ORM i usuwanie dodawanie etc. przez ten model
#   7. Add list_words endpoint with pagination
#   8. Dodac informacje po nieudanym dodawaniu pliku dlaczego (np jpg)
#   9. Usuwanie plikow z listy Files (i moze jakies inne manipulacje?)
