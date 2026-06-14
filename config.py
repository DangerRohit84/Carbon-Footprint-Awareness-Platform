import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError('SECRET_KEY environment variable must be set for production.')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    ENV = os.environ.get('FLASK_ENV', 'production')
