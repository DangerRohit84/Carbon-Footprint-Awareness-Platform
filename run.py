"""Application entry point.

Usage:
    python run.py          # Development server
    gunicorn run:app       # Production (via Dockerfile)
"""

import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402

__all__ = ['app']

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG'],
    )
