from flask import render_template
from flask_login import login_required

from app.main import main_bp


@main_bp.route("/")
@main_bp.route("/home")
def index():
    return render_template('home.html', title='Home', active_page='index')


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html',
                           title='Dashboard',
                           active_page='dashboard')
