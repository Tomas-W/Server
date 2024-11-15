import inspect
import os
import logging

import colorlog
from flask import request
from logging.handlers import RotatingFileHandler



def log_routes():
    try:
        referrer = request.referrer.split('/')[-2:]
        referrer = ".".join(referrer)
    except AttributeError:
        referrer = "Direct access"

    return f"route[{referrer} >> {request.endpoint}]"


def log_function():
    function_name = inspect.currentframe().f_back.f_code.co_name
    return f"func[{function_name}]"


def setup_logger():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.ans"),
        maxBytes=1024 * 1024,
        backupCount=5
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
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
        datefmt="%H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger 