import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


def _validate_security_config():
    """Validate that security configuration is properly set.
    
    Raises ValueError if using insecure defaults in production.
    Should be called during app initialization.
    """
    secret_key = os.environ.get('SECRET_KEY')
    password_salt = os.environ.get('SECURITY_PASSWORD_SALT')
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        if not secret_key:
            raise ValueError(
                "SECRET_KEY environment variable must be set in production. "
                "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        if not password_salt or password_salt == 'change-me-in-production':
            raise ValueError(
                "SECURITY_PASSWORD_SALT must be set to a secure value in production."
            )
        if secret_key == 'dev-secret-change-in-production':
            raise ValueError(
                "SECRET_KEY cannot be the default dev value in production."
            )


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Admins for error notifications
    ADMINS = os.environ.get('ADMINS', '').split(',') if os.environ.get('ADMINS') else []

    # Session security
    SESSION_COOKIE_NAME = 'janus_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    @property
    def SESSION_COOKIE_SECURE(self):
        """HTTPS only in production."""
        return not self.DEBUG

    # Database
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return os.environ.get('DATABASE_URL') or self._get_default_uri()

    def _get_default_uri(self):
        return f'sqlite:///{os.path.join(basedir, "janus.db")}'

    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = '200 per day'
    RATELIMIT_HEADERS_ENABLED = True

    # Password reset
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'change-me-in-production'
    RESET_PASSWORD_TOKEN_TIMEOUT = 3600  # 1 hour

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.environ.get('SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 900  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 604800  # 7 days
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    
    # Relaxed rate limits for development
    RATELIMIT_ENABLED = False

    def _get_default_uri(self):
        return f'sqlite:///{os.path.join(basedir, "janus_dev.db")}'


class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False
    
    # Strict rate limits for production
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    
    # Force secure cookies in production
    SESSION_COOKIE_SECURE = True

    def _get_default_uri(self):
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            raise ValueError(
                "DATABASE_URL must be set for production. "
                "Example: mysql+pymysql://user:pass@localhost/janus"
            )
        return db_url


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False

    def _get_default_uri(self):
        return 'sqlite:///:memory:'


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)
