import os

from flask import render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

from app.files import file_manager, files_bp
from utils import get_status, config


@files_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            try:
                filename = secure_filename(file.filename)
                if file_manager.allowed_file(filename):
                    file.save(os.path.join(config.upload_folder, filename))
                else:
                    flash('File type is not allowed.', 'danger')
                    return redirect(request.url)
            except Exception as e:
                flash(str(e), 'danger')
                return redirect(request.url)
            flash('File successfully uploaded!', 'success')
            return redirect(url_for('files.file_list'))
        else:
            flash('No selected file.', 'danger')
            return redirect(request.url)
    return render_template('upload.html', active_page='upload_file')


@files_bp.route('/file_list')
def file_list():
    pdf_files_info = []

    for pdf_file in file_manager.get_available_files():
        file_path = os.path.join(config.upload_folder, pdf_file)
        status = get_status(file_path)
        upload_date = file_manager.get_upload_date(file_path)
        access_date = file_manager.get_access_date(file_path)

        pdf_files_info.append({
            'name': pdf_file,
            'upload_date': upload_date,
            'access_date': access_date,
            'status': status
        })

    pdf_files_info.sort(key=lambda x: x['access_date'], reverse=True)

    return render_template('file_list.html',
                           pdf_files_info=pdf_files_info,
                           active_page='file_list')
