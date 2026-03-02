from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    """
    Decorator to enforce RBAC on a Flask route.
    Usage: @role_required('student') or @role_required('faculty', 'admin')
    
    - Returns 403 (styled) if the user's role is not in the allowed roles.
    - Redirects to login if the user is not authenticated.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                # Security alert: log unauthorized access attempt
                import logging
                logging.warning(
                    f'SECURITY ALERT: User {current_user.id} ({current_user.role}) '
                    f'attempted to access a route requiring {roles}'
                )
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
