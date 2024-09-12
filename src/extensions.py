from flask import current_app
from flask_mail import Mail
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from google_auth_oauthlib.flow import Flow
from argon2 import PasswordHasher

from config.settings import CLIENTS_SECRETS_PATH, DEFAULT_LIMITS, LIMITER_URI

server_db_: SQLAlchemy = SQLAlchemy()
mail_: Mail = Mail()
argon2_: PasswordHasher = PasswordHasher()
bootstrap_: Bootstrap = Bootstrap()
csrf_: CSRFProtect = CSRFProtect()
login_manager_: LoginManager = LoginManager()
migrater_: Migrate = Migrate()
limiter_ = Limiter(
        get_remote_address,
        app=current_app,
        default_limits=DEFAULT_LIMITS,
        storage_uri=LIMITER_URI,
    )
session_ = Session()
flow_ = Flow.from_client_secrets_file(
        client_secrets_file=CLIENTS_SECRETS_PATH,
        scopes=["https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri="http://localhost:5000/callback"
    )
