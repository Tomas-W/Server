import os
import logging

from argon2 import PasswordHasher
from flask import current_app
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from google_auth_oauthlib.flow import Flow
from itsdangerous import URLSafeTimedSerializer

from src.utils.logger import ServerLogger

from config.settings import (
    SERVER,
    PATH,
)


logger = ServerLogger()
server_db_: SQLAlchemy = SQLAlchemy()
mail_: Mail = Mail()
argon2_: PasswordHasher = PasswordHasher()
csrf_: CSRFProtect = CSRFProtect()
login_manager_: LoginManager = LoginManager()
migrater_: Migrate = Migrate()
limiter_ = Limiter(
        get_remote_address,
        app=current_app,
        default_limits=SERVER.DEFAULT_LIMITS,
        storage_uri=SERVER.LIMITER_URI,
    )
session_ = Session()
flow_ = Flow.from_client_secrets_file(
        client_secrets_file=PATH.CLIENTS_SECRETS,
        scopes=["https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri="http://localhost:5000/callback"
    )
serializer_ = URLSafeTimedSerializer(os.environ.get("FLASK_KEY"))
compress_ = Compress()

# Current problematic format might look like:
formatter = logging.Formatter('%(asctime)s - %(user)s - %(levelname)s - %(message)s')

# Should be changed to either:
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Or if you want to keep user logging, add a default:
class CustomFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'user'):
            record.user = 'system'  # or whatever default you want
        return super().format(record)

formatter = CustomFormatter('%(asctime)s - %(user)s - %(levelname)s - %(message)s')
