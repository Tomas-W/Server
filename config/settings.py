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
CET: pytz.timezone = pytz.timezone('CET')

# Redirects
LOGIN_REDIRECT: str = "auth.login"
SET_PASSWORD_REDIRECT: str = "auth.set_password"
REQUEST_RESET_REDIRECT: str = "auth.request_reset"
RESET_PASSWORD_REDIRECT: str = "auth.reset_password"
REGISTER_REDIRECT: str = "auth.register"
ALL_NEWS_REDIRECT: str = "news.all_news"
USER_ADMIN_REDIRECT: str = "admin.user_admin"

# Flash
TOKEN_ERROR_MSG: str = "Token authentication failed"
STATE_ERROR_MSG: str = "State authentication failed"
SESSION_ERROR_MSG: str = "Session authentication failed"
AUTHENTICATION_LINK_ERROR_MSG: str = "Authentication link is invalid or has expired."
CREDENTIALS_ERROR_MSG: str = "Incorrect credentials"
VERIFICATION_ERROR_MSG: str = "Verification error"
UNEXPECTED_ERROR_MSG: str = "An unexpected error occurred"

LOGIN_SUCCESS_MSG: str = "Logged in successfully"
LOGOUT_SUCCESS_MSG: str = "Logged out successfully"
CREATE_ACCOUNT_MSG: str = "Create an account first"
VERIFICATION_SEND_MSG: str = "If email exists, a verification email has been sent!"
PASSWORD_RESET_SEND_MSG: str = "If email exists, a password reset email has been sent!"
EMAIL_VERIFIED_MSG: str = "Your email has been verified!"
PASSWORD_UPDATE_MSG: str = "Your password has been updated!"

# Forms
REGISTER_FORM_TYPE: str = "register_form"
LOGIN_FORM_TYPE: str = "login_form"
FAST_LOGIN_FORM_TYPE: str = "fast_login_form"
REQUEST_RESET_FORM_TYPE: str = "request_reset_form"
SET_PASSWORD_FORM_TYPE: str = "set_password_form"
RESET_PASSWORD_FORM_TYPE: str = "reset_password_form"
VERIFY_FORM_TYPE: str = "verify_form"
AUTHENTICATION_FORM_TYPE: str = "authentication_form"
NEWS_FORM_TYPE: str = "news_form"
COMMENT_FORM_TYPE: str = "comment_form"

banned_words_list: list[str] = ["forbidden"]
banned_characters_list: list[str] = ["^"]
required_password_symbols: str = string.punctuation + string.digits

PWD_MATCH_MSG: str = "Passwords must match"
REQUIRED_FIELD_MSG: str = "Field is required"
INVALID_EMAIL_MSG: str = "Invalid email"

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

# Tokens
PASSWORD_VERIFICATION: str = "password_verification"
EMAIL_VERIFICATION: str = "email_verification"
