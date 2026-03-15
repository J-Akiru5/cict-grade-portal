from flask import flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFError


def register_error_handlers(app):
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        # CSRF failures are usually caused by expired sessions or stale cached pages.
        flash('Your session has expired. Please refresh the page and try again.', 'warning')
        return redirect(request.referrer or url_for('auth.login'))

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500
