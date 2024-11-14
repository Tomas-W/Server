from logging.handlers import RotatingFileHandler
import logging
import os
from flask import request


def get_logging_routes():
    try:
        referrer = request.referrer.split('/')[-2:]
    except AttributeError:
        referrer = "Direct access"

    text = f"triggered at: {request.endpoint}, " \
           f"came from: {'.'.join(referrer)}"
    return text


def setup_logger():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=1024 * 1024,
        backupCount=5
    )

    formatter = logging.Formatter(
        "%(asctime)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger 