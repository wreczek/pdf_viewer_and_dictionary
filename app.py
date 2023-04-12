import os
import csv

from flask import Flask, render_template

app = Flask(__name__)

UPLOAD_FOLDER = "./documents"  # change this to the path of your upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    # Get a list of all the PDF files in the upload folder
    pdf_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.pdf')]
    # Render the index.html template with the list of PDF files
    return render_template('index.html', pdf_files=pdf_files)


@app.route('/unfamiliar_words')
def unfamiliar_words():
    # Read the CSV file with the unfamiliar words and their translations
    with open('./db/unfamiliar_words.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        word_list = list(reader)

    # Render the unfamiliar_words.html template with the list of unfamiliar words
    return render_template('unfamiliar_words.html', word_list=word_list)


@app.route('/pdf/<filename>')
def pdf_viewer(filename):
    # Set the current file variable to the filename
    current_file = filename
    # Render the PDF viewer template with the current file variable
    return render_template('pdf_viewer.html', current_file=current_file)
