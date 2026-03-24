from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from app.utils.rate_limiter import get_limiter_key
from supabase import create_client, Client
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_limiter_key)

# Supabase client — initialized lazily after app context
_supabase: Client | None = None


def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
        if not url or not key:
            raise RuntimeError('SUPABASE_URL and SUPABASE_KEY must be set in .env')
        _supabase = create_client(url, key)
    return _supabase
