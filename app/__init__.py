import os
from flask import Flask
from .config import config
from .extensions import db, migrate, login_manager, csrf


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='static',
    )

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
        from .models import user, student, subject, enrollment, grade, schedule, audit  # noqa: F401

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.student import student_bp
    from .routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')

    # Register error handlers
    from .utils.errors import register_error_handlers
    register_error_handlers(app)

    return app
