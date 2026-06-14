"""CSRF (Cross-Site Request Forgery) protection module.

Uses Flask's built-in itsdangerous library (already a dependency)
to generate and validate signed CSRF tokens stored in the session.
"""

from flask import request, abort, session
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app
from typing import Optional


def get_csrf_token() -> str:
    """Retrieve the existing CSRF token from the session, or generate a new one."""
    s: URLSafeTimedSerializer = URLSafeTimedSerializer(
        current_app.config['SECRET_KEY'], salt='csrf-token',
    )
    if 'csrf_token' not in session:
        session['csrf_token'] = s.dumps('csrf')
    return session['csrf_token']


def validate_csrf() -> None:
    """Validate the CSRF token submitted with the form.

    Aborts with 400 if the token is missing, invalid, or expired.
    """
    token: Optional[str] = request.form.get('csrf_token')
    if not token:
        abort(400, 'Missing CSRF token.')

    s: URLSafeTimedSerializer = URLSafeTimedSerializer(
        current_app.config['SECRET_KEY'], salt='csrf-token',
    )
    stored: str = session.get('csrf_token', '')

    try:
        # Both the submitted token and the stored token must decrypt to 'csrf'.
        if s.loads(token) != s.loads(stored):
            abort(400, 'Invalid CSRF token.')
    except (BadSignature, SignatureExpired):
        abort(400, 'Invalid or expired CSRF token.')
