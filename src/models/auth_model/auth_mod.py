import glob
import os
import random

from datetime import datetime
from typing import Optional

from flask import (
    abort,
    session,
)
from flask_login import UserMixin
from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from wtforms.validators import ValidationError

from src.extensions import (
    argon2_,
    logger,
    server_db_,
)

from src.models.mod_utils import (
    set_updated_at,
)

from src.utils.form_utils import (
    DisplayNameLengthCheck,
    DisplayNameTakenCheck,
    EmailCheck,
    EmailTakenCheck,
    EmployeeNameCheck,
    FastCodeCheck,
    FastCodeLengthCheck,
    FastNameLengthCheck,
    PasswordCheck,
    PasswordLengthCheck,
    UsernameLengthCheck,
    UsernameTakenCheck,
)

from config.settings import (
    DIR,
    FORM,
    SERVER,
)


class AuthenticationToken(server_db_.Model):
    """
    Stores AuthenticationToken data for various authentication purposes.
    
    - ID (int): Identifier [Primary Key]
    - USER_EMAIL (str): User email [Optional]
    - TOKEN_TYPE (str): Type of token
    - TOKEN (str): Token
    - CREATED_AT (datetime): Timestamp of creation [Default]
    """
    __tablename__ = "authentication_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_email: Mapped[str] = mapped_column(String(75), nullable=True)
    token_type: Mapped[str] = mapped_column(String(32))
    token: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=lambda: datetime.now(SERVER.CET))
    
    def set_token(self, token: str) -> None:
        self.token = token


