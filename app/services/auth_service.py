import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase: Client | None = None


def _get_client() -> Client:
    global _supabase
    if _supabase is None:
        url = os.environ['SUPABASE_URL']
        key = os.environ['SUPABASE_KEY']
        _supabase = create_client(url, key)
    return _supabase


def sign_in(email: str, password: str) -> dict:
    """
    Authenticate a user via Supabase Auth.
    Returns the auth response with session tokens.
    Raises gotrue.errors.AuthApiError on failure.
    """
    client = _get_client()
    response = client.auth.sign_in_with_password({'email': email, 'password': password})
    return response


def sign_out(access_token: str) -> None:
    """Invalidate the current Supabase session."""
    client = _get_client()
    client.auth.sign_out()


def get_supabase_user(access_token: str):
    """
    Verify a JWT access token and return the Supabase user object.
    Returns None if the token is invalid or expired.
    """
    try:
        client = _get_client()
        # Set the session so the client uses this token
        response = client.auth.get_user(access_token)
        return response.user
    except Exception:
        return None


def sign_up(email: str, password: str, role: str = 'student') -> dict:
    """
    Register a new user in Supabase Auth with user_metadata for role.
    """
    client = _get_client()
    response = client.auth.sign_up({
        'email': email,
        'password': password,
        'options': {
            'data': {'role': role}
        }
    })
    return response
