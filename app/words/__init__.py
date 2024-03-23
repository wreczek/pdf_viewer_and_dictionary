from flask import Blueprint

from app.words.word_manager import WordManager
from utils import config

words_bp = Blueprint('words', __name__, template_folder='templates')

word_manager = WordManager(config.words_csv_path)
