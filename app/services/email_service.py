import json
import logging
from urllib import error, request

from flask import current_app


def send_resend_email(to_email: str, subject: str, html: str, text: str | None = None) -> bool:
    """Send an email via Resend API.

    Returns True on success; returns False on missing config or API failure.
    """
    api_key = current_app.config.get('RESEND_API_KEY')
    from_email = current_app.config.get('RESEND_FROM_EMAIL')

    if not api_key or not from_email:
        logging.warning('Resend email skipped: RESEND_API_KEY or RESEND_FROM_EMAIL is not configured.')
        return False

    payload = {
        'from': from_email,
        'to': [to_email],
        'subject': subject,
        'html': html,
    }
    if text:
        payload['text'] = text

    req = request.Request(
        url='https://api.resend.com/emails',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )

    try:
        with request.urlopen(req, timeout=15) as response:
            status_code = getattr(response, 'status', 0)
            if 200 <= status_code < 300:
                return True
            logging.warning('Resend email failed with status %s.', status_code)
            return False
    except error.HTTPError as exc:
        logging.warning('Resend email HTTP error %s: %s', exc.code, exc.reason)
        return False
    except Exception as exc:
        logging.warning('Resend email error: %s', exc)
        return False
