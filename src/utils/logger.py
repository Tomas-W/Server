import logging
import os
import sys
from flask import has_request_context, request, current_app
from flask_login import current_user
from logging.handlers import RotatingFileHandler
import inspect
import colorlog

class UserContextFilter(logging.Filter):
    """Filter that adds user context to log records"""
    def filter(self, record):
        if not hasattr(record, "user"):
            if has_request_context():
                try:
                    if current_user and hasattr(current_user, "username"):
                        record.user = current_user.username
                    else:
                        record.user = "Anonymous"
                except Exception:
                    record.user = "Anonymous"
            else:
                record.user = "CLI"
        return True

class ServerLogger:
    def __init__(self):
        """Initialize the logger without app to set it up in __init__.py."""
        self.app = None
    
    def _init_app(self, app):
        """Set up logger with Flask app"""
        self.app = app
        
        # Configure root logger to capture all logs
        root_logger = logging.getLogger()
        root_logger.handlers = []  # Clear any existing handlers
        
        # Configure Flask's logger
        flask_logger = logging.getLogger("flask.app")
        flask_logger.handlers = []
        
        # Create base formatter
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(user)-15s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # In development, use colored output for console
        console_formatter = formatter
        if app.config.get("FLASK_ENV") != "deploy":
            console_formatter = colorlog.ColoredFormatter(
                "%(log_color)s" + formatter._fmt,
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow", 
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                }
            )

        # Console handler writing to stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(UserContextFilter())
        root_logger.addHandler(console_handler)
        
        # In development, also log to file with non-colored output
        if app.config.get("FLASK_ENV") != "deploy":
            log_dir = app.config.get("LOG_DIR", "logs")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, app.config["LOG_FILE"]),
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)  # Use non-colored formatter for files
            file_handler.addFilter(UserContextFilter())
            root_logger.addHandler(file_handler)
        
        # Set log levels
        level = "DEBUG"
        root_logger.setLevel(level)
        
        # Prevent propagation to avoid duplicate logs
        app.logger.propagate = False
        flask_logger.propagate = False

        # Log startup message
        env = "Production" if os.environ.get("FLASK_ENV") == "deploy" else "Development"
        root_logger.info(f"Starting logging application in {env} mode")

    def _get_context(self):
        """Get current request context for logging"""
        context = {
            "method": "-",
            "url": "-",
            "remote_addr": "-",
            "custom_pathname": "-",
            "custom_lineno": 0,
            "custom_function": "-",
            "referrer": "-"
        }
        
        if has_request_context():
            try:
                context.update({
                    "method": request.method,
                    "url": request.url,
                    "remote_addr": request.remote_addr,
                    "referrer": request.referrer or "-"
                })
            except Exception:
                pass

        # Get caller information
        try:
            caller_frame = inspect.currentframe().f_back.f_back.f_back
            full_path = caller_frame.f_code.co_filename
            context["custom_lineno"] = caller_frame.f_lineno
            context["custom_function"] = caller_frame.f_code.co_name
            
            # Shorten pathname to Server/..
            server_index = full_path.find("Server\\")
            context["custom_pathname"] = (
                full_path[server_index:] if server_index != -1 else full_path
            )
        except Exception:
            pass
        
        return context

    def _log(self, level, msg, *args, **kwargs):
        """Internal logging method""" 
        show_location = kwargs.pop("location", False) or level >= logging.WARNING
        show_route = kwargs.pop("route", False) or level >= logging.WARNING

        extra = kwargs.get("extra", {})
        extra.update(self._get_context())
        kwargs["extra"] = extra
        
        complete_msg = msg % args if args else msg
        if show_location:
            complete_msg += (
                f"\n                     Location: "
                f"{extra['custom_pathname']}: {extra['custom_function']}: {extra['custom_lineno']}"
            )
        if show_route:
            complete_msg += (
                f"\n                     Route: {extra['method']} {extra['url']} "
                f"({extra['remote_addr']}) from {extra['referrer']}"
            )

        # Log only to root logger to avoid duplication
        logging.getLogger().log(level, complete_msg, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log(logging.CRITICAL, msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        kwargs["exc_info"] = True
        self._log(logging.ERROR, msg, *args, **kwargs)
