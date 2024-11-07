import os
import random
from datetime import datetime
from typing import Optional, List

from flask_login import UserMixin
from sqlalchemy import Boolean, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.extensions import server_db_, argon2_
from src.models.mod_utils import set_updated_at

from config.settings import CET, PROFILE_ICONS_FOLDER


class AuthenticationToken(server_db_.Model):
    """
    Stores AuthenticationToken data for various authentication purposes.
    
    - ID (int): Identifier [Primary Key]
    - USER_ID (int): User ID [Foreign Key]
    - TOKEN_TYPE (str): Type of token
    - TOKEN (str): Token
    - CREATED_AT (datetime): Timestamp of creation [Default]
    
    - USER (User): User relationship
    """
    __tablename__ = "authentication_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth.id", ondelete="CASCADE"))
    token_type: Mapped[str] = mapped_column(String(32))
    token: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(CET))

    user = relationship("User", back_populates="tokens")


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
    
    - EMAIL_VERIFIED (bool): Indicates if the email is verified [False]
    - REMEMBER_ME (bool): Indicates 'remember me' setting [False]
    - LAST_SETTING_UPDATE (str): Name of last updated setting [Default]
    - UPDATED_SETTING_AT (datetime): Timestamp of last update to settings [Default]
    
    - LAST_SEEN_AT (datetime): Timestamp of last activity [Default]
    - TOT_LOGINS (int): Total number of logins [Default]
    - CREATED_AT (datetime): Timestamp of account creation [Default]
    - VERIFIED_AT (datetime): Timestamp of email verification [Default]
    
    - TOKENS (List[AuthenticationToken]): AuthenticationTokens relationship
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
    
    tokens: Mapped[List[AuthenticationToken]] = relationship(
        "AuthenticationToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(  # type: ignore
        "Comment",
        back_populates="author_user"
    )
    
    def __init__(self, email: str, username: str, password: str,
                 fast_name: Optional[str] = None, fast_code: Optional[str] = None,
                 email_verified: bool = False):
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
        self.display_name = username
        self.profile_icon = random.choice([file for file in os.listdir(PROFILE_ICONS_FOLDER)])
        self.about_me = "Share something interesting about yourself..."
        self.email_verified = email_verified
    
    @set_updated_at
    def set_email(self, email: str) -> None:
        self.email = email
    
    @set_updated_at
    def set_username(self, username: str) -> None:
        self.username = username
    
    @set_updated_at
    def set_password(self, plain_password: str) -> None:
        self.password = self._get_hash(plain_password)
    
    @set_updated_at
    def set_fast_name(self, fast_name: str) -> None:
        self.fast_name = fast_name.lower()
    
    @set_updated_at
    def set_fast_code(self, fast_code: str) -> None:
        self.fast_code = self._get_hash(fast_code)
    
    @set_updated_at
    def set_display_name(self, display_name: str) -> None:
        self.display_name = display_name
    
    @set_updated_at
    def set_country(self, country: str) -> None:
        self.country = country
    
    @set_updated_at
    def set_profile_icon(self, profile_icon: str) -> None:
        self.profile_icon = profile_icon
    
    @set_updated_at
    def set_profile_picture(self, profile_picture: str) -> None:
        self.profile_picture = profile_picture
    
    @set_updated_at
    def set_about_me(self, about_me: str) -> None:
        self.about_me = about_me
    
    @set_updated_at
    def set_news_notifications(self, news_notifications: bool) -> None:
        self.news_notifications = news_notifications
    
    @set_updated_at
    def set_comment_notifications(self, comment_notifications: bool) -> None:
        self.comment_notifications = comment_notifications
    
    @set_updated_at
    def set_bakery_notifications(self, bakery_notifications: bool) -> None:
        self.bakery_notifications = bakery_notifications
    
    @set_updated_at
    def set_new_email(self, new_email: str) -> None:
        self.new_email = new_email
    
    def reset_new_email(self) -> None:
        self.new_email = None
    
    @set_updated_at
    def set_email_verified(self, verified: bool) -> None:
        self.email_verified = verified
    
    @set_updated_at
    def set_remember_me(self, remember: bool) -> None:
        self.remember_me = remember
    
    def update_last_seen(self) -> None:
        self.last_seen_at = datetime.now(CET)
    
    def increment_tot_logins(self) -> None:
        self.tot_logins += 1
    
    @staticmethod
    def _get_hash(plain_password: str) -> str:
        return argon2_.hash(plain_password)
    
    def __repr__(self) -> str:
        return (f"User:"
                f" (id={self.id},"
                f" username={self.username},"
                f" email={self.email})"
                )
