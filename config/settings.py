import os
import pathlib
import pycountry
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

UPLOAD_FOLDER = os.path.join(SRC_FOLDER, "uploads")
PROFILE_PICTURES_FOLDER = os.path.join(UPLOAD_FOLDER, "profile_pictures")
PROFILE_ICONS_FOLDER = os.path.join(UPLOAD_FOLDER, "profile_icons")

BAKERY_IMAGES_FOLDER = os.path.join(IMAGES_FOLDER, "bakery")
BAKERY_HEALTH_IMAGES_FOLDER = os.path.join(BAKERY_IMAGES_FOLDER, "health")

ROUTES_FOLDER = os.path.join(SRC_FOLDER, "routes")
ADMIN_FOLDER = os.path.join(ROUTES_FOLDER, "admin")
SCHEDULE_FOLDER = os.path.join(ROUTES_FOLDER, "schedule")
SCHEDULE_PATH = os.path.join(SCHEDULE_FOLDER, "schedule.json")

# Bakery paths [relative]
BREAD_IMAGES_FOLDER = "images/bakery/bread/"
SMALL_BREAD_IMAGES_FOLDER = "images/bakery/small_bread/"
STOKBROOD_IMAGES_FOLDER = "images/bakery/stokbrood/"
SAVORY_IMAGES_FOLDER = "images/bakery/savory/"
PASTRY_IMAGES_FOLDER = "images/bakery/pastry/"
SWEETS_IMAGES_FOLDER = "images/bakery/sweets/"

# Server
DATABASE_URI = f"sqlite:///{DB_PATH}"
LIMITER_URI = "memory://"
DEFAULT_LIMITS = ["9999 per day", "999 per hour"]
CET: pytz.timezone = pytz.timezone('CET')
GMAIL_EMAIL: str = os.environ.get("GMAIL_EMAIL")

EMAIL_REGEX: str = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

MAX_IMAGE_FILE_SIZE: int = 2 * 1024 * 1024
ALLOWED_FILE_EXTENSIONS: list[str] = ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"]

TOKEN_EXPIRATION: int = 3600

banned_words_list: list[str] = ["forbidden", "admin", "server"]
banned_characters_list: list[str] = ["|"]

# Roles
VERIFIED_ROLE: str = "verified"
ADMIN_ROLE: str = "admin"
NEWS_ROLE: str = "news"
USER_ROLES: list[str] = [VERIFIED_ROLE, ADMIN_ROLE, NEWS_ROLE]

# Templates
HOME_PAGE_TEMPLATE: str = "/news/all.html"
LOGIN_TEMPLATE: str = "/auth/login.html"
REGISTER_TEMPLATE: str = "/auth/register.html"
SET_PASSWORD_TEMPLATE: str = "/auth/set_password.html"
REQUEST_RESET_TEMPLATE: str = "/auth/request_reset.html"
RESET_PASSWORD_TEMPLATE: str = "/auth/reset_password.html"

ALL_NEWS_TEMPLATE: str = "/news/all.html"
NEWS_TEMPLATE: str = "/news/news.html"
ADD_NEWS_TEMPLATE: str = "/news/add.html"
DELETE_NEWS_TEMPLATE: str = "/news/delete.html"
USER_ADMIN_TEMPLATE: str = "/admin/user_admin.html"
VERIFY_EMAIL_TEMPLATE: str = "/admin/verify_email.html"

BAKERY_TEMPLATE: str = "/bakery/bakery.html"
PROGRAMS_TEMPLATE: str = "/bakery/programs.html"
DELETE_BAKERY_TEMPLATE: str = "/bakery/delete.html"
INFO_TEMPLATE: str = "/bakery/info.html"
SEARCH_TEMPLATE: str = "/bakery/search.html"

SCHEDULE_TEMPLATE: str = "/schedule/today.html"
TODAY_TEMPLATE: str = "/schedule/today.html"

EMAIL_TEMPLATE: str = "/admin/email.html"
E_400_TEMPLATE: str = "/errors/400.html"
E_401_TEMPLATE: str = "/errors/401.html"
E_403_TEMPLATE: str = "/errors/403.html"
E_404_TEMPLATE: str = "/errors/404.html"
E_500_TEMPLATE: str = "/errors/500.html"

# Redirects
HOME_PAGE_REDIRECT: str = "news.all"
LOGIN_REDIRECT: str = "auth.login"
REGISTER_REDIRECT: str = "auth.register"
SET_PASSWORD_REDIRECT: str = "auth.set_password"
REQUEST_RESET_REDIRECT: str = "auth.request_reset"
RESET_PASSWORD_REDIRECT: str = "auth.reset_password"

BAKERY_REDIRECT: str = "bakery.bakery"
PROGRAMS_REDIRECT: str = "bakery.programs"
DELETE_BAKERY_REDIRECT: str = "bakery.delete"
SEARCH_REDIRECT: str = "bakery.search"

ALL_NEWS_REDIRECT: str = "news.all"
NEWS_REDIRECT: str = "news.news"
DELETE_NEWS_REDIRECT: str = "news.delete"
USER_ADMIN_REDIRECT: str = "admin.user_admin"
VERIFY_EMAIL_REDIRECT: str = "admin.verify_email"

# Errors
E_400_REDIRECT: str = "errors.400"
E_401_REDIRECT: str = "errors.401"
E_403_REDIRECT: str = "errors.403"
E_404_REDIRECT: str = "errors.404"
E_498_REDIRECT: str = "errors.498"
E_500_REDIRECT: str = "errors.500"

