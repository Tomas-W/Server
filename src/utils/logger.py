import os
import uuid
import logging
import inspect
import colorlog
from flask import request, session, has_request_context, g
from flask_login import current_user
from logging.handlers import RotatingFileHandler
from functools import wraps


class RequestFormatter(logging.Formatter):
    """Custom formatter that adds request context to logs"""
    
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.method = request.method
            record.remote_addr = request.remote_addr
            record.request_id = getattr(g, 'request_id', '-')
            record.user = current_user.username if hasattr(current_user, 'username') else 'Anonymous'
        else:
            record.url = '-'
            record.method = '-'
            record.remote_addr = '-' 
            record.request_id = '-'
            record.user = '-'
            
        return super().format(record)


class ServerLogger:
    def __init__(self, app=None):
        """Initialize logger with optional Flask app"""
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize logger with Flask app"""
        self.app = app
        
        # Get config from Flask app
        log_dir = app.config.get('LOG_DIR', 'logs')
        log_date_format = app.config.get('LOG_DATE_FORMAT', '%d-%m %H:%M:%S')
        log_max_bytes = app.config.get('LOG_MAX_BYTES', 10485760)
        log_backup_count = app.config.get('LOG_BACKUP_COUNT', 5)
        log_colors = app.config.get('LOG_COLORS', {
            "DEBUG": "blue",
            "INFO": "green", 
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        })

        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Set up handlers
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, app.config['LOG_FILE']),
            maxBytes=log_max_bytes,
            backupCount=log_backup_count
        )
        
        console_handler = logging.StreamHandler()
        
        # Custom formatter with request context
        request_formatter = RequestFormatter(
            '[%(asctime)s] %(levelname)-8s [%(request_id)8s] %(user)-15s '
            '%(method)-7s %(url)s - %(message)s',
            datefmt=log_date_format
        )
        
        # Color formatter for console
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s[%(asctime)s] %(levelname)-8s [%(request_id)8s] "
            "%(user)-15s - %(message)s%(reset)s",
            datefmt=log_date_format,
            log_colors=log_colors
        )

        file_handler.setFormatter(request_formatter)
        console_handler.setFormatter(console_formatter)

        # Set levels based on environment
        if app.config['DEVELOPMENT']:
            file_handler.setLevel(logging.DEBUG)
            console_handler.setLevel(logging.DEBUG)
            app.logger.setLevel(logging.DEBUG)
        else:
            file_handler.setLevel(logging.WARNING)
            console_handler.setLevel(logging.WARNING)
            app.logger.setLevel(logging.WARNING)

        # Configure Flask logger
        app.logger.handlers = []
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)

        # Add request ID to each request
        @app.before_request
        def before_request():
            g.request_id = str(uuid.uuid4())[0:8]

    def debug(self, msg, *args, **kwargs):
        """Forward to app.logger.debug"""
        if self.app:
            self.app.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Forward to app.logger.info"""
        if self.app:
            self.app.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Forward to app.logger.warning"""
        if self.app:
            self.app.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Forward to app.logger.error"""
        if self.app:
            self.app.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """Forward to app.logger.critical"""
        if self.app:
            self.app.logger.critical(msg, *args, **kwargs)
