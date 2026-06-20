"""CSRF (Cross-Site Request Forgery) protection module.

Uses itsdangerous (already a Flask dependency) to generate
and validate signed CSRF tokens stored in the session.
"""

from flask import abort, current_app, request, session
from itsdangerous import (
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)
from typing import Optional

__all__ = ['get_csrf_token', 'validate_csrf']


def get_csrf_token() -> str:
    """Return existing CSRF token or generate a new one."""
    s: URLSafeTimedSerializer = URLSafeTimedSerializer(
        current_app.config['SECRET_KEY'], salt='csrf-token',
    )
    if 'csrf_token' not in session:
        session['csrf_token'] = s.dumps('csrf')
    return session['csrf_token']


def validate_csrf() -> None:
    """Validate the submitted CSRF token. Aborts with 400 on failure."""
    token: Optional[str] = request.form.get('csrf_token')
    if not token:
        abort(400, 'Missing CSRF token.')
    s: URLSafeTimedSerializer = URLSafeTimedSerializer(
        current_app.config['SECRET_KEY'], salt='csrf-token',
    )
    stored: str = session.get('csrf_token', '')
    try:
        if s.loads(token) != s.loads(stored):
            abort(400, 'Invalid CSRF token.')
    except (BadSignature, SignatureExpired):
        abort(400, 'Invalid or expired CSRF token.')
