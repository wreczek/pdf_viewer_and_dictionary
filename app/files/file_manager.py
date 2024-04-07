import json
import logging
import os
import shutil
from datetime import datetime

import send2trash
from werkzeug.utils import secure_filename
from win32_setctime import setctime

from utils import config, get_status

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class FileManager:
    def __init__(self, upload_folder, archive_folder):
        self.upload_folder = upload_folder
        self.archive_folder = archive_folder
        self.not_found_msg = 'File not found or is a directory.'

    def get_file_path(self, filename: str, folder_type: str) -> str:
        """
        Constructs a file path based on the filename and folder type.

        Args:
            filename (str): The name of the file.
            folder_type (str): The type of folder ('upload' or 'archive') to construct the path for.

        Returns:
            str: The constructed file path.
        """
        base_path = self.upload_folder if folder_type == 'upload' else self.archive_folder
        secure_name = secure_filename(filename)
        final_path = os.path.join(base_path, secure_name)
        # Ensure the final path is within the intended directory
        if os.path.commonpath([final_path, base_path]) != os.path.normpath(base_path):
            raise ValueError("Invalid file path. Potential directory traversal attempt detected.")
        return final_path

    @staticmethod
    def validate_file_for_operation(filename: str, operation: str) -> (bool, str):
        """
        Validates the file for the specified operation.

        Args:
            filename (str): The name of the file to validate.
            operation (str): The operation to validate against. Valid operations are 'upload', 'delete', 'archive', and 'restore'.

        Returns:
            (bool, str): A tuple where the first element is a boolean indicating if the file is valid for the operation, and the second element is an error message in case of validation failure.
        """
        # Check for allowed file type
        if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
            return False, f"File type of {filename} is not allowed."

        # Operation-specific validations
        if operation in ['delete', 'archive', 'restore'] and not filename.lower().endswith('.pdf'):
            return False, "Only PDF files can be processed for this operation."

        return True, ""

    def upload_files(self, files):
        """Uploads multiple files to the designated upload folder."""
        uploaded_files = []
        for file in files:
            if file.filename == '':
                continue
            filename = secure_filename(file.filename)

            # Use the new validation method
            is_valid, error_message = self.validate_file_for_operation(file.filename, 'upload')
            if not is_valid:
                return {'message': error_message, 'error': True}

            # Size check remains here as it's specific to uploads
            if file.content_length > config.max_size:
                size = file.content_length
                return {
                    'message': f'File size of {file.filename} exceeds the maximum limit of {self.format_file_size(size)}.',
                    'error': True}

            try:
                file_path = self.get_file_path(filename, "upload")
                file.save(file_path)
                self.update_file_creation_date(file_path)
                uploaded_files.append(filename)
                logging.info(f'File {filename} uploaded successfully.')
            except Exception as e:
                logging.error(f'Error uploading file {filename}: {e}')
                return {'message': f"Error uploading file {filename}: {e}", 'error': True}
        if uploaded_files:
            return {'message': f"Files successfully uploaded: {', '.join(uploaded_files)}", 'success': True}
        else:
            return {'message': 'No files were uploaded.', 'error': True}

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
        is_valid, error_message = self.validate_file_for_operation(filename, 'delete')
        if not is_valid:
            return {'message': error_message, 'error': True}

        file_path = self.get_file_path(filename, 'upload')
        if os.path.isfile(file_path):
            try:
                send2trash.send2trash(file_path)
                logging.info(f'File {filename} deleted successfully.')
                return {'message': f'File {filename} deleted successfully!', 'success': True}
            except Exception as e:
                logging.error(f'Error deleting file {filename}: {e}')
                return {'message': f"Error deleting file: {e}", 'error': True}
        else:
            logging.warning(f'File not found: {filename}')
            return {'message': self.not_found_msg, 'error': True}

    def permanently_delete_file(self, filename):
        """todo"""
        filename = secure_filename(filename)

        is_valid, error_message = self.validate_file_for_operation(filename, 'archive')
        if not is_valid:
            return {'message': error_message, 'error': True}

        file_path = self.get_file_path(filename, 'archive')

        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                logging.info(f'File {filename} permanently deleted successfully.')
                return {'message': f'File {filename} deleted successfully!', 'success': True}
            except Exception as e:
                logging.error(f'Error permanently deleting file {filename}: {e}')
                return {'message': f"Error deleting file: {e}", 'error': True}
        else:
            return {'message': self.not_found_msg, 'error': True}

    def archive_file(self, filename):
        """
        Archives a PDF file by moving it from the upload folder to the archive folder.

        Args:
            filename (str): The name of the file to be archived.
        Returns:
            dict: A dictionary containing the status message and success/error indicator.
        """
        filename = secure_filename(filename)

        is_valid, error_message = self.validate_file_for_operation(filename, 'archive')
        if not is_valid:
            return {'message': error_message, 'error': True}

        current_path = self.get_file_path(filename, "upload")
        new_path = self.get_file_path(filename, "archive")

        if os.path.isfile(new_path):
            return {'message': f"File {filename} already exists in the archive.", 'error': True}

        if os.path.isfile(current_path):
            try:
                shutil.move(current_path, new_path)
                self.write_archive_date(new_path, datetime.now())
                logging.info(f"File {filename} archived successfully.")
                return {'message': f'File {filename} archived successfully!', 'success': True}
            except (IOError, OSError) as e:
                logging.error(f"Error archiving file {filename}: {e}")
                return {'message': f"Error archiving file: {e}", 'error': True}
        else:
            logging.warning(f"File not found: {filename}")
            return {'message': self.not_found_msg, 'error': True}

    def restore_file(self, filename):
        """Restores a PDF file by moving it from the archive folder back to the upload folder.
        Returns a dictionary with the operation result."""
        filename = secure_filename(filename)
        if not filename.lower().endswith('.pdf'):
            return {'message': 'Only PDF files can be restored.', 'error': True}

        current_path = self.get_file_path(filename, 'archive')
        new_path = self.get_file_path(filename, 'upload')

        if os.path.isfile(new_path):
            return {'message': f"File {filename} already exists in the upload folder.", 'error': True}

        if os.path.isfile(current_path):
            try:
                shutil.move(current_path, new_path)
                logging.info(f"File {filename} restored successfully.")
                return {'message': f'File {filename} restored successfully!', 'success': True}
            except (IOError, OSError) as e:
                logging.error(f"Error restoring file {filename}: {e}")
                return {'message': f"Error restoring file: {e}", 'error': True}
        else:
            return {'message': self.not_found_msg, 'error': True}

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
