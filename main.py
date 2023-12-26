import os
import csv

from flask import Flask, render_template, send_from_directory, send_file, url_for, request, redirect

from config import load_config
from utils import get_status, get_upload_date, get_access_date, get_available_files, apply_filters

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
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        csv_header, *word_list = list(reader)

    available_files = get_available_files()

    selected_file = request.form.get('file', '')
    selected_date = request.form.get('date', '')
    selected_difficulty = request.form.get('difficulty', '')

    filtered_word_list = apply_filters(word_list, selected_file, selected_date, selected_difficulty)

    return render_template('unfamiliar_words.html',
                           filtered_word_list=filtered_word_list,
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
    return render_template('pdf_viewer.html',
                           file_name=filename,
                           current_file=filename,
                           pdf_path=pdf_path,
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
