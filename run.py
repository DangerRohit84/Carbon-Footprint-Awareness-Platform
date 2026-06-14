"""Application entry point.

Usage:
    python run.py          # Development server
    gunicorn run:app       # Production (via Dockerfile)
"""

import os
import sys
from dotenv import load_dotenv


def main() -> None:
    """Load environment, create app, and start the development server."""
    load_dotenv()

    from app import create_app
    app = create_app()

    if __name__ == '__main__':
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=app.config['DEBUG'],
        )


main()
