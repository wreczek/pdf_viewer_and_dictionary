from flask import Blueprint

# Define the 'main' blueprint
main_bp = Blueprint('main', __name__, template_folder='templates')
