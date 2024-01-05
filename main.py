import os
import csv

from flask import (
    flash, Flask, jsonify, redirect, request, render_template, send_from_directory, url_for
)
from flask_login import (
    current_user, login_required, login_user, logout_user, LoginManager, UserMixin
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
import pandas as pd
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from werkzeug.security import check_password_hash, generate_password_hash

from config import load_config
from utils import (
    apply_filters, get_access_date, get_available_files, get_status, get_upload_date, sort_records
)

app = Flask(__name__)
config = load_config()

UPLOAD_FOLDER = config.upload_folder
WORDS_CSV_PATH = config.words_csv_path

app.config['SECRET_KEY'] = 'your_secret_key'  # TODO: Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    print(f'Loading user with ID: {user_id}')
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@app.route('/')
def index():
    return render_template("home.html", active_page='index')


@app.route('/pdf_viewer')
def pdf_viewer_home():
    pdf_files_info = []

    for pdf_file in get_available_files():
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

    return render_template('dictionary.html',
                           filtered_word_list=filtered_and_sorted_word_list,
                           available_files=available_files,
                           csv_header=csv_header,
                           active_page='unfamiliar_words')


@app.route('/pdf/<path:filename>')
def pdf(filename):
    return send_from_directory(os.path.join(app.root_path, 'documents'), filename)


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
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            return redirect(url_for('pdf_viewer_home'))
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            print(f'User ID after login: {user.id}')
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',
                           current_user_id=current_user.id)


if __name__ == "__main__":
    app.run(debug=True)

#  TODO: 1. upload date to inna data (wydaje sie ze access date przy uploadzie jest ok)
#   2. po uploadzie powinno albo pozostac na tej samej stronie albo przejsc to listy plikow
#   3. login/logout/profil w bar.html
