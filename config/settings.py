from dataclasses import dataclass, field
import os
import pathlib
import pycountry
import string
import pytz


@dataclass
class Directory:
    # Server
    SERVER: os.path = os.path.join(pathlib.Path(__file__).parent.parent)
    SRC: os.path = os.path.join(SERVER, "src")
    CONFIG: os.path = os.path.join(SERVER, "config")
    DB: os.path = os.path.join(SERVER, "db")
    WEBASSETS: os.path = os.path.join(SRC, "static", ".webassets-cache")
    # Images
    IMAGES: os.path = os.path.join(SRC, "static", "images")
    UPLOAD: os.path = os.path.join(SRC, "uploads")
    PROFILE_PICS: os.path = os.path.join(UPLOAD, "profile_pictures")
    PROFILE_ICONS: os.path = os.path.join(UPLOAD, "profile_icons")
    # Auth
    ROUTES: os.path = os.path.join(SRC, "routes")
    # News
    # Bakery
    BAKERY: os.path = os.path.join(IMAGES, "bakery")
    BREAD: os.path = os.path.join(BAKERY, "bread")
    SMALL_BREAD: os.path = os.path.join(BAKERY, "small_bread")
    STOKBROOD: os.path = os.path.join(BAKERY, "stokbrood")
    SAVORY: os.path = os.path.join(BAKERY, "savory")
    PASTRY: os.path = os.path.join(BAKERY, "pastry")
    SWEETS: os.path = os.path.join(BAKERY, "sweets")
    BAKERY_HEALTH: os.path = os.path.join(BAKERY, "health")
    # Schedule
    SCHEDULE: os.path = os.path.join(ROUTES, "schedule")
    # Admin
    ADMIN: os.path = os.path.join(ROUTES, "admin")


@dataclass
class Path:
    DB: os.path = os.path.join(Directory.DB, "server.db")
    CLIENTS_SECRETS: os.path = os.path.join(Directory.CONFIG, "client_secret.json")
    EMPLOYEES: os.path = os.path.join(Directory.SCHEDULE, "employees.json")


@dataclass
class Server:
    DATABASE_URI = f"sqlite:///{Path.DB}"
    LIMITER_URI = "memory://"
    DEFAULT_LIMITS = ["9999 per day", "999 per hour"]
    CET: pytz.timezone = pytz.timezone('CET')
    EMAIL: str = os.environ.get("GMAIL_EMAIL")

    MAX_IMAGE_FILE_SIZE: int = 2 * 1024 * 1024
    ALLOWED_FILE_EXTENSIONS: list[str] = field(
        default_factory=lambda: ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"]
    )
    TOKEN_EXPIRATION: int = 3600

    LOG_ROUTE = "route"
    LOG_LOCATION = "location"

    VERIFIED_ROLE: str = "verified"
    ADMIN_ROLE: str = "admin"
    NEWS_ROLE: str = "news"
    EMPLOYEE_ROLE: str = "employee"
    USER_ROLES: list[str] = field(
        default_factory=lambda: ["verified", "admin", "news", "employee"]
    )
    
    NORMAL_LOGIN: str = "normal_login"
    FAST_LOGIN: str = "fast_login"
    GOOGLE_LOGIN: str = "google_login"

    PASSWORD_VERIFICATION: str = "PASSWORD_VERIFICATION"
    EMAIL_VERIFICATION: str = "EMAIL_VERIFICATION"
    EMPLOYEE_VERIFICATION: str = "EMPLOYEE_VERIFICATION"

    EMAIL_REGEX: str = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    BANNED_WORDS: list[str] = field(
        default_factory=lambda: ["forbidden", "admin", "server"]
    )
    BANNED_CHARS: list[str] = field(
        default_factory=lambda: ["|"]
    )


