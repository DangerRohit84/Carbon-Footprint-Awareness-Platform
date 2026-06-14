"""Application entry point.

Loads environment variables from .env, creates the Flask app,
and starts the development server when executed directly.
"""

import os
from dotenv import load_dotenv

# Load .env before importing the app so SECRET_KEY and DEBUG are available.
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Bind to 0.0.0.0 so the server is accessible from outside the container.
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
