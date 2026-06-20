"""Application configuration.

Validates required settings at initialization time
rather than at import time for cleaner error handling.
"""

import os

__all__ = ['Config']


class Config:
    """Flask configuration loaded via app.config.from_object()."""

    SECRET_KEY: str = ''
    DEBUG: bool = False
    ENV: str = 'production'
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Lax'

    @classmethod
    def validate(cls) -> None:
        """Check required config values before the app starts."""
        cls.SECRET_KEY = os.environ.get('SECRET_KEY', '')
        if not cls.SECRET_KEY:
            raise RuntimeError(
                'SECRET_KEY environment variable must be set.'
            )
        cls.DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
        cls.ENV = os.environ.get('FLASK_ENV', 'production')
