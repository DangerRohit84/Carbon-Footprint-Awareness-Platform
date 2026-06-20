"""Test configuration and fixtures for pytest."""

import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
)

import pytest
from app import create_app
from app.models import DATA_FILE, FootprintRecord

os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('FLASK_ENV', 'testing')


@pytest.fixture(autouse=True)
def clean_state():
    """Clear in-memory records and temp data file before each test."""
    FootprintRecord._records = []
    FootprintRecord._loaded = False
    if os.path.exists(DATA_FILE):
        try:
            os.remove(DATA_FILE)
        except PermissionError:
            pass


@pytest.fixture(autouse=True)
def csrf_bypass(monkeypatch):
    """Bypass CSRF validation during tests."""
    monkeypatch.setattr('app.routes.validate_csrf', lambda: None)


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()
