import os
import csv

from flask import Flask, render_template, send_from_directory, send_file, url_for, request

app = Flask(__name__)

UPLOAD_FOLDER = "./documents"  # change this to the path of your upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    # Get a list of all the PDF files in the upload folder
    pdf_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.pdf')]
    # Render the home.html template with the list of PDF files
    return render_template('home.html', pdf_files=pdf_files)


@app.route('/unfamiliar_words')
def unfamiliar_words():
    # Read the CSV file with the unfamiliar words and their translations
    with open('./db/unfamiliar_words.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        word_list = list(reader)

    # Render the unfamiliar_words.html template with the list of unfamiliar words
    return render_template('unfamiliar_words.html', word_list=word_list)


@app.route('/pdf_viewer/<path:filename>')
def pdf_viewer(filename):
    # Render the PDF viewer template with the current file variable
    return render_template('pdf_viewer.html', file_name=filename)


# # TODO: wyswietla sam pdf, chcemy pdf z barem
# @app.route('/files/<path:filename>')
# def files(filename):
#     """Serve a PDF file from the pdf directory."""
#     # pdf_dir = os.path.join(app.root_path, 'static', 'pdf')
#     pdf_dir = os.path.join(app.root_path, 'documents')
#     return send_from_directory(pdf_dir, filename, as_attachment=False)


@app.route('/pdf/<path:filename>')
def pdf(filename):
    return send_file(os.path.join(app.root_path, 'documents', filename))
