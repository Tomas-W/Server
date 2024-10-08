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
banned_words_list: list = []
banned_characters_list: list = []

banned_news_words: list = []
banned_news_chars: list = []

required_password_symbols: str = string.punctuation + string.digits

# Errors

