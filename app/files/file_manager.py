import json
import os
import shutil
from datetime import datetime

import send2trash
from werkzeug.utils import secure_filename
from win32_setctime import setctime

from utils import config, get_status

ALLOWED_EXTENSIONS = {'txt', 'pdf'}


class FileManager:
    def __init__(self, upload_folder, archive_folder):
        self.upload_folder = upload_folder
        self.archive_folder = archive_folder

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
            self.update_file_creation_date(file_path)
            return {'message': 'File successfully uploaded!', 'success': True}
        except Exception as e:
            return {'message': f"Error uploading file: {e}", 'error': True}

    @staticmethod
    def update_file_creation_date(file_path):
        current_time = datetime.now().timestamp()
        setctime(file_path, current_time)

    def list_uploaded_files(self):
        """Retrieves information about available files in the upload folder."""
        files_info = self.list_files(path=self.upload_folder)
        files_info.sort(key=lambda x: x['access_date'], reverse=True)
        return files_info

    def list_archived_files(self):
        """TODO"""
        files_info = self.list_files(path=self.archive_folder)
        files_info.sort(key=lambda x: x['archive_date'], reverse=True)
        return files_info

    def list_files(self, path):
        files_info = []
        for filename in self.get_available_files(path):
            file_path = os.path.join(path, filename)
            status = get_status(file_path)
            upload_date = self.get_upload_date(file_path)
            access_date = self.get_access_date(file_path)
            archive_date = self.get_archive_date(file_path)

            files_info.append({
                'name': filename,
                'upload_date': upload_date,
                'access_date': access_date,
                'archive_date': archive_date,
                'status': status
            })

        return files_info

    def delete_file(self, filename):
        """Deletes a file from the upload folder after ensuring it is a PDF and not a directory."""
        filename = secure_filename(filename)
        if not filename.lower().endswith('.pdf'):
            return {'message': 'Only PDF files can be deleted.', 'error': True}

        file_path = os.path.join(self.upload_folder, filename)

        if os.path.isfile(file_path):
            try:
                send2trash.send2trash(file_path)  # TODO: Logger
                return {'message': f'File {filename} deleted successfully!', 'success': True}
            except Exception as e:
                return {'message': f"Error deleting file: {e}", 'error': True}
        else:
            return {'message': 'File not found or is a directory.', 'error': True}

    def permanently_delete_file(self, filename):
        """todo"""
        filename = secure_filename(filename)
        if not filename.lower().endswith('.pdf'):
            return {'message': 'Only PDF files can be (permanently) deleted.', 'error': True}

        file_path = os.path.join(self.archive_folder, filename)

        if os.path.isfile(file_path):
            try:
                os.remove(file_path)  # TODO: Logger
                return {'message': f'File {filename} deleted successfully!', 'success': True}
            except Exception as e:
                return {'message': f"Error deleting file: {e}", 'error': True}
        else:
            return {'message': 'File not found or is a directory.', 'error': True}

    def archive_file(self, filename):
        """todo"""
        filename = secure_filename(filename)
        if not filename.lower().endswith('.pdf'):
            return {'message': 'Only PDF files can be archived.', 'error': True}

        file_path = os.path.join(self.upload_folder, filename)
        new_path = os.path.join(self.archive_folder, filename)
        if os.path.isfile(file_path):
            try:
                shutil.move(file_path, new_path)
                self.write_archive_date(new_path, datetime.now())
                # TODO:
                return {'message': f'File {filename} archived successfully!', 'success': True}
            except Exception as e:
                return {'message': f"Error archiving file: {e}", 'error': True}
        else:
            return {'message': 'File not found or is a directory.', 'error': True}

    def restore_file(self, filename):
        """TODO"""
        filename = secure_filename(filename)
        if not filename.lower().endswith('.pdf'):
            return {'message': 'Only PDF files can be restored.', 'error': True}

        file_path = os.path.join(self.archive_folder, filename)
        new_path = os.path.join(self.upload_folder, filename)
        if os.path.isfile(file_path):
            try:
                shutil.move(file_path, new_path)
                return {'message': f'File {filename} restored successfully!', 'success': True}
            except Exception as e:
                return {'message': f"Error restoring file: {e}", 'error': True}
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
    def get_available_files(path):
        pdf_files = [f for f in os.listdir(path) if f.endswith('.pdf')]

        return pdf_files

    @staticmethod
    def allowed_file(filename: str):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    def get_upload_date(file_path):
        try:
            creation_time = os.path.getctime(file_path)
            upload_date = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
            return upload_date
        except Exception as e:
            print(f"Error getting upload date: {e}")
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

    @staticmethod
    def write_archive_date(file_path, archive_date):
        metadata_file = config.metadata_file
        # Ensure the directory exists
        directory = os.path.dirname(metadata_file)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except Exception as e:
                return {'message': f'Failed to create directory: {e}', 'error': True}

        # Attempt to read existing data
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file) as f:
                    data = json.load(f)
            except Exception as e:
                return {'message': f'Failed to read metadata file: {e}', 'error': True}
        else:
            data = {}

        # Convert datetime to string in ISO format
        if isinstance(archive_date, datetime):
            archive_date = archive_date.isoformat()

        # Update the data
        data[file_path] = archive_date

        # Attempt to write the data back
        try:
            with open(metadata_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            return {'message': f'Failed to write metadata file: {e}', 'error': True}

        return {'message': 'Archive date updated successfully.', 'error': False}
