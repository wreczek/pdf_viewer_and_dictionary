import os
import csv

from flask import Flask, render_template, send_from_directory, send_file, url_for, request

from utils import get_status, get_upload_date, get_access_date

app = Flask(__name__)

UPLOAD_FOLDER = "./documents"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    pdf_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.pdf')]

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

    return render_template('home.html', pdf_files_info=pdf_files_info)


@app.route('/pdf_viewer')
def pdf_viewer_home():
    return index()


@app.route('/unfamiliar_words')
def unfamiliar_words():
    with open('./db/unfamiliar_words.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        word_list = list(reader)

    return render_template('unfamiliar_words.html', word_list=word_list)


@app.route('/pdf_viewer/<path:filename>')
def pdf_viewer(filename):
    return render_template('pdf_viewer.html', file_name=filename)


@app.route('/pdf/<path:filename>')
def pdf(filename):
    return send_file(os.path.join(app.root_path, 'documents', filename))
