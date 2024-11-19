import glob
import os
import random
import re
from datetime import datetime
from typing import Optional
from flask import redirect, url_for, session, abort
from flask_login import UserMixin
from sqlalchemy import (
    Integer, String, DateTime, Boolean, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from src.extensions import server_db_, argon2_, logger
from src.models.mod_utils import (
    set_updated_at
)
from src.models.auth_model.auth_mod_utils import (
    get_user_by_username, get_user_by_fast_name, get_user_by_display_name
)
from config.settings import (
    CET, PROFILE_ICONS_FOLDER, PROFILE_PICTURES_FOLDER, USER_ROLES, E_500_REDIRECT,
    EMAIL_REGEX, COUNTRY_CHOICES, MAX_ABOUT_ME_LENGTH
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
                                                 default=lambda: datetime.now(CET))
    
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

    roles: Mapped[list[str]] = mapped_column(String(255), default="")

    new_email: Mapped[Optional[str]] = mapped_column(String(75))
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    remember_me: Mapped[bool] = mapped_column(Boolean, default=False)
    last_setting_update: Mapped[Optional[str]] = mapped_column(String(32))
    updated_setting_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=lambda: datetime.now(CET))

    last_seen_at: Mapped[datetime] = mapped_column(DateTime,
                                                   default=lambda: datetime.now(CET))
    tot_logins: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=lambda: datetime.now(CET))
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    news_articles: Mapped[list["News"]] = relationship(  # type: ignore
        "News",
        back_populates="user")
    comments: Mapped[list["Comment"]] = relationship(  # type: ignore
        "Comment",
        back_populates="user")

    def __init__(self, email: str, username: str, password: str,
                 fast_name: Optional[str] = None, fast_code: Optional[str] = None,
                 email_verified: bool = False, roles: Optional[str] = None):
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
        self._init_roles(roles)

    @set_updated_at
    def set_email(self, email: str) -> None:
        if not re.match(EMAIL_REGEX, email):
            session["error_msg"] = f"Invalid email: {email}"
            abort(500)
        self.email = email

    @set_updated_at
    def set_username(self, username: str) -> None:
        if get_user_by_username(username):
            session["error_msg"] = f"Username taken: {username}"
            abort(500)
        self.username = username

    @set_updated_at
    def set_password(self, plain_password: str) -> None:
        self.password = self._get_hash(plain_password)

    @set_updated_at
    def set_fast_name(self, fast_name: str) -> None:
        if get_user_by_fast_name(fast_name):
            session["error_msg"] = f"Fast name taken: {fast_name}"
            abort(500)
        self.fast_name = fast_name

    @set_updated_at
    def set_fast_code(self, fast_code: str) -> None:
        self.fast_code = self._get_hash(fast_code)

    @set_updated_at
    def set_display_name(self, display_name: str) -> None:
        if get_user_by_display_name(display_name):
            session["error_msg"] = f"Display name taken: {display_name}"
            abort(500)
        else:
            self.display_name = display_name

    @set_updated_at
    def set_country(self, country: str) -> None:
        if country not in COUNTRY_CHOICES:
            errors = f"Invalid country: {country} - {logger.get_log_info()}"
            logger.error(errors)
        else:
            self.country = country

    @set_updated_at
    def set_profile_icon(self, profile_icon: str) -> None:
        if profile_icon not in os.listdir(PROFILE_ICONS_FOLDER):
            errors = f"Invalid profile icon: {profile_icon} - {logger.get_log_info()}"
            logger.error(errors)
        else:
            self.profile_icon = profile_icon

    @set_updated_at
    def set_profile_picture(self, profile_picture: str) -> None:
        try:
            pattern = os.path.join(PROFILE_PICTURES_FOLDER, f"{self.id}_")
            for file_path in glob.glob(pattern):
                os.remove(file_path)
        except FileNotFoundError:
            return
        except PermissionError as e:
            errors = f"PermissionError: {e} - {logger.get_log_info()}"
            logger.critical(errors)
            return
        except Exception as e:
            errors = f"Error setting profile picture: {e} - {logger.get_log_info()}"
            logger.critical(errors)
            return
        self.profile_picture = profile_picture

    @set_updated_at
    def set_about_me(self, about_me: str) -> None:
        if len(about_me) > MAX_ABOUT_ME_LENGTH:
            errors = f"About me too long: {about_me} - {logger.get_log_info()}"
            logger.error(errors)
        else:    
            self.about_me = about_me

    @set_updated_at
    def set_news_notifications(self, news_notifications: bool) -> None:
        if not isinstance(news_notifications, bool):
            errors = f"Invalid news notifications type: {type(news_notifications)} - {logger.get_log_info()}"
            logger.error(errors)
        else:
            self.news_notifications = news_notifications

    @set_updated_at
    def set_comment_notifications(self, comment_notifications: bool) -> None:
        if not isinstance(comment_notifications, bool):
            errors = f"Invalid comment notifications type: {type(comment_notifications)} - {logger.get_log_info()}"
            logger.error(errors)
        else:
            self.comment_notifications = comment_notifications

    @set_updated_at
    def set_bakery_notifications(self, bakery_notifications: bool) -> None:
        if not isinstance(bakery_notifications, bool):
            errors = f"Invalid bakery notifications type: {type(bakery_notifications)} - {logger.get_log_info()}"
            logger.error(errors)
        else:
            self.bakery_notifications = bakery_notifications

    def get_roles(self) -> list[str]:
        return self.roles.split("|")

    @set_updated_at
    def add_roles(self, roles: list[str] | str) -> None:
        user_roles = self.get_roles()
        if isinstance(roles, list):
            for role in roles:
                if role not in USER_ROLES:
                    errors = f"Invalid role: {role} - {logger.get_log_info()}"
                    logger.error(errors)
                    return
                if role in user_roles:
                    continue
                user_roles.append(role)
            self.update_roles(user_roles)
        elif isinstance(roles, str):
            if roles not in USER_ROLES:
                errors = f"Invalid role: {roles} - {logger.get_log_info()}"
                logger.error(errors)
                return
            if roles in user_roles:
                return
            user_roles.append(roles)
            self.update_roles(user_roles)
        else:
            errors = f"Invalid role type: {type(roles)} - {logger.get_log_info()}"
            logger.error(errors)

    @set_updated_at
    def remove_roles(self, roles: list[str] | str) -> None:
        user_roles = self.get_roles()
        if isinstance(roles, list):
            for role in roles:
                if role not in USER_ROLES:
                    errors = f"Invalid role: {role} - {logger.get_log_info()}"
                    logger.error(errors)
                    continue
                if role not in user_roles:
                    errors = f"User does not have role: {role} - {logger.get_log_info()}"
                    logger.warning(errors)
                    continue
                user_roles.remove(role)
            self.update_roles(user_roles)
        elif isinstance(roles, str):
            if roles not in USER_ROLES:
                errors = f"Invalid role: {roles} - {logger.get_log_info()}"
                logger.error(errors)
                return
            if roles not in user_roles:
                errors = f"User does not have role: {roles} - {logger.get_log_info()}"
                logger.warning(errors)
                return
            user_roles.remove(roles)
            self.update_roles(user_roles)
        else:
            errors = f"Invalid role type: {type(roles)} - {logger.get_log_info()}"
            logger.error(errors)

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
        else:
            errors = f"Invalid roles type: {type(roles)} - {logger.get_log_info()}"
            logger.error(errors)

    def has_role(self, role: str) -> bool:
        return role in self.roles.split("|")

    @set_updated_at
    def set_new_email(self, new_email: str) -> None:
        if not re.match(EMAIL_REGEX, new_email):
            errors = f"Invalid new email: {new_email} - {logger.get_log_info()}"
            logger.error(errors)
        else:
            self.new_email = new_email

    def reset_new_email(self) -> None:
        self.new_email = None

    @set_updated_at
    def set_email_verified(self, verified: bool) -> None:
        if not isinstance(verified, bool):
            errors = f"Invalid email verified type: {type(verified)} - {logger.get_log_info()}"
            logger.error(errors)
            return
        if verified:
            self.add_roles("verified")
        else:
            self.remove_roles("verified")
        self.email_verified = verified

    @set_updated_at
    def set_remember_me(self, remember: bool) -> None:
        if not isinstance(remember, bool):
            errors = f"Invalid remember me type: {type(remember)} - {logger.get_log_info()}"
            logger.error(errors)
            return
        self.remember_me = remember

    def update_last_seen(self) -> None:
        self.last_seen_at = datetime.now(CET)

    def increment_tot_logins(self) -> None:
        self.tot_logins += 1

    def _init_roles(self, roles: str | list[str] | None) -> str:
        if roles is None:
            return ""
        user_roles = []
        if isinstance(roles, list):
            for role in roles:
                if role not in USER_ROLES:
                    errors = f"Invalid role: {role} - {logger.get_log_info()}"
                    logger.error(errors)
                user_roles.append(role)
        elif isinstance(roles, str):
            user_roles.append(roles)

        self.update_roles(user_roles)

    @staticmethod
    def _init_profile_icon() -> str:
        return random.choice([file for file in os.listdir(PROFILE_ICONS_FOLDER)])

    @staticmethod
    def _get_hash(plain_password: str) -> str:
        try:
            return argon2_.hash(plain_password)
        except Exception as e:
            session["error_msg"] = f"Error hashing password: {e} - {logger.get_log_info()}"
            abort(500)

    def __repr__(self) -> str:
        return (f"User:"
                f" (id={self.id},"
                f" username={self.username},"
                f" email={self.email})"
                )
