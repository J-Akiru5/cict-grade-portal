import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase: Client | None = None
_supabase_admin: Client | None = None


def _get_client() -> Client:
    global _supabase
    if _supabase is None:
        url = os.environ['SUPABASE_URL']
        key = os.environ['SUPABASE_KEY']
        _supabase = create_client(url, key)
    return _supabase


def _get_admin_client() -> Client:
    global _supabase_admin
    if _supabase_admin is None:
        url = os.environ['SUPABASE_URL']
        service_key = os.environ['SUPABASE_SERVICE_KEY']
        _supabase_admin = create_client(url, service_key)
    return _supabase_admin


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


def sign_up(email: str, password: str, role: str = 'student', redirect_to: str | None = None):
    """
    Register a new user by generating a signup confirmation link.
    The caller is responsible for sending the returned action_link via email.
    """
    client = _get_admin_client()

    options = {'data': {'role': role}}
    if redirect_to:
        options['redirect_to'] = redirect_to

    response = client.auth.admin.generate_link({
        'type': 'signup',
        'email': email,
        'password': password,
        'options': options,
    })
    return response
