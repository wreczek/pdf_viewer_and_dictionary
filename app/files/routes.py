import json
import os
from datetime import datetime

from flask import render_template, request, flash, redirect, url_for, send_from_directory, jsonify

from app.files import file_manager, files_bp
from utils import config

FILE_LIST_ROUTE = 'files.file_list'
ARCHIVE_LIST_ROUTE = 'files.archive_list'


@files_bp.route('/upload', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST' and 'files' in request.files:
        result = file_manager.upload_files(request.files.getlist('files'))
        flash(result['message'], 'success' if 'success' in result else 'danger')
        return redirect(request.url if 'error' in result else url_for(FILE_LIST_ROUTE))
    return render_template('upload.html', active_page='upload_file')


@files_bp.route('/file_list')
def file_list():
    pdf_files_info = file_manager.list_uploaded_files()
    return render_template('file_list.html',
                           pdf_files_info=pdf_files_info,
                           active_page='file_list')


@files_bp.route('/archive_list')
def archive_list():
    archived_files_info = file_manager.list_archived_files()
    return render_template('archive_list.html',
                           archived_files_info=archived_files_info,
                           active_page='archive_list')


@files_bp.route('/delete_file/<filename>', methods=['POST'])
def delete_file(filename):
    result = file_manager.delete_file(filename)
    flash(result['message'], 'success' if 'success' in result else 'danger')
    return redirect(url_for(FILE_LIST_ROUTE))


@files_bp.route('/permanently_delete_file', methods=['POST'])
def permanently_delete_file(filename):
    """TODO"""
    result = file_manager.permanently_delete_file(filename)
    flash(result['message'], 'success' if 'success' in result else 'danger')
    return redirect(url_for(ARCHIVE_LIST_ROUTE))


@files_bp.route('/archive_file/<filename>', methods=['POST'])
def archive_file(filename):
    """TODO"""
    result = file_manager.archive_file(filename)
    flash(result['message'], 'success' if 'success' in result else 'danger')
    return redirect(url_for(ARCHIVE_LIST_ROUTE))


@files_bp.route('/restore_file/<filename>', methods=['POST'])
def restore_file(filename):
    result = file_manager.restore_file(filename)
    flash(result['message'], 'success' if 'success' in result else 'danger')
    return redirect(url_for(FILE_LIST_ROUTE))


@files_bp.route('/pdf/<path:filename>')
def pdf(filename):
    return send_from_directory(config.upload_folder, filename)


@files_bp.route('/uploaded_list/<path:filename>')
def pdf_viewer(filename):
    pdf_path = url_for('files.pdf', filename=filename)

    # Retrieve the last stored position from localStorage
    last_position = request.cookies.get(f'last_position_{filename}')

    # Update access time
    file_path = os.path.join(config.upload_folder, filename)
    current_time = datetime.now().timestamp()

    # Update the access time of the file
    os.utime(file_path, (current_time, current_time))

    return render_template('pdf_viewer.html',
                           file_name=filename,
                           current_file=filename,
                           pdf_path=pdf_path,
                           last_position=last_position,  # Pass last_position to the template
                           active_page='pdf_viewer')


@files_bp.route('/perform_batch_operation', methods=['POST'])
def perform_batch_operation():
    filenames = request.form.get('filenames')
    operation = request.form.get('operation')

    if not filenames:
        return jsonify({'success': False, 'message': 'No files selected.'})

    try:
        filenames = json.loads(filenames)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid file list.'})

    print(filenames)

    results = []
    for filename in filenames:
        if operation == 'archive':
            result = file_manager.archive_file(filename)
        elif operation == 'delete':
            result = file_manager.delete_file(filename)
        elif operation == "restore":
            result = file_manager.restore_file(filename)
        elif operation == "annihilate":
            result = file_manager.permanently_delete_file(filename)
        else:
            return jsonify({'success': False, 'message': 'Invalid operation.'})
        results.append(result)

    return jsonify({'success': True, 'results': results})
