from flask import render_template

from . import error_bp


@error_bp.route('/test_404')
def test_404():
    return render_template('404.html'), 404


@error_bp.route('/test_500')
def test_500():
    return render_template('500.html'), 500
