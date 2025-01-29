import os
import time
import socket

from itsdangerous import URLSafeTimedSerializer
from flask import (
    Flask,
    send_from_directory,
)
from flask_assets import (
    Bundle,
    Environment,
)
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta
from flask_session import Session
from flask_migrate import upgrade
from sqlalchemy import inspect
from urllib.parse import urlparse

from src.extensions import (
    compress_,
    csrf_,
    limiter_,
    login_manager_,
    logger,
    mail_,
    migrater_,
    serializer_,
    init_serializer,
    server_db_,
    cache_,
)
from src.extensions_utils import (
    clear_webassets_cache,
    get_all_css_bundles,
)

from src.cli.user_cli import user_cli
from src.cli.news_cli import news_cli
from src.cli.schedule_cli import schedule_cli
from src.cli.server_cli import server_cli
from src.cli.bakery_cli import bakery_cli

from config.settings import (
    Environ,
    DIR,
    REDIRECT,
)
from config.app_config import (
    DebugConfig,
    DeployConfig,
)


def _configure_server(app_: Flask) -> Flask:
    """Configure the Flask application."""
    
    _configure_dirs(app_)
    _configure_variables(app_)
    
    # Add healthcheck endpoint
    @app_.route("/up")
    def healthcheck():
        return "OK", 200
    
    environment = os.environ.get("FLASK_ENV", "debug").lower()
    if environment == "debug":
        config_obj = DebugConfig()
        app_.config.update({"FLASK_DEBUG": "1"})

    elif environment == "deploy":
        config_obj = DeployConfig()
        app_.config.update({"FLASK_DEBUG": "0"})
    else:
        raise ValueError(f"Invalid FLASK_ENV value: '{environment}'. Expected 'debug' or 'deploy'")
    
    # Apply configuration
    app_.config.from_object(config_obj)
    app_.config["INSTANCE"] = config_obj

    _configure_extensions(app_)
    _configure_blueprints(app_)
    _configure_requests(app_)
    _configure_cli(app_)
    
    # Configure migrations
    app_.config['ALEMBIC'] = {
        'script_location': 'migrations',
        'compare_type': True
    }
    
    _configure_database(app_)
    _configure_url_rules(app_)
    _configure_jinja(app_)

    return app_


def _configure_dirs(app_: Flask) -> None:
    for folder in [DIR.DB, DIR.UPLOAD, DIR.PROFILE_PICS, DIR.PROFILE_ICONS]:
        if not os.path.exists(folder):
            os.makedirs(folder)

def _configure_variables(app_: Flask) -> None:
    try:
        app_.ENV = Environ.from_env()
    except ValueError as e:
        raise SystemExit(1)

    app_.config["SECRET_KEY"] = app_.ENV.FLASK_KEY.get_secret_value()
    app_.config["MAIL_USERNAME"] = app_.ENV.GMAIL_EMAIL.get_secret_value()
    app_.config["MAIL_PASSWORD"] = app_.ENV.GMAIL_PASS.get_secret_value()

def _configure_extensions(app_: Flask) -> None:
    logger._init_app(app_)
    server_db_.init_app(app_)
    
    # Configure cache
    cache_.init_app(app_, config={
        "CACHE_TYPE": "SimpleCache",  # Simple in-memory cache
        "CACHE_DEFAULT_TIMEOUT": 300  # 5 minutes default timeout
    })
    
    # Configure filesystem sessions
    app_.config.update({
        "SESSION_TYPE": "filesystem",
        "SESSION_FILE_DIR": DIR.DB,
        "SESSION_FILE_THRESHOLD": 500,  # Maximum number of sessions
        "PERMANENT_SESSION_LIFETIME": timedelta(days=7),
        "SESSION_PERMANENT": True,
        "SESSION_USE_SIGNER": True,
    })
    
    session = Session()
    session.init_app(app_)
    
    mail_.init_app(app_)
    csrf_.init_app(app_)
    login_manager_.init_app(app_)
    login_manager_.login_view = REDIRECT.LOGIN
    migrater_.init_app(app_, server_db_)
    limiter_.init_app(app_)
    
    assets_ = Environment(app_)
    _configure_css(assets_)
    app_.config["ASSETS_ROOT"] = os.path.join(app_.root_path, "static")
    app_.context_processor(lambda: {"assets": assets_})
    init_serializer(app_.ENV.FLASK_KEY.get_secret_value())
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


def _validate_database_url(url: str) -> bool:
    """Validate database URL format and connectivity"""
    try:
        result = urlparse(url)
        return all([
            result.scheme in ("postgresql", "postgres"),
            result.hostname,
            result.username,
            result.password,
            result.path
        ])
    except Exception as e:
        logger.error(f"Invalid database URL format: {e}")
        return False

