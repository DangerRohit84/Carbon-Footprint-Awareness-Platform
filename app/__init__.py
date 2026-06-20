"""Flask application factory.

Creates and configures the Flask app, registers the blueprint,
and attaches security headers to every response.
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

    _attach_response_headers(app)

    return app


def _attach_response_headers(app: Flask) -> None:
    """Attach security and cache headers to every outgoing HTTP response."""
    @app.after_request
    def add_headers(response: Response) -> Response:
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; "
            "img-src 'self' data:;"
        )
        if response.content_type:
            if response.content_type.startswith(('text/css', 'application/javascript', 'text/javascript')):
                response.headers['Cache-Control'] = 'public, max-age=86400'
        return response
