import os
from flask import Flask, request
from flask_login import current_user
from .config import config
from .extensions import db, migrate, login_manager, csrf
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='static',
    )

    # Trust the X-Forwarded-Proto header for HTTPS redirection on Vercel/Proxies
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Load config
    app.config.from_object(config.get(config_name, config['default']))

    # Fail fast with a clear message when the DB URI is missing (e.g. Vercel
    # env var not configured) instead of a cryptic SQLAlchemy RuntimeError.
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        raise RuntimeError(
            "SQLALCHEMY_DATABASE_URI is not set. "
            "Add DATABASE_URL to your environment variables "
            "(Vercel dashboard → Project Settings → Environment Variables)."
        )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Flask-Login setup
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    # Import models so Alembic can detect them
    with app.app_context():
        from .models import user, student, faculty, subject, enrollment, grade, schedule, audit, academic_settings, section  # noqa: F401

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.student import student_bp
    from .routes.main import main_bp
    from .routes.panel import panel_bp
    from .routes.chatbot import chatbot_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(panel_bp, url_prefix='/panel')
    app.register_blueprint(chatbot_bp)

    # Register error handlers
    from .utils.errors import register_error_handlers
    register_error_handlers(app)

    # Register CLI commands
    from .utils.seed import register_cli
    register_cli(app)

    @app.after_request
    def add_no_store_headers(response):
        # Prevent caching of dynamic pages that contain session-bound CSRF tokens.
        if not request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    @app.context_processor
    def inject_pending_approvals():
        """Inject pending approval count for admin sidebar badge."""
        if current_user.is_authenticated and current_user.role == 'admin':
            from .models.user import User
            pending = User.query.filter_by(is_active=False).count()
            return {'pending_approval_count': pending}
        return {'pending_approval_count': 0}

    return app