# Flash messages
NOT_AUTHORIZED_MSG: str = "You tried to access a page you are not authorized to."

LOGIN_SUCCESS_MSG: str = "Logged in successfully"
LOGOUT_SUCCESS_MSG: str = "Logged out successfully"
FAST_LOGIN_FAILED_MSG: str = "Fast login failed"
CREATE_ACCOUNT_MSG: str = "Create an account first"
VERIFICATION_SEND_MSG: str = "If email exists, a verification email has been sent!"
PASSWORD_RESET_SEND_MSG: str = "If email exists, a password reset email has been sent!"
EMAIL_VERIFIED_MSG: str = "Your email has been verified!"
PASSWORD_UPDATE_MSG: str = "Your password has been updated!"
CHECK_INBOX_MSG: str = "Check inbox for email verification!"
NO_CHANGES_MSG: str = "No changes made"
UPDATED_DATA_MSG: str = "Updated data"

TOKEN_ERROR_MSG: str = "Token authentication failed"
STATE_ERROR_MSG: str = "State authentication failed"
SESSION_ERROR_MSG: str = "Session authentication failed"
AUTHENTICATION_LINK_ERROR_MSG: str = "Authentication link invalid or expired"
CREDENTIALS_ERROR_MSG: str = "Incorrect credentials"
VERIFICATION_ERROR_MSG: str = "Verification error"
UNEXPECTED_ERROR_MSG: str = "Unexpected error"

PROFILE_PICTURE_ERROR_MSG: str = "Error saving profile picture"

COMMENT_SUCCESS_MSG: str = "Comment submitted successfully!"

# Forms
REQUIRED_SYMBOLS: str = string.punctuation + string.digits
COUNTRY_CHOICES: list[str] = [country.name for country in pycountry.countries]
NUTRI_CHOICES: list[tuple[str, str]] = [("", "Nutri score"), ("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"), ("E", "E")]


# Form types
REGISTER_FORM_TYPE: str = "register_form"
LOGIN_FORM_TYPE: str = "login_form"
FAST_LOGIN_FORM_TYPE: str = "fast_login_form"
REQUEST_RESET_FORM_TYPE: str = "request_reset_form"
SET_PASSWORD_FORM_TYPE: str = "set_password_form"
RESET_PASSWORD_FORM_TYPE: str = "reset_password_form"

VERIFY_FORM_TYPE: str = "verify_form"
AUTHENTICATION_FORM_TYPE: str = "authentication_form"
PROFILE_FORM_TYPE: str = "profile_form"
NOTIFICATIONS_FORM_TYPE: str = "notifications_form"
COMMENT_FORM_TYPE: str = "comment_form"

BAKERY_SEARCH_FORM_TYPE: str = "bakery_search_form"
BAKERY_REFINE_SEARCH_FORM_TYPE: str = "bakery_refine_search_form"

# Form messages
EMAIL_TAKEN_MSG: str = "Email taken"
INVALID_EMAIL_MSG: str = "Invalid email"
USERNAME_TAKEN_MSG: str = "Username taken"
PWD_MATCH_MSG: str = "Passwords must match"
FAST_NAME_TAKEN_MSG: str = "Fast name taken"
FAST_CODE_ERROR_MSG: str = "Must be numeric"

DISPLAY_NAME_TAKEN_MSG: str = "Display name taken"

SPECIAL_CHAR_MSG: str = "Special character required"
CAPITAL_LETTER_MSG: str = "Capital letter required"
LOWER_LETTER_MSG: str = "Lower case letter required"
FORBIDDEN_WORD_MSG: str = "Banned word: "
FORBIDDEN_CHAR_MSG: str = "Banned character: "
REQUIRED_FIELD_MSG: str = "Field is required"
FILE_EXTENSION_ERROR_MSG: str = "Invalid file extension"
FILE_SIZE_ERROR_MSG: str = f"Max. file size: {MAX_IMAGE_FILE_SIZE // (1024)} kb"

NEWS_CODE_LENGTH_ERROR_MSG: str = "Must be 3 digits"
NEWS_CODE_NUMERIC_ERROR_MSG: str = "Must be numeric"

MIN_EMAIL_LENGTH: int = 10
MAX_EMAIL_LENGTH: int = 50
MIN_USERNAME_LENGTH: int = 4
MAX_USERNAME_LENGTH: int = 20
MIN_PASSWORD_LENGTH: int = 6
MAX_PASSWORD_LENGTH: int = 18
MIN_FAST_NAME_LENGTH: int = 4
MAX_FAST_NAME_LENGTH: int = 10
FAST_CODE_LENGTH: int = 5

MIN_ABOUT_ME_LENGTH: int = 10
MAX_ABOUT_ME_LENGTH: int = 1_000

MIN_NEWS_HEADER_LENGTH: int = 3
MAX_NEWS_HEADER_LENGTH: int = 24
MIN_NEWS_TITLE_LENGTH: int = 3
MAX_NEWS_TITLE_LENGTH: int = 55
NEWS_CODE_LENGTH: int = 3
MIN_NEWS_IMPORTANT_LENGTH: int = 10
MAX_NEWS_IMPORTANT_LENGTH: int = 400
MIN_NEWS_LENGTH: int = 4
MAX_NEWS_LENGTH: int = 10_000

MIN_COMMENT_LENGTH: int = 10
MAX_COMMENT_LENGTH: int = 1_000

# Tokens
PASSWORD_VERIFICATION: str = "password_verification"
EMAIL_VERIFICATION: str = "email_verification"
