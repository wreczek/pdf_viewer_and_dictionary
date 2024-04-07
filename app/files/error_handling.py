import logging

from flask import flash, redirect, url_for


def handle_route_errors(route_function):
    """
    A decorator to handle errors and flash messages for Flask routes.
    """

    def wrapper(*args, **kwargs):
        try:
            # Attempt to call the route function
            return route_function(*args, **kwargs)
        except Exception as e:
            # Log the error and flash a generic error message
            logging.error(f"An error occurred: {e}", exc_info=True)
            flash('An unexpected error occurred. Please try again.', 'danger')
            # Redirect to a generic error page or home page
            return redirect(url_for('home'))

    wrapper.__name__ = route_function.__name__
    return wrapper
