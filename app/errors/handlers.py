from flask import render_template

from app.errors import error_bp
from app.extensions import db


@error_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@error_bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Rollback the session in case of database errors
    return render_template('500.html'), 500
