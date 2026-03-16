import os
import logging
from supabase import create_client

logger = logging.getLogger(__name__)

BUCKET = 'avatars'


def _get_storage_client():
    """Return a Supabase client with service-role key (bypasses RLS)."""
    url = os.environ['SUPABASE_URL']
    service_key = os.environ['SUPABASE_SERVICE_KEY']
    return create_client(url, service_key)


def upload_avatar(user_id: str, file_bytes: bytes, content_type: str) -> str | None:
    """Upload a profile photo to the 'avatars' bucket. Returns the public URL or None."""
    try:
        client = _get_storage_client()
        ext = 'png' if 'png' in content_type else 'jpg'
        path = f'users/{user_id}.{ext}'

        # Remove stale file (ok to fail if not found)
        try:
            client.storage.from_(BUCKET).remove([path])
        except Exception:
            pass

        client.storage.from_(BUCKET).upload(
            path=path,
            file=file_bytes,
            file_options={'content-type': content_type}
        )
        public_url = client.storage.from_(BUCKET).get_public_url(path)
        return public_url
    except Exception as e:
        logger.warning('Avatar upload failed for user %s: %s', user_id, e)
        return None
