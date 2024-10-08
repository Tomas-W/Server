"""
Initializes the FlaskApp.

Sets general app settings as well as private variables,
    blueprints, databases.
"""
import os
from datetime import datetime

from flask import Flask
from flask_login import current_user

from src.cli import _auth_cli, _server_cli
from src.extensions import (server_db_, mail_, bootstrap_, csrf_,
                            login_manager_, migrater_, limiter_, session_)

from config.app_config import DebugConfig, DeployConfig, TestConfig
from config.settings import DATABASE_URI, LOGIN_VIEW, DB_FOLDER, CET
from src.utils.db_utils import update_user_last_seen


def _configure_server(app_: Flask, testing: bool = False) -> Flask:
    _configure_paths()
    environment = os.environ.get("FLASK_ENV", "debug").lower()

    if testing:
        config_obj = TestConfig()
    elif environment == "debug":
        config_obj = DebugConfig()
    elif environment == "deploy":
        config_obj = DeployConfig()
    else:
        raise ValueError(f"Expected 'debug' or 'deploy' but received '{environment}'")

    app_.config.from_object(config_obj)
    app_.config["INSTANCE"] = config_obj

    _configure_extensions(app_)
    _configure_blueprints(app_)
    _configure_requests(app_)
    _configure_cli(app_)
    _configure_database(app_)

    return app_


def _configure_paths() -> None:
    if not os.path.exists(DB_FOLDER):
        os.mkdir(DB_FOLDER)


def _configure_extensions(app_: Flask) -> None:
    server_db_.init_app(app_)
    mail_.init_app(app_)
    bootstrap_.init_app(app_)
    csrf_.init_app(app_)
    login_manager_.init_app(app_)
    login_manager_.login_view = LOGIN_VIEW
    migrater_.init_app(app_, server_db_)
    limiter_.init_app(app_)
    app_.config['SESSION_SQLALCHEMY'] = server_db_
    session_.init_app(app_)


def _configure_blueprints(app_: Flask) -> None:
    from src.home.home_routes import home_bp
    from src.auth.auth_routes import auth_bp
    from src.admin.admin_routes import admin_bp
    from src.bakery.bakery_routes import bakery_bp
    app_.register_blueprint(home_bp)
    app_.register_blueprint(auth_bp)
    app_.register_blueprint(admin_bp)
    app_.register_blueprint(bakery_bp)


def _configure_requests(app_: Flask) -> None:
    @app_.before_request
    def before_request():
        if current_user.is_authenticated:
            update_user_last_seen(current_user, datetime.now(CET))


def _configure_cli(app_: Flask) -> None:
    _auth_cli(app_)
    _server_cli(app_)


def _configure_database(app_: Flask) -> None:
    with app_.app_context():
        if not os.path.exists(DATABASE_URI):

            server_db_.create_all()


def get_app(testing: bool = False) -> Flask:
    app_: Flask = Flask(__name__.split('.')[0], template_folder="templates", static_folder="static")
    app_ = _configure_server(app_, testing=testing)    
    
    return app_
