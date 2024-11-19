import os
import logging
import inspect
import colorlog
from flask import request, session
from flask_login import current_user
from logging.handlers import RotatingFileHandler


class Logger:
    def __init__(self, name="app", log_dir="logs", log_file="app.log"):
        self.log = logging.getLogger(name)
        self.log.setLevel(logging.INFO)
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, log_file),
            maxBytes=1024 * 1024,
            backupCount=5
        )
        
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%d-%m %H:%M:%S",
            log_colors={
                "DEBUG": "white",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            }
        ))
        
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%d-%m %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        
        self.log.addHandler(file_handler)
        self.log.addHandler(stream_handler)
    
    def get_log_info(self):
        return (self.get_log_trigger(),
                self.get_log_user(),
                self.get_log_routes())
    
    def get_log_trigger(self):
        log_trigger = session.pop("log_trigger", None)
        if log_trigger:
            return f"TRIGGER[{log_trigger}]"
        return f"TRIGGER[{inspect.currentframe().f_back.f_code.co_name}]"
    
    def get_log_user(self):
        if current_user.is_authenticated:
            return f"USER[{current_user.id} {current_user.username}]"        
        return "USER[Anonymous]"

    def get_log_routes(self):
        try:
            referrer = request.referrer.split('/')[-2:]
            referrer = ".".join(referrer)
        except AttributeError:
            referrer = "Direct access"
        return f"ROUTE[{referrer} >> {request.endpoint}]"

    def get_errors(self, error):
        error_msg = session.pop("error_msg", None)
        if error_msg is None:
            error_msg = str(error).split("\n")[0].split(":")[0]
        errors = f"{error_msg} - {self.get_log_info()}"
        
        return errors
    
    @staticmethod
    def get_user_info():
        return session.pop("error_user_info", None)
    
    @staticmethod
    def func_name():
        return f"FUNC[{inspect.currentframe().f_code.co_name}]"
