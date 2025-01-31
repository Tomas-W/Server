import os
import sys
from loguru import logger
from flask import current_app
from flask_login import current_user

class Logger:
    def __init__(self):
        pass

    def _configure_logger(self):
        # Set up the log file and format
        log_file_path = os.path.join(current_app.root_path, "logs", "app.log")
        logger.add(
            log_file_path,
            format="{time} [{level:<8}] - {message}",
            rotation="100kb",
            retention="10 days"
        )
        
        # Set up console logging
        if current_app.config["DEBUG"]:
            logger.add(sys.stderr, level="DEBUG")
        else:
            logger.add(sys.stderr, level="INFO")
    
    def _get_context(self, message: str, user: str | None = None):
        if user is None:
            if current_user and current_user.is_authenticated:
                username = current_user.username
                user_id = str(current_user.id).zfill(3)
            else:
                username = "Anonymous"
                user_id = "..."
            return f"[{user_id:<3}]{username:<15} | {message}"
        else:
            return f"[{user}] | {message}"


    def info(self, message: str, user: str | None = None):
        """Log an info message with user context."""
        message = self._get_context(message, user)
        logger.info(message)
    
    def warning(self, message: str, user: str | None = None):
        """Log a warning message with user context."""
        message = self._get_context(message, user)
        logger.warning(message)

    def error(self, message: str, user: str | None = None):
        """Log an error message with user context."""
        message = self._get_context(message, user)
        logger.error(message)

    def debug(self, message: str, user: str | None = None):
        """Log a debug message with user context."""
        message = self._get_context(message, user)
        logger.debug(message)

    def exception(self, message: str, user: str | None = None):
        """Log an exception message with user context."""
        message = self._get_context(message, user)
        logger.exception(message)