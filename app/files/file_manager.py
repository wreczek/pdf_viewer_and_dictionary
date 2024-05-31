import json
import logging
import os
import shutil
from datetime import datetime

import send2trash
from werkzeug.utils import secure_filename
from win32_setctime import setctime

from utils import config

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class FileManager:
    def __init__(self, upload_folder, archive_folder, max_file_size=config.max_size):
        self.uploader = FileUploader(upload_folder, max_file_size)
        self.lister = FileLister(upload_folder, archive_folder)
        self.deleter = FileDeleter(upload_folder, archive_folder)
        self.archiver = FileArchiver(upload_folder, archive_folder)

    # Facade methods for backward compatibility or simplified access
    def upload_files(self, files):
        return self.uploader.upload_files(files)

    def list_uploaded_files(self):
        return self.lister.list_files('upload')

    def list_archived_files(self):
        return self.lister.list_files('archive')

    def delete_file(self, filename, permanent=False):
        return self.deleter.delete_file(filename, permanent)

    def archive_file(self, filename):
        return self.archiver.archive_file(filename)

    def restore_file(self, filename):
        return self.archiver.restore_file(filename)


class FileUploader:
    def __init__(self, upload_folder, max_file_size):
        self.upload_folder = upload_folder
        self.max_file_size = max_file_size

    def upload_files(self, files):
        uploaded_files = []
        for file in files:
            if file.filename == '':
                continue
            filename = secure_filename(file.filename)

            if not self.allowed_file(filename):
                return {'message': f"File type of {filename} is not allowed.", 'error': True}

            if file.content_length > self.max_file_size:
                return {'message': f"File size of {filename} exceeds the maximum limit.", 'error': True}

            file_path = os.path.join(self.upload_folder, filename)
            file.save(file_path)
            uploaded_files.append(filename)

        if uploaded_files:
            return {'message': f"Files successfully uploaded: {', '.join(uploaded_files)}", 'success': True}
        else:
            return {'message': "No files were uploaded.", 'error': True}

    @staticmethod
    def update_file_creation_date(file_path):
        current_time = datetime.now().timestamp()
        setctime(file_path, current_time)

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class FileLister:
    def __init__(self, upload_folder, archive_folder):
        self.upload_folder = upload_folder
        self.archive_folder = archive_folder

    def list_files(self, folder_type, extension=None):
        """
        Lists files in the specified folder, optionally filtering by extension.

        Args:
            folder_type (str): 'upload' or 'archive' to specify the folder.
            extension (str, optional): Filter files by this extension. Include the dot, e.g., '.pdf'.

        Returns:
            list[dict]: List of dictionaries with file information.
        """
        path = self.upload_folder if folder_type == 'upload' else self.archive_folder
        return [self.get_file_info(os.path.join(path, filename)) for filename in
                self.get_available_files(path, extension)]

    @staticmethod
    def get_available_files(path, extension=None):
        """
        Get available files in the specified path, optionally filtered by an extension.

        Args:
            path (str): Path to the directory to list files from.
            extension (str, optional): File extension to filter by.

        Returns:
            list[str]: List of filenames.
        """
        files = os.listdir(path)
        if extension:
            return [f for f in files if f.endswith(extension)]
        return files

    @staticmethod
    def get_file_info(file_path):
        """
        Retrieves basic information about a file.

        Args:
            file_path (str): Path to the file.

        Returns:
            dict: Dictionary containing the file's name and upload date.
        """
        try:
            creation_time = os.path.getctime(file_path)
            upload_date = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logging.error(f"Error getting information for file {file_path}: {e}")
            upload_date = "Unknown"
        return {
            'name': os.path.basename(file_path),
            'path': file_path,
            'upload_date': upload_date
        }

    @staticmethod
    def get_upload_date(file_path):
        try:
            creation_time = os.path.getctime(file_path)
            return datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logging.error(f"Error getting upload date for {file_path}: {e}")
            return "Unknown"

    @staticmethod
    def get_access_date(file_path):
        try:
            access_time = os.path.getatime(file_path)
            access_date = datetime.fromtimestamp(access_time).strftime("%Y-%m-%d %H:%M:%S")
            return access_date
        except Exception as e:
            print(f"Error getting access date: {e}")
            return None

    @staticmethod
    def get_archive_date(filepath):
        if not filepath.lower().endswith('.pdf'):
            return {'message': 'Only PDF files can be archived.', 'error': True}

        if not os.path.exists(config.metadata_file):
            return "Metadata file not found."

        with open(config.metadata_file) as f:
            data = json.load(f)

        date = data.get(filepath, None)  # TODO: default: None? co zwrocic
        if date:
            date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
            date = date_obj.strftime("%Y-%m-%d %H:%M:%S")

        return date


class FileDeleter:
    def __init__(self, upload_folder, archive_folder):
        self.upload_folder = upload_folder
        self.archive_folder = archive_folder

    def delete_file(self, filename, permanent=False):
        folder = self.archive_folder if permanent else self.upload_folder
        file_path = os.path.join(folder, secure_filename(filename))
        if not os.path.exists(file_path):
            return {'message': "File not found.", 'error': True}

        if permanent:
            os.remove(file_path)
        else:
            send2trash.send2trash(file_path)

        return {'message': f"File {filename} {'permanently ' if permanent else ''}deleted successfully.",
                'success': True}


class FileArchiver:
    def __init__(self, upload_folder, archive_folder):
        self.upload_folder = upload_folder
        self.archive_folder = archive_folder

    def archive_file(self, filename):
        source = os.path.join(self.upload_folder, secure_filename(filename))
        destination = os.path.join(self.archive_folder, secure_filename(filename))
        if not os.path.exists(source):
            return {'message': "File not found.", 'error': True}
        shutil.move(source, destination)
        return {'message': f"File {filename} archived successfully.", 'success': True}

    def restore_file(self, filename):
        source = os.path.join(self.archive_folder, secure_filename(filename))
        destination = os.path.join(self.upload_folder, secure_filename(filename))
        if not os.path.exists(source):
            return {'message': "File not found in archive.", 'error': True}
        shutil.move(source, destination)
        return {'message': f"File {filename} restored successfully.", 'success': True}
