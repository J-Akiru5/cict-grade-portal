"""
Rate limit error handlers for the Grade Portal.
"""
from flask import render_template, jsonify, request, flash, redirect, url_for
from flask_limiter import RateLimitExceeded


def register_rate_limit_handlers(app, limiter):
    """Register rate limit error handlers."""

    @limiter.request_filter
    def rate_limit_exempt():
        """Exempt certain requests from rate limiting."""
        # Exempt static files
        if request.path.startswith('/static/'):
            return True
        # Exempt health checks or monitoring endpoints
        if request.path in ['/health', '/status']:
            return True
        return False

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(e):
        """Handle rate limit exceeded errors."""
        # Check if it's an API request
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'retry_after': e.retry_after
            }), 429

        # Check if it's an HTMX request
        if request.headers.get('HX-Request'):
            # Return HTMX-friendly error
            return render_template('errors/rate_limit.html', error=e), 429

        # For regular web requests
        if request.endpoint == 'auth.login':
            flash('Too many login attempts. Please wait before trying again.', 'error')
            return render_template('auth/login.html'), 429
        elif request.endpoint == 'auth.register':
            flash('Too many registration attempts. Please wait before trying again.', 'error')
            return render_template('auth/register.html'), 429
        elif request.endpoint == 'auth.forgot_password':
            flash('Too many password reset requests. Please check your email or wait before trying again.', 'error')
            return render_template('auth/forgot_password.html'), 429
        else:
            # General rate limit error
            flash('Too many requests. Please wait a moment before trying again.', 'error')

            # Try to redirect to a safe page based on user role
            from flask_login import current_user
            if current_user.is_authenticated:
                if current_user.role == 'student':
                    return redirect(url_for('student.dashboard'))
                elif current_user.role in ['faculty', 'admin']:
                    return redirect(url_for('panel.dashboard'))

            # Fallback to main page
            return redirect(url_for('main.index'))