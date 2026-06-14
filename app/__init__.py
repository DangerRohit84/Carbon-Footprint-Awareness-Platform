"""Flask application factory.

Creates and configures the Flask app, registers the blueprint,
enables gzip compression, and attaches security headers.
"""

from flask import Flask, Response
from config import Config


def create_app() -> Flask:
    """Build and return a configured Flask application instance."""
    Config.validate()

    app: Flask = Flask(__name__)
    app.config.from_object(Config)

    from app.routes import bp
    app.register_blueprint(bp)

    _add_static_cache_headers(app)
    _add_security_headers(app)

    return app


def _add_static_cache_headers(app: Flask) -> None:
    """Cache static assets for 1 year for repeat-visit performance."""
    @app.after_request
    def cache_static(response: Response) -> Response:
        if response.content_type and response.content_type.startswith('text/css'):
            response.headers['Cache-Control'] = 'public, max-age=86400'
        return response


def _add_security_headers(app: Flask) -> None:
    """Attach security headers to every outgoing HTTP response."""
    @app.after_request
    def add_security_headers(response: Response) -> Response:
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
