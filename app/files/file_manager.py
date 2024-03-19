import os
from datetime import datetime

from werkzeug.utils import secure_filename

from utils import get_status, config

ALLOWED_EXTENSIONS = {'txt', 'pdf'}


class FileManager:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    def upload_file(self, file):
        """Uploads a file to the designated upload folder.

        Args:
          file: A file object from the request.

        Returns:
          A dictionary containing a success message or an error message.
        """

        if file.filename != '':
            try:
                filename = secure_filename(file.filename)
                if self.allowed_file(filename):
                    file.save(os.path.join(self.upload_folder, filename))
                    return {'message': 'File successfully uploaded!', 'success': True}
                else:
                    return {'message': 'File type is not allowed.', 'error': True}
            except Exception as e:
                print(f"Error uploading file: {e}")
                return {'message': str(e), 'error': True}
        else:
            return {'message': 'No selected file.', 'error': True}

    def list_files(self):
        """Retrieves information about available PDF files in the upload folder.

        Returns:
          A list of dictionaries containing details about each PDF file.
        """

        pdf_files_info = []
        for pdf_file in self.get_available_files():
            file_path = os.path.join(self.upload_folder, pdf_file)
            status = get_status(file_path)
            upload_date = self.get_upload_date(file_path)
            access_date = self.get_access_date(file_path)

            pdf_files_info.append({
                'name': pdf_file,
                'upload_date': upload_date,
                'access_date': access_date,
                'status': status
            })

        pdf_files_info.sort(key=lambda x: x['access_date'], reverse=True)
        return pdf_files_info

    def delete_file(self, filename):
        """Deletes a file from the upload folder.

        Args:
          filename: The name of the file to be deleted.

        Returns:
          A dictionary containing a success message or an error message.
        """

        try:
            file_path = os.path.join(self.upload_folder, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return {'message': 'File deleted successfully!', 'success': True}
            else:
                return {'message': 'File not found.', 'error': True}
        except Exception as e:
            print(f"Error deleting file: {e}")
            return {'message': str(e), 'error': True}

    def get_pdf_path(self, filename):
        """Returns the full path to a PDF file in the upload folder.

        Args:
          filename: The name of the PDF file.

        Returns:
          The full path to the file.
        """

        return os.path.join(self.upload_folder, filename)

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