@dataclass
class Template:
    # Auth
    LOGIN: str = "/auth/login.html"
    REGISTER: str = "/auth/register.html"
    SET_PASSWORD: str = "/auth/set_password.html"
    REQUEST_RESET: str = "/auth/request_reset.html"
    RESET_PASSWORD: str = "/auth/reset_password.html"

    HOME: str = "/news/all.html"
    # News
    ALL_NEWS: str = "/news/all.html"
    NEWS: str = "/news/news.html"
    # Bakery
    BAKERY: str = "/bakery/bakery.html"
    PROGRAMS: str = "/bakery/programs.html"
    INFO: str = "/bakery/info.html"
    SEARCH: str = "/bakery/search.html"
    # Schedule
    PERSONAL: str = "/schedule/personal.html"
    CALENDAR: str = "/schedule/calendar.html"
    # User admin
    USER_ADMIN: str = "/admin/user_admin.html"
    VERIFY_EMAIL: str = "/admin/verify_email.html"
    # Admin
    ADD_NEWS: str = "/news/add.html"
    DELETE_NEWS: str = "/news/delete.html"
    DELETE_BAKERY: str = "/bakery/delete.html"
    EMAIL_TEMPLATE: str = "/admin/email.html"
    # Errors
    E_400: str = "/errors/400.html"
    E_401: str = "/errors/401.html"
    E_403: str = "/errors/403.html"
    E_404: str = "/errors/404.html"
    E_500: str = "/errors/500.html"


@dataclass
class Redirect:
    # Auth
    LOGIN: str = "auth.login"
    REGISTER: str = "auth.register"
    SET_PASSWORD: str = "auth.set_password"
    REQUEST_RESET: str = "auth.request_reset"
    RESET_PASSWORD: str = "auth.reset_password"
    # News
    ALL_NEWS: str = "news.all"
    NEWS: str = "news.news"
    HOME: str = "news.all"
    # Bakery
    BAKERY: str = "bakery.bakery"
    PROGRAMS: str = "bakery.programs"
    DELETE_BAKERY: str = "bakery.delete"
    SEARCH: str = "bakery.search"
    # Schedule
    SCHEDULE: str = "schedule.personal"
    VERIFY_EMPLOYEE: str = "schedule.verify_employee"
    # User admin
    USER_ADMIN: str = "admin.user_admin"
    VERIFY_EMAIL: str = "admin.verify_email"
    # Admin
    DELETE_NEWS: str = "news.delete"
    # Errors
    E_400: str = "errors.400"
    E_401: str = "errors.401"
    E_403: str = "errors.403"
    E_404: str = "errors.404"
    E_498: str = "errors.498"
    E_500: str = "errors.500"


@dataclass
class Message:
    # Auth
    LOGIN_SUCCESS: str = "Logged in successfully"
    LOGOUT_SUCCESS: str = "Logged out successfully"
    FAST_LOGIN_FAILED: str = "Fast login failed"
    CREATE_ACCOUNT: str = "Create an account first"
    PASSWORD_RESET_SEND: str = "If email exists, a password reset email has been sent!"
    PASSWORD_UPDATE: str = "Your password has been updated!"
    EMAIL_TAKEN: str = "Email taken"
    INVALID_EMAIL: str = "Invalid email"
    USERNAME_TAKEN: str = "Username taken"
    PWD_MATCH: str = "Passwords must match"
    FAST_NAME_TAKEN: str = "Fast name taken"
    FAST_CODE_ERROR: str = "Must be numeric"
    SPECIAL_CHAR: str = "Special character required"
    CAPITAL_LETTER: str = "Capital letter required"
    LOWER_LETTER: str = "Lower case letter required"
    # News
    COMMENT_SUCCESS: str = "Comment submitted successfully!"
    # Bakery
    # Schedule
    EMPLOYEE_VERIFICATION_SEND: str = "If email exists, an employee verification email has been sent!"
    EMPLOYEE_VERIFIED: str = "Your employee account has been verified!"
    EMPLOYEE_NAME_ERROR: str = "Name must match name on schedule"
    EMPLOYEE_NOT_FOUND: str = "Employee not found: "
    # User admin
    VERIFICATION_SEND: str = "If email exists, a verification email has been sent!"
    EMAIL_VERIFIED: str = "Your email has been verified!"
    CHECK_INBOX: str = "Check inbox for email verification!"
    NO_CHANGES: str = "No changes made"
    UPDATED_DATA: str = "Updated data"
    PROFILE_PICTURE_ERROR: str = "Error saving profile picture"
    DISPLAY_NAME_TAKEN: str = "Display name taken"
    INVALID_PROFILE_ICON: str = "Invalid profile icon"
    # Admin
    NEWS_CODE_LENGTH_ERROR: str = "Must be 3 digits"
    NEWS_CODE_NUMERIC_ERROR: str = "Must be numeric"
    # Errors
    REQUIRED_FIELD: str = "Field is required"
    NOT_AUTHORIZED: str = "You tried to access a page you are not authorized to."
    TOKEN_ERROR: str = "Token authentication failed"
    STATE_ERROR: str = "State authentication failed"
    SESSION_ERROR: str = "Session authentication failed"
    AUTHENTICATION_LINK_ERROR: str = "Authentication link invalid or expired"
    CREDENTIALS_ERROR: str = "Incorrect credentials"
    VERIFICATION_ERROR: str = "Verification error"
    UNEXPECTED_ERROR: str = "Unexpected error"
    FORBIDDEN_WORD: str = "Banned word: "
    FORBIDDEN_CHAR: str = "Banned character: "
    FILE_EXTENSION_ERROR: str = "Invalid file extension"
    FILE_SIZE_ERROR: str = f"Max. file size: {Server.MAX_IMAGE_FILE_SIZE // (1024)} kb"


