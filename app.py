import os
import csv

from flask import Flask, render_template, send_from_directory, send_file, url_for, request

app = Flask(__name__)

UPLOAD_FOLDER = "./documents"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    pdf_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.pdf')]
    return render_template('home.html', pdf_files=pdf_files)


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
