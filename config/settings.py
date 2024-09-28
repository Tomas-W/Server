import os
import pathlib
import string

import pytz

# Paths
SERVER_PATH: os.path = os.path.join(pathlib.Path(__file__).parent.parent)
SRC_PATH: os.path = os.path.join(SERVER_PATH, "src")
CONFIG_PATH: os.path = os.path.join(SERVER_PATH, "config")
DB_PATH: os.path = os.path.join(SERVER_PATH, "db", "server.db")
CLIENTS_SECRETS_PATH = os.path.join(CONFIG_PATH, "client_secret.json")

# Server
LOGIN_VIEW = "auth.login2"
DATABASE_URI = f"sqlite:///{DB_PATH}"
LIMITER_URI = "memory://"
DEFAULT_LIMITS = ["9999 per day", "999 per hour"]
CET = pytz.timezone('CET')

# Forms
banned_username_words: list = []
banned_username_chars: list = []

banned_news_words: list = []
banned_news_chars: list = []

required_password_symbols: str = string.punctuation + string.digits
