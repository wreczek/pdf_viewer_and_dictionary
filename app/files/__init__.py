from flask import Blueprint

from app.files.file_manager import FileManager
from utils import config

files_bp = Blueprint('files', __name__, template_folder='templates')

file_manager = FileManager(config.upload_folder, config.archive_folder)
