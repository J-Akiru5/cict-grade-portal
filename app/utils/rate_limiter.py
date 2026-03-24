"""
Rate limiting configuration and utilities for the Grade Portal.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request, current_app
from flask_login import current_user


def get_limiter_key():
    """
    Custom key function for rate limiting.
    - Uses user ID for authenticated users
    - Uses IP address for anonymous users
    - Includes endpoint for more granular control
    """
    if current_user.is_authenticated:
        # Use user ID for authenticated requests
        key = f"user:{current_user.id}:{request.endpoint}"
    else:
        # Use IP address for anonymous requests
        ip = get_remote_address()
        key = f"ip:{ip}:{request.endpoint}"

    return key


def init_limiter(app):
    """Initialize Flask-Limiter with the app."""
    limiter = Limiter(
        app=app,
        key_func=get_limiter_key,
        storage_uri="memory://",  # In-memory storage for simplicity
        default_limits=["1000 per hour"],  # Global default limit
        headers_enabled=True,  # Include rate limit headers in response
    )

    return limiter


# Rate limit configurations for different endpoint types
RATE_LIMITS = {
    # Authentication endpoints (stricter limits)
    'auth_login': '5 per minute',
    'auth_forgot_password': '3 per 10 minutes',
    'auth_reset_password': '3 per 10 minutes',
    'auth_register': '3 per 10 minutes',

    # API endpoints
    'api_validation': '60 per minute',
    'api_bulk_validation': '30 per minute',

    # File upload endpoints
    'file_upload': '10 per minute',
    'bulk_import': '5 per minute',

    # Admin operations
    'admin_create': '20 per minute',
    'admin_delete': '10 per minute',
    'admin_bulk_operations': '5 per minute',

    # Grade operations
    'grade_encode': '100 per minute',
    'grade_release': '20 per minute',

    # Search and list endpoints
    'search': '200 per minute',
    'list': '300 per minute',

    # Profile updates (less strict for user convenience)
    'profile_update': '20 per minute',
}