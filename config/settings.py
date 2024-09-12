import os
import pathlib
import string

# Paths
SERVER_PATH: os.path = os.path.join(pathlib.Path(__file__).parent.parent)
SRC_PATH: os.path = os.path.join(SERVER_PATH, "src")
CONFIG_PATH: os.path = os.path.join(SERVER_PATH, "config")
DB_PATH: os.path = os.path.join(SERVER_PATH, "db", "server.db")
CLIENTS_SECRETS_PATH = os.path.join(CONFIG_PATH, "client_secret.json")

# Server
LOGIN_VIEW = "auth.login"
DATABASE_URI = f"sqlite:///{DB_PATH}"
LIMITER_URI = "memory://"
DEFAULT_LIMITS = ["240 per day", "60 per hour"]

# Forms
banned_username_words: list = []
banned_username_chars: list = []

required_password_symbols: str = string.punctuation + string.digits
