import os

from datetime import timedelta
from typing import Final

from config.settings import SERVER

class BaseConfig(object):
    CONFIG_NAME = "base"

    SEND_FILE_MAX_AGE_DEFAULT = timedelta(days=7)
    ASSETS_DEBUG = True
    
    COMPRESS_ALGORITHM = "gzip"
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    DEFAULT_LIMITS = SERVER.DEFAULT_LIMITS

    SESSION_TYPE = 'sqlalchemy'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = SERVER.DATABASE_URI

    REMEMBER_COOKIE_DURATION = timedelta(hours=12)
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    
    # Simpler CSP that only allows resources from your domain
    SECURITY_HEADERS: Final = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; style-src 'self' fonts.googleapis.com; font-src fonts.gstatic.com",
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block'
    }
    
    # Security Headers
    SECURITY_HEADERS: Final = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block'
    }
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STORAGE_URL = "memory://"  # Change to redis:// in production
    
    # Cookie Settings
    SESSION_COOKIE_NAME = "secure_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"  # Move to base config
    
    # Logging Configuration
    LOG_DIR = "logs"
    LOG_FILE = "app.log"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL = 'INFO'
    LOG_MAX_BYTES =  8 * 1024 * 1024  # 8MB
    LOG_BACKUP_COUNT = 5
    LOG_DATE_FORMAT = "%d-%m %H:%M:%S"
    
    # Color logging for development
    LOG_COLORS = {
        "DEBUG": "blue",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }

    def config_name(self):
        return self.CONFIG_NAME


class DebugConfig(BaseConfig):
    CONFIG_NAME = "debug"
    DEBUG = True
    DEVELOPMENT = True
    TEMPLATES_AUTO_RELOAD = True
    EXPLAIN_TEMPLATE_LOADING = False
    
    # Logging configuration
    LOG_LEVEL = 'DEBUG'
    LOG_DIR = 'logs/debug'
    LOG_FILE = 'debug.log'
    
    # Development-specific security settings
    SESSION_COOKIE_HTTPONLY = False  # Allow JavaScript access in development
    SESSION_COOKIE_SECURE = False    # Allow HTTP in development
    SESSION_COOKIE_SAMESITE = "Lax" # More permissive for development
    PREFERRED_URL_SCHEME = 'http'
    
    # Allow OAuth over HTTP in development
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    def config_name(self):
        return self.CONFIG_NAME


class DeployConfig(BaseConfig):
    CONFIG_NAME = "deploy"
    DEBUG = False
    DEVELOPMENT = False
    TEMPLATES_AUTO_RELOAD = False
    EXPLAIN_TEMPLATE_LOADING = False
    
    # Logging configuration
    LOG_LEVEL = 'INFO'  # Only log warnings and above in production
    LOG_DIR = 'logs/production'
    LOG_FILE = 'production.log'
    
    # Production security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True     # Ensure cookies only sent over HTTPS
    SESSION_COOKIE_SAMESITE = "Strict"
    PREFERRED_URL_SCHEME = 'https'   # Force HTTPS for url_for
    
    # Security headers for HTTPS
    SECURITY_HEADERS = {
        **BaseConfig.SECURITY_HEADERS,
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'Content-Security-Policy': "upgrade-insecure-requests"  # Force HTTPS upgrades
    }

    def config_name(self):
        return self.CONFIG_NAME