class User(server_db_.Model, UserMixin):
    """
    Stores the User data.

    - ID (int): Identifier [Primary Key]
    - EMAIL (str): User's email address [Unique]
    - USERNAME (str): User's username [Unique]
    - PASSWORD (str): User's hashed password
    - FAST_NAME (str): User's fast name [Unique] [Optional]
    - FAST_CODE (int): User's fast code [Optional]

    - DISPLAY_NAME (str): User's display name [Unique] [Optional]
    - COUNTRY (str): User's country [Optional]
    - PROFILE_ICON (str): User's profile icon [Optional]
    - PROFILE_PICTURE (str): User's profile picture [Optional]
    - ABOUT_ME (str): User's about me [Optional]

    - NEWS_NOTIFICATIONS (bool): User wants news notifications [False]
    - COMMENT_NOTIFICATIONS (bool): User wants comment notifications [False]
    - BAKERY_NOTIFICATIONS (bool): User wants bakery notifications [False]

    - EMPLOYEE_NAME (str): User's employee name [Optional]
    - ROLES (str): User's roles [Default: ""] ['|' separated]

    - NEW_EMAIL (str): User's new (temporary) email [Optional]
    - EMAIL_VERIFIED (bool): Indicates if the email is verified [False]
    - REMEMBER_ME (bool): Indicates 'remember me' setting [False]
    - LAST_SETTING_UPDATE (str): Name of last updated setting [Default]
    - UPDATED_SETTING_AT (datetime): Timestamp of last update to settings [Default]

    - LAST_SEEN_AT (datetime): Timestamp of last activity [Default]
    - TOT_LOGINS (int): Total number of logins [Default]
    - CREATED_AT (datetime): Timestamp of account creation [Default]
    - VERIFIED_AT (datetime): Timestamp of email verification [Default]

    - COMMENTS (list["Comment"]): User's comments relationship
    """
    __tablename__ = 'auth'  # noqa

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(75), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(75), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    fast_name: Mapped[Optional[str]] = mapped_column(String(16), unique=True)
    fast_code: Mapped[Optional[str]] = mapped_column(String(5))

    display_name: Mapped[Optional[str]] = mapped_column(String(16), unique=True)
    country: Mapped[Optional[str]] = mapped_column(String(32))
    profile_icon: Mapped[Optional[str]] = mapped_column(String(32))
    profile_picture: Mapped[Optional[str]] = mapped_column(String(255))
    about_me: Mapped[Optional[str]] = mapped_column(Text)

    news_notifications: Mapped[bool] = mapped_column(Boolean, default=False)
    comment_notifications: Mapped[bool] = mapped_column(Boolean, default=False)
    bakery_notifications: Mapped[bool] = mapped_column(Boolean, default=False)

    employee_name: Mapped[Optional[str]] = mapped_column(String(32), unique=True, default=None)
    roles: Mapped[list[str]] = mapped_column(String(255), default="")

    new_email: Mapped[Optional[str]] = mapped_column(String(75))
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    remember_me: Mapped[bool] = mapped_column(Boolean, default=False)
    last_setting_update: Mapped[Optional[str]] = mapped_column(String(32))
    updated_setting_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=lambda: datetime.now(SERVER.CET))

    last_seen_at: Mapped[datetime] = mapped_column(DateTime,
                                                   default=lambda: datetime.now(SERVER.CET))
    tot_logins: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=lambda: datetime.now(SERVER.CET))
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    news_articles: Mapped[list["News"]] = relationship(  # type: ignore
        "News",
        back_populates="user")
    comments: Mapped[list["Comment"]] = relationship(  # type: ignore
        "Comment",
        back_populates="user")

    def __init__(self, email: str, username: str, password: str,
                 fast_name: Optional[str] = None, fast_code: Optional[str] = None,
                 display_name: Optional[str] = None, email_verified: bool = False,
                 employee_name: Optional[str] = None, roles: Optional[str] = None):
        """
        Initialize a new User instance.
        Applies argon2 hashing to the password.
        Sets fast_name to lowercase if provided.
        Applies argon2 hashing to the fast_code if provided.
        """
        self.email = email
        self.username = username
        self.password = self._get_hash(password)
        self.fast_name = fast_name.lower() if fast_name else None
        self.fast_code = self._get_hash(fast_code) if fast_code else None
        self.profile_icon = self._init_profile_icon()
        self.about_me = "Share something interesting about yourself..."
        self.email_verified = email_verified
        self.employee_name = employee_name
        self._init_roles(roles)
        self.display_name = display_name

    @set_updated_at
    def set_email(self, email: str) -> None:
        regex_check = EmailCheck()
        taken_check = EmailTakenCheck()
        try:
            regex_check(None, type("Field", (object,), {"data": email})())
            taken_check(None, type("Field", (object,), {"data": email})())
            self.email = email
        except ValidationError as e:
            raise ValueError(f"Email validation error: {e}")
        

    @set_updated_at
    def set_username(self, username: str) -> None:
        taken_check = UsernameTakenCheck()
        length_check = UsernameLengthCheck()
        try:
            taken_check(None, type("Field", (object,), {"data": username})())
            length_check(None, type("Field", (object,), {"data": username})())
            self.username = username
        except ValidationError as e:
            raise ValueError(f"Username validation error: {e}")

    @set_updated_at
    def set_password(self, plain_password: str) -> None:
        regex_check = PasswordCheck()
        length_check = PasswordLengthCheck()
        try:
            regex_check(None, type("Field", (object,), {"data": plain_password})())
            length_check(None, type("Field", (object,), {"data": plain_password})())
            self.password = self._get_hash(plain_password)
        except ValidationError as e:
            raise ValueError(f"Password validation error: {e}")

    @set_updated_at
    def set_fast_name(self, fast_name: str) -> None:
        length_check = FastNameLengthCheck()
        try:
            length_check(None, type("Field", (object,), {"data": fast_name})())
            self.fast_name = fast_name.lower()
        except ValidationError as e:
            raise ValueError(f"Fast name validation error: {e}")

    @set_updated_at
    def set_fast_code(self, fast_code: str) -> None:
        regex_check = FastCodeCheck()
        length_check = FastCodeLengthCheck()
        try:
            regex_check(None, type("Field", (object,), {"data": fast_code})())
            length_check(None, type("Field", (object,), {"data": fast_code})())
            self.fast_code = self._get_hash(fast_code)
        except ValidationError as e:
            raise ValueError(f"Fast code validation error: {e}")

    @set_updated_at
    def set_display_name(self, display_name: str) -> None:
        taken_check = DisplayNameTakenCheck()
        length_check = DisplayNameLengthCheck()
        try:
            taken_check(None, type("Field", (object,), {"data": display_name})())
            length_check(None, type("Field", (object,), {"data": display_name})())
            self.display_name = display_name
        except ValidationError as e:
            raise ValueError(f"Display name validation error: {e}")

    @set_updated_at
    def set_country(self, country: str) -> None:
        if country not in FORM.COUNTRY_CHOICES:
            raise ValueError(f"Invalid country: {country}")
        else:
            self.country = country

    @set_updated_at
    def set_profile_icon(self, profile_icon: str) -> None:
        if profile_icon in os.listdir(DIR.PROFILE_ICONS):
            self.profile_icon = profile_icon

    @set_updated_at
    def set_profile_picture(self, profile_picture: str) -> None:
        try:
            pattern = os.path.join(DIR.PROFILE_PICS, f"{self.id}_")
            for file_path in glob.glob(pattern):
                os.remove(file_path)
        except FileNotFoundError:
            return
        except PermissionError as e:
            logger.critical(f"[SYS] PERMISSION ERROR while removing profile picture: {str(e)}", exc_info=True)
            return
        except Exception as e:
            logger.error(f"[SYS] UNEXPECTED ERROR while setting profile picture: {str(e)}", exc_info=True)
            return
        self.profile_picture = profile_picture

    @set_updated_at
    def set_about_me(self, about_me: str) -> None:
        if len(about_me) <= FORM.MAX_ABOUT_ME:
            self.about_me = about_me

    @set_updated_at
    def set_news_notifications(self, news_notifications: bool) -> None:
        if not isinstance(news_notifications, bool):
            raise ValueError(f"[AUTH] INVALID NEWS NOTIFICATIONS TYPE: {type(news_notifications)}")
        self.news_notifications = news_notifications

    @set_updated_at
    def set_comment_notifications(self, comment_notifications: bool) -> None:
        if not isinstance(comment_notifications, bool):
            raise ValueError(f"[AUTH] INVALID COMMENT NOTIFICATIONS TYPE: {type(comment_notifications)}")
        self.comment_notifications = comment_notifications

    @set_updated_at
    def set_bakery_notifications(self, bakery_notifications: bool) -> None:
        if not isinstance(bakery_notifications, bool):
            raise ValueError(f"[AUTH] INVALID BAKERY NOTIFICATIONS TYPE: {type(bakery_notifications)}")
        self.bakery_notifications = bakery_notifications

    @set_updated_at
    def set_employee_name(self, employee_name: str) -> None:
        name_check = EmployeeNameCheck()
        try:
            name_check(None, type("Field", (object,), {"data": employee_name})())
            self.employee_name = employee_name
        except ValidationError as e:
            raise ValueError(f"[AUTH] EMPLOYEE NAME VALIDATION ERROR: {e}")
    
    def _init_roles(self, roles: str | list[str] | None) -> str:
        if roles is None:
            return ""
        user_roles = []
        if isinstance(roles, list):
            for role in roles:
                if role in SERVER.USER_ROLES:
                    user_roles.append(role)
        elif isinstance(roles, str):
            user_roles.append(roles)

        self.update_roles(user_roles)

    def get_roles(self) -> list[str]:
        if not self.roles:
            return []
        return self.roles.split("|")

    @set_updated_at
    def add_roles(self, roles: list[str] | str) -> None:
        user_roles = self.get_roles()
        if isinstance(roles, list):
            for role in roles:
                if role not in SERVER.USER_ROLES:
                    logger.warning(f"[AUTH] INVALID ROLE: {role} for user: {self.username}")
                    continue
                if role in user_roles:
                    continue
                user_roles.append(role)
            self.update_roles(user_roles)
        elif isinstance(roles, str):
            if roles not in SERVER.USER_ROLES:
                logger.warning(f"[AUTH] INVALID ROLE: {roles} for user: {self.username}")
                return
            if roles in user_roles:
                return
            user_roles.append(roles)
            self.update_roles(user_roles)

    @set_updated_at
    def remove_roles(self, roles: list[str] | str) -> None:
        user_roles = self.get_roles()
        if isinstance(roles, list):
            for role in roles:
                if role not in SERVER.USER_ROLES:
                    logger.warning(f"[AUTH] INVALID ROLE: {role} for user: {self.username}")
                    continue
                if role not in user_roles:
                    logger.warning(f"[AUTH] INVALID ROLE: {role} for user: {self.username}")
                    continue
                user_roles.remove(role)
            self.update_roles(user_roles)
        elif isinstance(roles, str):
            if roles not in SERVER.USER_ROLES:
                logger.warning(f"[AUTH] INVALID ROLE: {roles} for user: {self.username}")
                return
            if roles not in user_roles:
                logger.warning(f"[AUTH] INVALID ROLE: {roles} for user: {self.username}")
                return
            user_roles.remove(roles)
            self.update_roles(user_roles)

    def update_roles(self, roles: list[str] | str) -> None:
        """
        Sets the Users roles to the provided roles.
        """
        if not roles:
            self.roles = ""
            return
        if isinstance(roles, list):
            self.roles = "|".join(roles)
            self.roles += "|"
        elif isinstance(roles, str):
            self.roles = roles if not roles.endswith("|") else roles + "|"

    def has_role(self, role: str) -> bool:
        return role in self.roles.split("|")

    @set_updated_at
    def set_new_email(self, new_email: str) -> None:
        regex_check = EmailCheck()
        taken_check = EmailTakenCheck()
        try:
            regex_check(None, type("Field", (object,), {"data": new_email})())
            taken_check(None, type("Field", (object,), {"data": new_email})())
            self.new_email = new_email
        except ValidationError as e:
            raise ValueError(f"New email validation error: {e}")

    def reset_new_email(self) -> None:
        self.new_email = None

    @set_updated_at
    def set_email_verified(self, verified: bool) -> None:
        if not isinstance(verified, bool):
            raise ValueError(f"Invalid email verified type: {type(verified)}")
        if verified:
            self.add_roles("verified")
        else:
            self.remove_roles("verified")
        self.email_verified = verified

    @set_updated_at
    def set_remember_me(self, remember: bool) -> None:
        if not isinstance(remember, bool):
            raise ValueError(f"Invalid remember me type: {type(remember)}")
        self.remember_me = remember

    def update_last_seen(self) -> None:
        self.last_seen_at = datetime.now(SERVER.CET)

    def increment_tot_logins(self) -> None:
        self.tot_logins += 1

    @staticmethod
    def _init_profile_icon() -> str:
        return random.choice([file for file in os.listdir(DIR.PROFILE_ICONS)])

    @staticmethod
    def _get_hash(plain_password: str) -> str:
        try:
            return argon2_.hash(plain_password)
        except Exception as e:
            logger.critical(f"[SYS] ERROR HASHING PASSWORD: {e}")
            abort(500)

    def __repr__(self) -> str:
        return (f"User:"
                f" (id={self.id},"
                f" username={self.username},"
                f" email={self.email}),"
                f" employee_name={self.employee_name})")

    def cli_repr(self) -> str:
        return (f"{'ID':<18}{self.id}\n"
                f"{'USERNAME':<18}{self.username}\n"
                f"{'EMAIL':<18}{self.email}\n"
                f"{'EMPLOYEE NAME':<18}{self.employee_name}\n"
                f"{'DISPLAY NAME':<18}{self.display_name}\n"
                f"{'ROLES':<18}{self.roles.replace('|', ', ')}\n"
                f"{'LAST SEEN AT':<18}{self.last_seen_at.strftime('%d %b %Y @ %H:%M')}")
                