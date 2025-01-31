import inspect
import os
import sys

from datetime import datetime
from flask_login import current_user

from config.settings import PATH, SERVER, COLOR


class Logger:
    def __init__(self, logger):
        self.logger = logger
        self.logger.remove()
        if os.environ.get("FLASK_ENV") != "deploy":
            self._configure_file_logging()
        
        self._configure_console_logging()


    def _configure_file_logging(self):
        """
        Configure file logging.
        """
        file_path = PATH.LOGS
        if not os.path.exists(file_path):
            open(file_path, "w").close()
        self.logger.add(
            file_path,
            format="{message}",
            rotation="100 KB",
            retention="10 days",
            encoding="utf-8",
            enqueue=True,
            mode="a",
            level="TRACE"
        )
    
    def _configure_console_logging(self):
        if os.environ.get("FLASK_ENV") != "deploy":
            self.logger.add(sys.stderr,
                            format="{message}",
                            level="TRACE")
        else:
            self.logger.add(sys.stderr,
                            format="{message}<",
                            level="INFO")
    
    def _get_stack_trace(self):
        caller = inspect.stack()[1]
        frame = caller.frame.f_back
        name = frame.f_globals["__name__"]
        function = frame.f_code.co_name
        line = frame.f_lineno
        stack_trace = f"{name}.{function}:{line}"
        return stack_trace
    
    def _get_user(self, user: str | None = None):
        if user is None:
            if current_user and current_user.is_authenticated:
                username = current_user.username
                user_id = str(current_user.id).zfill(3)
                user_str = f"[{user_id:<3}] {username:<15}"
                return user_str

        username = "Anonymous"
        user_id = "[...]"
        user_str = f"{user_id} {username:<15}"
        return user_str
    
    def _format_message(self, level, user, message):
        """Format the log message with timestamp and level."""
        time_str = datetime.now(SERVER.CET).strftime("%Y-%m-%d %H:%M:%S")
        if level == "TRACE":
            return f"{COLOR.TRACE}   {time_str} | TRACE    | {user} | {message} {COLOR.RESET}"
        elif level == "DEBUG":
            return f"{COLOR.DEBUG}   {time_str} | DEBUG    | {user} | {message} {COLOR.RESET}"
        elif level == "INFO":
            return f"{COLOR.INFO}   {time_str} | INFO     | {user} | {message} {COLOR.RESET}"
        elif level == "SUCCESS":
            return f"{COLOR.SUCCESS}   {time_str} | SUCCESS  | {user} | {message} {COLOR.RESET}"
        elif level == "WARNING":
            return f"{COLOR.WARNING}   {time_str} | WARNING  | {user} | {message} {COLOR.RESET}"
        elif level == "ERROR":
            return f"{COLOR.ERROR}   {time_str} | ERROR    | {user} | {message} {COLOR.RESET}"
        elif level == "CRITICAL":
            return f"{COLOR.CRITICAL}   {time_str} | CRITICAL | {user} | {message} {COLOR.RESET}"
        elif level == "EXCEPTION":
            return f"{COLOR.EXCEPTION}   {time_str} | EXCEPTION| {user} | {message} {COLOR.RESET}"
    

    def _get_log_message(self, level, message, user: str | None = None):
        origin = self._get_stack_trace()
        user = self._get_user(user)
        formatted_message = self._format_message(level, user, message)
        return formatted_message

    def trace(self, message: str, user: str | None = None):
        """Log a trace message with user context."""
        log = self._get_log_message("TRACE", message, user)
        self.logger.trace(log)
    
    def debug(self, message: str, user: str | None = None):
        """Log a debug message with user context."""
        log = self._get_log_message("DEBUG", message, user)
        self.logger.debug(log)

    def info(self, message: str, user: str | None = None):
        """Log an info message with user context."""
        log = self._get_log_message("INFO", message, user)
        self.logger.info(log)

    def success(self, message: str, user: str | None = None):
        """Log a success message with user context."""
        log = self._get_log_message("SUCCESS", message, user)
        self.logger.success(log)

    def warning(self, message: str, user: str | None = None):
        """Log a warning message with user context."""
        log = self._get_log_message("WARNING", message, user)
        self.logger.warning(log)

    def error(self, message: str, user: str | None = None):
        """Log an error message with user context."""
        log = self._get_log_message("ERROR", message, user)
        self.logger.error(log)

    def critical(self, message: str, user: str | None = None):
        """Log a critical message with user context."""
        log = self._get_log_message("CRITICAL", message, user)
        self.logger.critical(log)

    def exception(self, message: str, user: str | None = None):
        """Log an exception message with user context."""
        log = self._get_log_message("EXCEPTION", message, user)
        self.logger.exception(log)
