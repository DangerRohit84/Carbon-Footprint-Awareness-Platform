"""Application configuration.

Defines configuration class loaded by Flask at startup.
SECRET_KEY is required in production for session signing and CSRF.
"""

import os


class Config:
    """Flask configuration loaded via app.config.from_object()."""

    # Cryptographically sign sessions and CSRF tokens.
    # Must be set via environment variable - no default for safety.
    SECRET_KEY: str = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError('SECRET_KEY environment variable must be set for production.')

    # Debug mode enables verbose error pages and hot-reload.
    DEBUG: bool = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Flask environment (development / production).
    ENV: str = os.environ.get('FLASK_ENV', 'production')

    # Secure cookies: not accessible via JavaScript, sent on same-site requests.
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Lax'
