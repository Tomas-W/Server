import os
import secrets

from dotenv import load_dotenv
load_dotenv('.flaskenv')
from flask import Flask, send_from_directory
from flask_login import current_user
from flask_assets import Environment, Bundle
from sqlalchemy.exc import SQLAlchemyError

from config.app_config import DebugConfig, DeployConfig
from config.settings import DIR, REDIRECT

from src.extensions import (
    server_db_, mail_, csrf_, login_manager_, migrater_, limiter_, session_,
    logger, compress_
)
from src.models.mod_utils import load_user
from src.cli.user_cli import user_cli
from src.cli.news_cli import news_cli
from src.cli.schedule_cli import schedule_cli
from src.cli.server_cli import server_cli
from src.cli.bakery_cli import bakery_cli
from src.extensions_utils import clear_webassets_cache, get_all_css_bundles


def _configure_server(app_: Flask) -> Flask:
    """Configure the Flask application."""
    _configure_dirs(app_)
    
    # Get environment setting
    environment = os.environ.get("FLASK_ENV", "debug").lower()
    
    # Select configuration based on environment
    if environment == "debug":
        config_obj = DebugConfig()
        os.environ["FLASK_DEBUG"] = "1"
        app_.logger.warning("Detected debug environment")

    elif environment == "deploy":
        config_obj = DeployConfig()
        os.environ["FLASK_DEBUG"] = "0"
        app_.logger.warning("Detected deployment environment")
    else:
        raise ValueError(f"Invalid FLASK_ENV value: '{environment}'. Expected 'debug' or 'deploy'")

    # Apply configuration
    app_.config.from_object(config_obj)
    app_.config["INSTANCE"] = config_obj

    _configure_extensions(app_)
    _configure_blueprints(app_)
    _configure_requests(app_)
    _configure_cli(app_)
    _configure_database(app_)
    _configure_url_rules(app_)

    return app_


def _configure_dirs(app_: Flask) -> None:
    for folder in [DIR.DB, DIR.UPLOAD, DIR.PROFILE_PICS, DIR.PROFILE_ICONS]:
        if not os.path.exists(folder):
            os.makedirs(folder)


def _configure_extensions(app_: Flask) -> None:
    logger._init_app(app_)
    server_db_.init_app(app_)
    mail_.init_app(app_)
    csrf_.init_app(app_)
    login_manager_.init_app(app_)
    login_manager_.login_view = REDIRECT.LOGIN
    migrater_.init_app(app_, server_db_)
    limiter_.init_app(app_)
    app_.config['SESSION_SQLALCHEMY'] = server_db_
    session_.init_app(app_)
    assets_ = Environment(app_)
    _configure_css(assets_)
    app_.config['ASSETS_ROOT'] = os.path.join(app_.root_path, 'static')
    app_.context_processor(lambda: {"assets": assets_})
    compress_.init_app(app_)


def _configure_blueprints(app_: Flask) -> None:
    from src.routes.news.news_routes import news_bp
    from src.routes.auth.auth_routes import auth_bp
    from src.routes.admin.admin_routes import admin_bp
    from src.routes.bakery.bakery_routes import bakery_bp
    from src.routes.errors.error_routes import errors_bp
    from src.routes.schedule.schedule_routes import schedule_bp
    app_.register_blueprint(news_bp)
    app_.register_blueprint(auth_bp)
    app_.register_blueprint(admin_bp)
    app_.register_blueprint(bakery_bp)
    app_.register_blueprint(errors_bp)
    app_.register_blueprint(schedule_bp)


def _configure_requests(app_: Flask) -> None:
    def handle_user_activity():
        if current_user.is_authenticated:
            current_user.update_last_seen()

    def add_security_headers(resp):
        resp.headers.update(app_.config['SECURITY_HEADERS'])
        return resp

    def add_cache_control_headers(response):
        content_type = response.headers.get("Content-Type", "")
        if "application/javascript" in content_type or "image/" in content_type:
            response.cache_control.public = True
            response.cache_control.max_age = 3600 * 24 * 7
            response.expires = 3600 * 24 * 7
        elif "text/html" in content_type or "text/css" in content_type:
            response.cache_control.no_store = True
            response.cache_control.no_cache = True
            response.cache_control.max_age = 0
            response.expires = 0
        return response
    
    def manage_db_sessions(exception=None):
        if exception:
            server_db_.session.rollback()
            app_.logger.error(f"Database error: {exception}")
        else:
            try:
                server_db_.session.commit()
            except SQLAlchemyError as e:
                server_db_.session.rollback()
                app_.logger.error(f"Database commit failed: {e}")
            finally:
                server_db_.session.remove()

    app_.before_request(handle_user_activity)
    app_.after_request(add_security_headers)
    app_.after_request(add_cache_control_headers)
    app_.teardown_request(manage_db_sessions)


def _configure_cli(app_: Flask) -> None:
    user_cli(app_)
    schedule_cli(app_)
    news_cli(app_)
    bakery_cli(app_)
    server_cli(app_)


def _configure_database(app_: Flask) -> None:
    with app_.app_context():
        if not os.path.exists(DIR.DB):

            server_db_.create_all()


def _configure_url_rules(app_: Flask) -> None:
    app_.add_url_rule("/uploads/profile_icons/<filename>",
                      endpoint="profile_icons_folder",
                      view_func=lambda filename: send_from_directory(
                          DIR.PROFILE_ICONS,
                          filename))
    app_.add_url_rule("/uploads/profile_pictures/<filename>",
                      endpoint="profile_picture_folder",
                      view_func=lambda filename: send_from_directory(
                          DIR.PROFILE_PICS,
                          filename))
    app_.add_url_rule("/static/images/bakery/health/<path:filename>",
                      endpoint="bakery_health_folder",
                      view_func=lambda filename: send_from_directory(
                          DIR.BAKERY_HEALTH,
                          filename))


def _configure_css(assets_: Environment) -> None:
    css_bundle = get_all_css_bundles()
    for bundle in css_bundle:
        assets_.register(
            bundle["name"],
            Bundle(*bundle["files"],
                   filters=bundle["filters"],
                   output=bundle["output"])
        )


def get_app() -> Flask:
    app_: Flask = Flask(
        import_name=__name__.split('.', maxsplit=1)[0],
        template_folder="templates",
        static_folder="static"
    )
    app_ = _configure_server(app_)
    clear_webassets_cache()    
    return app_
