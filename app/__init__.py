"""Flask application factory.

Creates and configures the Flask app, registers the blueprint,
enables gzip compression, and attaches security and cache headers.
"""

from flask import Flask, Response
from flask_compress import Compress
from config import Config

__all__ = ['create_app']

compress: Compress = Compress()


def create_app() -> Flask:
    """Build and return a configured Flask application instance."""
    Config.validate()
    app: Flask = Flask(__name__)
    app.config.from_object(Config)
    from app.routes import bp
    app.register_blueprint(bp)
    compress.init_app(app)
    _attach_response_headers(app)
    return app


def _attach_response_headers(app: Flask) -> None:
    """Attach security and cache headers to every outgoing HTTP response."""
    @app.after_request
    def add_headers(response: Response) -> Response:
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = (
            'max-age=31536000; includeSubDomains'
        )
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; "
            "img-src 'self' data:;"
        )
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = (
            'camera=(), geolocation=(), microphone=()'
        )
        if response.content_type:
            types: tuple = (
                'text/css',
                'application/javascript',
                'text/javascript',
                'image/',
                'font/',
            )
            if response.content_type.startswith(types):
                response.headers['Cache-Control'] = (
                    'public, max-age=31536000, immutable'
                )
        return response
