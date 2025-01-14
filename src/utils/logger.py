import colorlog
import logging
import os
import uuid

from flask import (
    g,
    has_request_context,
    request,
)
from flask_login import current_user
from logging.handlers import RotatingFileHandler

from config.settings import SERVER


class LoggingFormatter(logging.Formatter):
    """
    Adds and formats logging messages with optionals.
    - Base format: [timestamp] [level] [user] - [message]
    - 'location': [module] [function] [line]
    - 'route': [method] [url] [remote_addr]
    - 'exc_info': [stack trace]
    Usage:
    logger.level("Message", location=bool, route=bool, exc_info=bool)
    """
    
    def __init__(self, **kwargs):
        self.base_format = '[%(asctime)s] %(levelname)-8s %(user)-15s - %(message)s'
        self.location_format = '\nLocation: %(module)s.%(function)s:%(line)d'
        self.route_format = '\nRoute: %(method)-7s %(url)s (%(remote_addr)s)'
        super().__init__(self.base_format, datefmt=kwargs.get('datefmt'))

    def format(self, record):
        self._add_base_context(record)
        fmt = self.base_format

        if getattr(record, SERVER.LOG_LOCATION, False):
            self._add_location_context(record)
            fmt += self.location_format
        
        if getattr(record, SERVER.LOG_ROUTE, False):
            self._add_route_context(record)
            fmt += self.route_format

        formatter = logging.Formatter(fmt, datefmt=self.datefmt)
        return formatter.format(record)

    def _add_base_context(self, record):
        """Base context: [timestamp] [level] [user] - [message]"""
        if has_request_context():
            record.user = current_user.username if hasattr(current_user, 'username') else 'Anonymous'
            record.request_id = getattr(g, 'request_id', '-')
        else:
            record.user = '-'
            record.request_id = '-'

    def _add_location_context(self, record):
        """Location context: [module] [function] [line]"""
        record.function = record.funcName
        record.line = record.lineno
        record.module = record.module

    def _add_route_context(self, record):
        """Route context: [method] [url] [remote_addr]"""
        if has_request_context():
            record.url = request.url
            record.method = request.method
            record.remote_addr = request.remote_addr
        else:
            record.url = '-'
            record.method = '-'
            record.remote_addr = '-'


class ServerLogger:
    def __init__(self):
        """Initialize logger without Flask app"""
        self.app = None
    
    def _init_app(self, app):
        """Set up logger with Flask app"""
        self.app = app
        self._load_config()
        self._configure_dirs()
        self._configure_handlers()
        self._setup_request_tracking()

    def _load_config(self):
        """Load logging configuration from Flask app config"""
        self.log_dir = self.app.config.get('LOG_DIR', 'logs')
        self.log_date_format = self.app.config.get('LOG_DATE_FORMAT', '%d-%m %H:%M:%S')
        self.log_max_bytes = self.app.config.get('LOG_MAX_BYTES', 10485760)
        self.log_backup_count = self.app.config.get('LOG_BACKUP_COUNT', 5)
        self.log_level = self.app.config.get('LOG_LEVEL', 'INFO')
        self.log_colors = self.app.config.get('LOG_COLORS', {
            "DEBUG": "blue",
            "INFO": "green", 
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        })

    def _configure_dirs(self):
        """Create log directory if it doesn't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _configure_handlers(self):
        """Set up and configure logging handlers"""
        file_handler = self._create_file_handler()
        console_handler = self._create_console_handler()
        
        level = getattr(logging, self.log_level.upper())
        for handler in (file_handler, console_handler):
            handler.setLevel(level)
        self.app.logger.setLevel(level)

        self.app.logger.handlers = []
        self.app.logger.addHandler(file_handler)
        self.app.logger.addHandler(console_handler)

    def _create_file_handler(self):
        """Create and configure the file handler"""
        handler = RotatingFileHandler(
            os.path.join(self.log_dir, self.app.config['LOG_FILE']),
            maxBytes=self.log_max_bytes,
            backupCount=self.log_backup_count
        )
        handler.setFormatter(LoggingFormatter(datefmt=self.log_date_format))
        return handler

    def _create_console_handler(self):
        """Create and configure the console handler"""
        handler = logging.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            "%(log_color)s[%(asctime)s] %(levelname)-8s %(user)-15s - %(message)s"
            "%(reset)s%(location_log)s%(route_log)s",
            datefmt=self.log_date_format,
            log_colors=self.log_colors,
            secondary_log_colors={
                'location': self.log_colors,
                'route': self.log_colors
            }
        ))
        return handler

    def _setup_request_tracking(self):
        """Configure request ID tracking"""
        @self.app.before_request
        def before_request():
            g.request_id = str(uuid.uuid4())[0:4]

    def _log(self, level, msg, *args, location=None, route=None, **kwargs):
        """Internal logging method that handles additional context flags"""
        try:
            if 'extra' not in kwargs:
                kwargs['extra'] = {}
            
            kwargs['extra'].update({
                SERVER.LOG_LOCATION: location,
                SERVER.LOG_ROUTE: route
            })
            
            self.app.logger.log(level, msg, *args, **kwargs)
        except Exception as e:
            # Fallback to basic logging if something goes wrong
            print(f"Logging failed: {e}")
            print(f"Original message: {msg}")

    def debug(self, msg, *args, location=None, route=None, **kwargs):
        """Log debug message"""
        self._log(logging.DEBUG, msg, *args, location=location, route=route, **kwargs)

    def info(self, msg, *args, location=None, route=None, **kwargs):
        """Log info message"""
        self._log(logging.INFO, msg, *args, location=location, route=route, **kwargs)

    def warning(self, msg, *args, location=None, route=None, **kwargs):
        """Log warning message"""
        self._log(logging.WARNING, msg, *args, location=location, route=route, **kwargs)

    def error(self, msg, *args, location=None, route=None, **kwargs):
        """Log error message"""
        self._log(logging.ERROR, msg, *args, location=location, route=route, **kwargs)

    def critical(self, msg, *args, location=None, route=None, **kwargs):
        """Log critical message"""
        self._log(logging.CRITICAL, msg, *args, location=location, route=route, **kwargs)

    def exception(self, msg, *args, exc_info=True, location=True, route=True, **kwargs):
        """Log exception with stack trace"""
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        kwargs['extra'].update({
            SERVER.LOG_LOCATION: location,
            SERVER.LOG_ROUTE: route
        })
        self.app.logger.exception(msg, *args, exc_info=exc_info, **kwargs)
