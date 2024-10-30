import os
import pathlib
import string

import pytz

# Paths
SERVER_FOLDER: os.path = os.path.join(pathlib.Path(__file__).parent.parent)
SRC_FOLDER: os.path = os.path.join(SERVER_FOLDER, "src")
CONFIG_FOLDER: os.path = os.path.join(SERVER_FOLDER, "config")
DB_FOLDER: os.path = os.path.join(SERVER_FOLDER, "db")
DB_PATH: os.path = os.path.join(SERVER_FOLDER, "db", "server.db")
CLIENTS_SECRETS_PATH = os.path.join(CONFIG_FOLDER, "client_secret.json")
IMAGES_FOLDER = os.path.join(SRC_FOLDER, "static", "images")
BAKERY_IMAGES_FOLDER = os.path.join("IMAGES_FOLDER", "bakery")

# Bakery paths [relative]
BREAD_IMAGES_FOLDER = "images/bakery/bread/"
SMALL_BREAD_IMAGES_FOLDER = "images/bakery/small_bread/"
STOKBROOD_IMAGES_FOLDER = "images/bakery/stokbrood/"
SAVORY_IMAGES_FOLDER = "images/bakery/savory/"
PASTRY_IMAGES_FOLDER = "images/bakery/pastry/"
SWEETS_IMAGES_FOLDER = "images/bakery/sweets/"

# Server
LOGIN_VIEW = "auth.login"
DATABASE_URI = f"sqlite:///{DB_PATH}"
LIMITER_URI = "memory://"
DEFAULT_LIMITS = ["9999 per day", "999 per hour"]
CET = pytz.timezone('CET')

# Forms
banned_words_list: list = ["forbidden"]
banned_characters_list: list = ["^"]

MIN_COMMENT_LENGTH: int = 10
MAX_COMMENT_LENGTH: int = 1000
MIN_USERNAME_LENGTH: int = 4
MAX_USERNAME_LENGTH: int = 20
MIN_PASSWORD_LENGTH: int = 6
MAX_PASSWORD_LENGTH: int = 18
MIN_EMAIL_LENGTH: int = 10
MAX_EMAIL_LENGTH: int = 50
MIN_FAST_NAME_LENGTH: int = 4
MAX_FAST_NAME_LENGTH: int = 10
FAST_CODE_LENGTH: int = 5

MIN_NEWS_TITLE_LENGTH: int = 4
MAX_NEWS_TITLE_LENGTH: int = 80
MIN_NEWS_CONTENT_LENGTH: int = 10
MAX_NEWS_CONTENT_LENGTH: int = 10_000

MIN_COMMENT_TITLE_LENGTH: int = 4
MAX_COMMENT_TITLE_LENGTH: int = 25
MIN_COMMENT_LENGTH: int = 4
MAX_COMMENT_LENGTH: int = 1_000

# banned_news_words: list = []
# banned_news_chars: list = []

required_password_symbols: str = string.punctuation + string.digits

# Errors

