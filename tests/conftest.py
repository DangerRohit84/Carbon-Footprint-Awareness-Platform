"""Test configuration and fixtures for pytest."""

import sys
import os

# Ensure the project root is in the Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.models import FootprintRecord


@pytest.fixture(autouse=True)
def clear_records():
    """Clear in-memory records before each test to ensure isolation."""
    FootprintRecord._records.clear()


@pytest.fixture(autouse=True)
def csrf_bypass(monkeypatch):
    """Bypass CSRF validation during tests so we don't need tokens."""
    monkeypatch.setattr('app.routes.validate_csrf', lambda: None)


def _csrf_token():
    """Return a dummy CSRF token for use in test form submissions."""
    return 'test-csrf-token'


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def csrf_data():
    """Return a dict with a CSRF token for use in test form POSTs."""
    return {'csrf_token': 'test-csrf-token'}
