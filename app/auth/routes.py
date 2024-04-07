import logging
from sqlite3 import IntegrityError

from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app.auth.forms import LoginForm, RegistrationForm
from app.extensions import db
from app.models import User
from . import auth_bp

HOME_PAGE = 'main.index'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(HOME_PAGE))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user is not None:
            flash('Username already taken. Please choose a different one.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        try:
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError as e:
            db.session.rollback()
            flash('Username already taken. Please choose a different one.', 'danger')
            logging.error(f'Error: {e}')
    return render_template('register.html', title='Register', form=form)


@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(HOME_PAGE))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            logging.error(f'Login for {current_user} unsuccessful.')
    return render_template('login.html', title='Login', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for(HOME_PAGE))
