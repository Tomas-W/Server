from datetime import timedelta
import os

from config.settings import DATABASE_URI


class BaseConfig(object):
    CONFIG_NAME = "base"
    SECRET_KEY = os.environ.get("FLASK_KEY")

    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    DEFAULT_LIMITS = ["240 per day", "60 per hour"]

    SESSION_TYPE = 'sqlalchemy'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = DATABASE_URI

    REMEMBER_COOKIE_DURATION = timedelta(days=21)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("GMAIL_EMAIL")
    MAIL_PASSWORD = os.environ.get("GMAIL_PASS")

    def config_name(self):
        return self.CONFIG_NAME


class DebugConfig(BaseConfig):
    CONFIG_NAME = "debug"
    TEMPLATES_AUTO_RELOAD = True
    EXPLAIN_TEMPLATE_LOADING = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Allow HTTP traffic

    def config_name(self):
        return self.CONFIG_NAME


class DeployConfig(BaseConfig):
    CONFIG_NAME = "deploy"
    TEMPLATES_AUTO_RELOAD = False
    EXPLAIN_TEMPLATE_LOADING = False
    SESSION_COOKIE_SAMESITE = "Strict"
    SESSION_COOKIE_SECURE = True

    def config_name(self):
        return self.CONFIG_NAME
