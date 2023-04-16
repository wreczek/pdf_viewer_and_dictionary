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
    # Render the index.html template with the list of PDF files
    return render_template('index.html', pdf_files=pdf_files)


# @app.route('/unfamiliar_words')
# def unfamiliar_words():
#     # Read the CSV file with the unfamiliar words and their translations
#     with open('./db/unfamiliar_words.csv', 'r', encoding='utf-8') as f:
#         reader = csv.reader(f)
#         word_list = list(reader)
#
#     # Render the unfamiliar_words.html template with the list of unfamiliar words
#     return render_template('unfamiliar_words.html', word_list=word_list)


@app.route('/unfamiliar_words')
def unfamiliar_words():
    word_list = [
        ['Word 1', 'Translation 1', 'Book 1', 'Difficulty 1'],
        ['Word 2', 'Translation 2', 'Book 2', 'Difficulty 2'],
        ['Word 3', 'Translation 3', 'Book 3', 'Difficulty 3'],
        ['Word 4', 'Translation 4', 'Book 4', 'Difficulty 4']
    ]
    pdf_url = None
    if 'pdf' in request.args:
        pdf_url = url_for('pdf', path=request.args['pdf'])
    return render_template('unfamiliar_words.html', word_list=word_list, pdf_url=pdf_url)


# TODO: wyswietla tylko bar
@app.route('/viewer/<filename>')
def pdf_viewer(filename):
    # Set the current file variable to the filename
    current_file = filename
    # Render the PDF viewer template with the current file variable
    return render_template('pdf_viewer.html', current_file=current_file)


# TODO: wyswietla bar + filename, ale zamiast pdf-a jest NOT FOUND
@app.route('/test/<filename>')
def test_pdf(filename):
    return render_template('file.html', file_name=filename)


# TODO: wyswietla sam pdf, chcemy pdf z barem
@app.route('/files/<path:filename>')
def pdf(filename):
    """Serve a PDF file from the pdf directory."""
    # pdf_dir = os.path.join(app.root_path, 'static', 'pdf')
    pdf_dir = os.path.join(app.root_path, 'documents')
    return send_from_directory(pdf_dir, filename, as_attachment=False)


# TODO: wyswietla bar + filename, ale zamiast pdf-a jest NOT FOUND
@app.route('/later/<filename>')
def later(filename):
    return render_template('base.html', pdf_url=filename)