@dataclass
class Form:
    # Auth
    REQUIRED_SYMBOLS: str = string.punctuation + string.digits
    REGISTER: str = "register_form"
    LOGIN: str = "login_form"
    FAST_LOGIN: str = "fast_login_form"
    REQUEST_RESET: str = "request_reset_form"
    SET_PASSWORD: str = "set_password_form"
    RESET_PASSWORD: str = "reset_password_form"
    # News
    COMMENT: str = "comment_form"
    # Bakery
    BAKERY_SEARCH: str = "bakery_search_form"
    BAKERY_REFINE_SEARCH: str = "bakery_refine_search_form"
    NUTRI_CHOICES: list[tuple[str, str]] = field(
        default_factory=lambda: [("", "Nutri score"), ("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"), ("E", "E")]
    )
    # Schedule
    SCHEDULE_REQUEST: str = "schedule_request_form"
    ADD_EMPLOYEE: str = "add_employee_form"
    SCALENDAR_FORM_TYPE: str = "calendar_form"
    # User admin
    VERIFY: str = "verify_form"
    AUTHENTICATION: str = "authentication_form"
    PROFILE: str = "profile_form"
    NOTIFICATIONS: str = "notifications_form"
    COUNTRY_CHOICES: list[str] = field(
        default_factory=lambda: [country.name for country in pycountry.countries]
    )
    # Admin
    # Errors

    # Auth
    MIN_EMAIL: int = 10
    MAX_EMAIL: int = 50
    MIN_USERNAME: int = 4
    MAX_USERNAME: int = 20
    MIN_PASSWORD: int = 6
    MAX_PASSWORD: int = 18
    MIN_FAST_NAME: int = 4
    MAX_FAST_NAME: int = 10
    FAST_CODE_LENGTH: int = 5
    # News
    MIN_NEWS_HEADER: int = 3
    MAX_NEWS_HEADER: int = 24
    MIN_NEWS_TITLE: int = 3
    MAX_NEWS_TITLE: int = 55
    NEWS_CODE_LENGTH: int = 3
    MIN_NEWS_IMPORTANT: int = 10
    MAX_NEWS_IMPORTANT: int = 400
    MIN_NEWS: int = 4
    MAX_NEWS: int = 10_000

    MIN_COMMENT: int = 10
    MAX_COMMENT: int = 1_000
    # Bakery
    # Schedule
    # User admin
    MIN_ABOUT_ME: int = 10
    MAX_ABOUT_ME: int = 1_000
    # Admin
    # Errors


DIR = Directory()
PATH = Path()
SERVER = Server()
TEMPLATE = Template()
REDIRECT = Redirect()
MESSAGE = Message()
FORM = Form()