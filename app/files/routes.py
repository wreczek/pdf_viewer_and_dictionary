from flask import render_template, request, flash, redirect, url_for

from app.files import file_manager, files_bp


@files_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST' and 'file' in request.files:
        result = file_manager.upload_file(request.files['file'])
        flash(result['message'], 'success' if 'success' in result else 'danger')
        return redirect(request.url if 'error' in result else url_for('files.file_list'))
    return render_template('upload.html', active_page='upload_file')


@files_bp.route('/file_list')
def file_list():
    pdf_files_info = file_manager.list_files()
    return render_template('file_list.html', pdf_files_info=pdf_files_info, active_page='file_list')


@files_bp.route('/delete_file/<filename>', methods=['POST'])
def delete_file(filename):
    result = file_manager.delete_file(filename)
    flash(result['message'], 'success' if 'success' in result else 'danger')
    return redirect(url_for('files.file_list'))
