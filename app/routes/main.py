from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Root route — redirect to dashboard if logged in, else to login."""
    if current_user.is_authenticated:
        from app.routes.auth import _redirect_by_role
        return _redirect_by_role(current_user.role)
    return redirect(url_for('auth.login'))


@main_bp.route('/about')
def about():
    """Public portal information page."""
    return render_template('about.html')


@main_bp.route('/about/retention-policies')
def retention_policies():
    """Public BSIT retention policy page."""
    return render_template('retention_policies.html')


@main_bp.route('/health')
def health():
    """Health check endpoint for Vercel monitoring."""
    from app.extensions import db
    try:
        db.session.execute(db.text('SELECT 1'))
        return {'status': 'ok', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'error', 'database': str(e)}, 500
