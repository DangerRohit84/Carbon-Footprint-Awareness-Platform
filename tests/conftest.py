import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.models import FootprintRecord


@pytest.fixture(autouse=True)
def clear_records():
    FootprintRecord._records.clear()


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    return app


@pytest.fixture
def client(app):
    return app.test_client()
