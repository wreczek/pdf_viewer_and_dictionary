import os
from datetime import datetime

import send2trash
from werkzeug.utils import secure_filename
from win32_setctime import setctime

from utils import config, get_status

ALLOWED_EXTENSIONS = {'txt', 'pdf'}


class FileManager:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    def upload_file(self, file):
        """Uploads a file to the designated upload folder."""
        if file.filename == '':
            return {'message': 'No selected file.', 'error': True}

        filename = secure_filename(file.filename)
        if not self.allowed_file(filename):
            return {'message': 'File type is not allowed.', 'error': True}

        if file.content_length > config.max_size:
            size = file.content_length
            return {
                'message': f'File size exceeds the maximum limit of {self.format_file_size(size)}.',
                'error': True}

        try:
            file_path = os.path.join(self.upload_folder, filename)
            file.save(file_path)
            current_time = datetime.now().timestamp()
            setctime(file_path, current_time)
            return {'message': 'File successfully uploaded!', 'success': True}
        except Exception as e:
            return {'message': f"Error uploading file: {e}", 'error': True}

    def list_files(self):
        """Retrieves information about available files in the upload folder."""
        files_info = []
        for filename in self.get_available_files():
            file_path = os.path.join(self.upload_folder, filename)
            status = get_status(file_path)  # Ensure get_status is accessible or move its logic here
            upload_date = self.get_upload_date(file_path)
            access_date = self.get_access_date(file_path)

            files_info.append({
                'name': filename,
                'upload_date': upload_date,
                'access_date': access_date,
                'status': status
            })

        files_info.sort(key=lambda x: x['access_date'], reverse=True)
        return files_info

    def delete_file(self, filename):
        """Deletes a file from the upload folder after ensuring it is a PDF and not a directory."""
        # Ensure the filename is secure and the file extension is correct
        filename = secure_filename(filename)
        if not filename.lower().endswith('.pdf'):
            return {'message': 'Only PDF files can be deleted.', 'error': True}

        file_path = os.path.join(self.upload_folder, filename)

        # Check if the file exists and is a file, not a directory
        if os.path.isfile(file_path):
            try:
                send2trash.send2trash(file_path)  # TODO: Logger
                return {'message': f'File {filename} deleted successfully!', 'success': True}
            except Exception as e:
                return {'message': f"Error deleting file: {e}", 'error': True}
        else:
            return {'message': 'File not found or is a directory.', 'error': True}

    @staticmethod
    def format_file_size(size_bytes):
        """Formats the file size in a human-readable format using f-strings and a dictionary."""
        suffixes = ["bytes", "KiB", "MiB", "GiB"]
        index = 0

        while size_bytes >= 1024 and index < len(suffixes) - 1:
            size_bytes /= 1024
            index += 1

        return f"{size_bytes:.1f} {suffixes[index]}"

    @staticmethod
    def get_available_files():
        pdf_files = [f for f in os.listdir(config.upload_folder) if f.endswith('.pdf')]

        return pdf_files

    @staticmethod
    def allowed_file(filename: str):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def get_access_date(file_path):
        try:
            access_time = os.path.getatime(file_path)
            upload_date = datetime.fromtimestamp(access_time).strftime("%Y-%m-%d %H:%M:%S")
            return upload_date
        except Exception as e:
            print(f"Error getting upload date: {e}")
            return None

    @staticmethod
    def get_upload_date(file_path):
        try:
            creation_time = os.path.getctime(file_path)
            upload_date = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
            return upload_date
        except Exception as e:
            print(f"Error getting upload date: {e}")
            return None