def _test_network_connection(host, port):
    """Test raw TCP connection with DNS resolution"""
    try:
        # Try to resolve the hostname first
        if host == "web.railway.internal":
            # Use PGHOST environment variable as fallback
            actual_host = os.environ.get("PGHOST", host)
        else:
            actual_host = host

        logger.info(f"Attempting connection to {actual_host}:{port}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        result = sock.connect_ex((actual_host, int(port)))
        sock.close()
        return result == 0
    except Exception as e:
        logger.error(f"Network test failed for {actual_host}:{port} - {str(e)}")
        return False

def _configure_database(app_: Flask) -> None:
    """Configure database connection with network test"""
    logger.info("Starting database configuration...")
    logger.info("Environment Variables:")
    logger.info(f"PGUSER: {os.environ.get('PGUSER')}")
    logger.info(f"PGPASSWORD: {'*' * len(os.environ.get('PGPASSWORD', ''))}")  # Mask password
    logger.info(f"PGHOST: {os.environ.get('PGHOST')}")
    logger.info(f"PGPORT: {os.environ.get('PGPORT', '5432')}")
    logger.info(f"PGDATABASE: {os.environ.get('PGDATABASE')}")
    logger.info(f"DATABASE_PUBLIC_URL: {os.environ.get('DATABASE_PUBLIC_URL')}")
    logger.info(f"RAILWAY_PRIVATE_DOMAIN: {os.environ.get('RAILWAY_PRIVATE_DOMAIN')}")
    
    logger.info("AFTER AFTER")
    logger.info("Environment Variables:")
    logger.info(f"PGUSER: {os.environ.get('PGUSER')}")
    logger.info(f"PGPASSWORD: {'*' * len(os.environ.get('PGPASSWORD', ''))}")  # Mask password
    logger.info(f"PGHOST: {os.environ.get('PGHOST')}")
    logger.info(f"PGPORT: {os.environ.get('PGPORT', '5432')}")
    logger.info(f"PGDATABASE: {os.environ.get('PGDATABASE')}")
    logger.info(f"DATABASE_PUBLIC_URL: {os.environ.get('DATABASE_PUBLIC_URL')}")
    logger.info(f"RAILWAY_PRIVATE_DOMAIN: {os.environ.get('RAILWAY_PRIVATE_DOMAIN')}")

    # Get connection details from Railway's environment variables
    db_config = {
        "user": os.environ.get("PGUSER"),
        "password": os.environ.get("PGPASSWORD"),
        "host": os.environ.get("PGHOST"),
        "port": os.environ.get("PGPORT", "5432"),
        "database": os.environ.get("PGDATABASE")
    }
    
    # Validate required environment variables
    required_vars = ["PGUSER", "PGPASSWORD", "PGHOST", "PGDATABASE"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Log configuration (masked)
    logger.info(f"Database Configuration:")
    logger.info(f"Host: {db_config['host']}")
    logger.info(f"Port: {db_config['port']}")
    logger.info(f"Database: {db_config['database']}")
    logger.info(f"User: {'set' if db_config['user'] else 'not set'}")
    
    # Construct database URL with SSL mode
    db_url = (
        f"postgresql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}"
        f"/{db_config['database']}?sslmode=require"
    )
    
    # Update app configuration
    app_.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app_.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 180,
        "pool_size": 5,
        "max_overflow": 2,
        "connect_args": {
            "connect_timeout": 180,
            "keepalives": 1,
            "keepalives_idle": 60,
            "keepalives_interval": 20,
            "keepalives_count": 5,
            "application_name": "flask_app",
            "sslmode": "require"
        }
    }
    
    max_retries = 5
    retry_delay = 3
    
    for attempt in range(max_retries):
        try:
            with app_.app_context():
                # Test connection
                logger.info(f"Attempting database connection (attempt {attempt + 1}/{max_retries})...")
                server_db_.engine.connect()
                logger.info("Database connection successful!")
                return
                
        except Exception as e:
            logger.error(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            logger.info("setting new env")
            public_db_url = os.environ.get("DATABASE_PUBLIC_URL")
            public_host = public_db_url.split("@")[1].split(":")[0]
            logger.info(f"Setting RAILWAY_PRIVATE_DOMAIN to {public_host}")
            os.environ["RAILWAY_PRIVATE_DOMAIN"] = public_host

            if attempt < max_retries - 1:
                logger.info(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            else:
                logger.critical("All database connection attempts failed!")
                raise


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

def _configure_jinja(app_: Flask) -> None:
    app_.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app_.jinja_env.globals["REDIRECT"] = REDIRECT


def get_app() -> Flask:
    app_: Flask = Flask(
        import_name=__name__.split('.', maxsplit=1)[0],
        template_folder="templates",
        static_folder="static"
    )

    app_ = _configure_server(app_)
    clear_webassets_cache()

    with app_.app_context():
        # Check if the database is empty using inspect
        if not inspect(server_db_.engine).has_table('flask'):
            # Run migrations
            upgrade()  # This applies all migrations

    return app_
