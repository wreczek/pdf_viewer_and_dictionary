import os
import csv

import pandas as pd
from flask import Flask, render_template, send_from_directory, url_for, request, \
    redirect, jsonify

from config import load_config
from utils import get_status, get_upload_date, get_access_date, get_available_files, \
    apply_filters, sort_records

app = Flask(__name__)

config = load_config()

UPLOAD_FOLDER = config.upload_folder
DB_PATH = config.db_path

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template("home.html",
                           active_page='index')


@app.route('/pdf_viewer')
def pdf_viewer_home():
    pdf_files = get_available_files()

    pdf_files_info = []

    for pdf_file in pdf_files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file)
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
                           active_page='pdf_viewer_home')


@app.route('/unfamiliar_words', methods=['GET', 'POST'])
def unfamiliar_words():
    with open(DB_PATH, encoding='utf-8') as f:
        reader = csv.reader(f)
        csv_header, *word_list = list(reader)

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


@app.route('/pdf/<path:filename>')
def pdf(filename):
    directory = os.path.join(app.root_path, 'documents')
    return send_from_directory(directory, filename)


@app.route('/pdf_viewer/<path:filename>')
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
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            return redirect(url_for('index'))

    return render_template('upload.html',
                           active_page='upload_file')


@app.route('/delete_word/<word_id>', methods=['DELETE'])
def delete_word(word_id):
    print(f"Received DELETE request for word ID: {word_id}")
    word_id = int(word_id)

    db_csv = pd.read_csv(DB_PATH)
    db_csv = db_csv.drop(db_csv[db_csv.id == word_id].index)
    db_csv.to_csv(DB_PATH, index=False)

    return jsonify({'message': 'Word deleted successfully', 'word_id': word_id})


@app.route('/get_updated_content')
def get_updated_content():
    # Fetch and serialize the updated content as JSON
    updated_content = fetch_updated_content()

    # Assuming fetch_updated_content returns a dictionary with an 'html' key
    return jsonify({'html': updated_content})


# This function should return the HTML content you want to update
def fetch_updated_content():
    # Similar to the logic in your 'unfamiliar_words' route
    with open(DB_PATH, encoding='utf-8') as f:
        reader = csv.reader(f)
        csv_header, *word_list = list(reader)

    selected_file = request.form.get('file', '')
    selected_date = request.form.get('date', '')
    selected_difficulty = request.form.get('difficulty', '')
    sort_by = request.form.get('sort_by', '-1')
    is_reversed = request.form.get('reverse_sort', 'False')

    filtered_word_list = apply_filters(word_list, selected_file, selected_date, selected_difficulty)
    filtered_and_sorted_word_list = sort_records(sort_by, is_reversed, filtered_word_list)

    available_files = get_available_files()

    # Render the template and return the HTML content
    updated_content = render_template('dictionary_table.html',
                                      filtered_word_list=filtered_and_sorted_word_list,
                                      available_files=available_files,
                                      csv_header=csv_header,
                                      active_page='unfamiliar_words')

    return updated_content
