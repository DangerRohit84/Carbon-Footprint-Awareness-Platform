"""Flask application factory.

Creates and configures the Flask app, registers the blueprint,
and attaches security response headers to every HTTP response.
"""

from flask import Flask
from flask import Response
from config import Config


def create_app() -> Flask:
    """Build and return a configured Flask application instance."""
    app: Flask = Flask(__name__)
    app.config.from_object(Config)

    # Register the main blueprint which contains all route definitions.
    from app.routes import bp
    app.register_blueprint(bp)

    # Attach security headers to every outgoing HTTP response.
    @app.after_request
    def add_security_headers(response: Response) -> Response:
        """Prevent MIME sniffing, clickjacking, XSS, and content injection."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "script-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:;"
        )
        return response

    return app
