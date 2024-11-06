"""
Initializes the FlaskApp.

Sets general app settings as well as private variables,
    blueprints, databases.
"""
import os
from flask import Flask, send_from_directory, request
from flask_login import current_user
import secrets

from src.extensions import (server_db_, mail_, csrf_,
                            login_manager_, migrater_, limiter_, session_
)
from src.models.mod_utils import load_user

from src.cli import _auth_cli, _server_cli
from config.app_config import DebugConfig, DeployConfig, TestConfig
from config.settings import (DATABASE_URI, LOGIN_REDIRECT, DB_FOLDER,
                             PROFILE_ICONS_FOLDER, PROFILE_PICTURES_FOLDER,
                             BAKERY_HEALTH_IMAGES_FOLDER
)


HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Frame-Options": "SAMEORIGIN",
    "X-XSS-Protection": "1; mode=block",
    "X-Content-Type-Options": "nosniff",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "object-src 'none'; "
        "script-src 'self' 'nonce-{request.csp_nonce}' cdn.jsdelivr.net kit.fontawesome.com; "
        "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net fonts.googleapis.com ka-f.fontawesome.com; "
        "font-src 'self' fonts.gstatic.com ka-f.fontawesome.com; "
        "base-uri 'self'; "
        "require-trusted-types-for 'script';"
    ),
    "Referrer-Policy": "strict-origin-when-cross-origin"
}


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
    _configure_url_rules(app_)

    return app_


def _configure_paths() -> None:
    if not os.path.exists(DB_FOLDER):
        os.mkdir(DB_FOLDER)


def _configure_extensions(app_: Flask) -> None:
    server_db_.init_app(app_)
    mail_.init_app(app_)
    csrf_.init_app(app_)
    login_manager_.init_app(app_)
    login_manager_.login_view = LOGIN_REDIRECT
    migrater_.init_app(app_, server_db_)
    limiter_.init_app(app_)
    app_.config['SESSION_SQLALCHEMY'] = server_db_
    session_.init_app(app_)


def _configure_blueprints(app_: Flask) -> None:
    from src.routes.news.news_routes import news_bp
    from src.routes.auth.auth_routes import auth_bp
    from src.routes.admin.admin_routes import admin_bp
    from src.routes.bakery.bakery_routes import bakery_bp
    app_.register_blueprint(news_bp)
    app_.register_blueprint(auth_bp)
    app_.register_blueprint(admin_bp)
    app_.register_blueprint(bakery_bp)


def _configure_requests(app_: Flask) -> None:
    def handle_user_activity():
        if current_user.is_authenticated:
            current_user.update_last_seen()
    
    def make_nonce():
        if not getattr(request, 'csp_nonce', None):
            request.csp_nonce = secrets.token_urlsafe(18)[:18]
    
    def add_security_headers(resp):
        resp.headers.update(HEADERS)
        csp_header = resp.headers.get('Content-Security-Policy')
        if csp_header and 'nonce' not in csp_header:
            resp.headers['Content-Security-Policy'] = \
                csp_header.replace('script-src', f"script-src 'nonce-{request.csp_nonce}'")
        return resp
    
    app_.before_request(handle_user_activity)
    # app_.before_request(make_nonce)
    # app_.after_request(add_security_headers)


def _configure_cli(app_: Flask) -> None:
    _auth_cli(app_)
    _server_cli(app_)


def _configure_database(app_: Flask) -> None:
    with app_.app_context():
        if not os.path.exists(DATABASE_URI):

            server_db_.create_all()
    
def _configure_url_rules(app_: Flask) -> None:
    app_.add_url_rule("/uploads/profile_icons/<filename>",
                      endpoint="profile_icons_folder",
                      view_func=lambda filename: send_from_directory(
                          PROFILE_ICONS_FOLDER,
                          filename))
    app_.add_url_rule("/uploads/profile_pictures/<filename>",
                      endpoint="profile_picture_folder",
                      view_func=lambda filename: send_from_directory(
                          PROFILE_PICTURES_FOLDER,
                          filename))
    app_.add_url_rule("/static/images/bakery/health/<path:filename>",
                      endpoint="bakery_health_folder",
                      view_func=lambda filename: send_from_directory(
                          BAKERY_HEALTH_IMAGES_FOLDER,
                          filename))


def get_app(testing: bool = False) -> Flask:
    app_: Flask = Flask(
        import_name=__name__.split('.')[0],
        template_folder="templates",
        static_folder="static"
    )
    app_ = _configure_server(app_, testing=testing)    

    return app_


