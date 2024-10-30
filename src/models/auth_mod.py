from datetime import datetime
from typing import Optional, Callable
from functools import wraps

from flask_login import UserMixin
from sqlalchemy import select, Boolean, Integer, String, DateTime, or_
from sqlalchemy.orm import Mapped, mapped_column

from src.extensions import server_db_, login_manager_, argon2_
from config.settings import CET


@login_manager_.user_loader
def load_user(user_id):
    """Load the currently logged in Users information into the session."""
    return server_db_.session.get(User, user_id)


def commit_to_db(func: Callable) -> Callable:
    """Decorator to commit the session after executing the wrapped function."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        server_db_.session.commit()
        return result
    return wrapper


def set_updated_at(func: Callable) -> Callable:
    """
    Decorator to set the updated_setting_at and last_setting_update attributes
    after executing the wrapped function.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self.updated_setting_at = datetime.now(CET)
        self.last_setting_update = f"{func.__name__}"
        return result
    return wrapper


class User(server_db_.Model, UserMixin):
    """
    Stores the User data.

    - ID (int): Identifier [Primary Key]
    - EMAIL (str): User's email address [Unique]
    - USERNAME (str): User's username [Unique]
    - PASSWORD (str): User's hashed password
    - FAST_NAME (str): User's fast name [Unique] [Optional]
    - FAST_CODE (int): User's fast code [Optional]
    
    - EMAIL_VERIFIED (bool): Indicates if the email is verified [False]
    - REMEMBER_ME (bool): Indicates 'remember me' setting [False]
    - LAST_SETTING_UPDATE (str): Name of last updated setting [Default]
    - UPDATED_SETTING_AT (datetime): Timestamp of last update to settings [Default]
    
    - LAST_SEEN_AT (datetime): Timestamp of last activity [Default]
    - TOT_LOGINS (int): Total number of logins [Default]
    - CREATED_AT (datetime): Timestamp of account creation [Default]
    """
    __tablename__ = 'auth'  # noqa

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(75), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(75), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    fast_name: Mapped[Optional[str]] = mapped_column(String(16), unique=True)
    fast_code: Mapped[Optional[str]] = mapped_column(String(5))

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
    
    def __init__(self, email: str, username: str, password: str,
                 fast_name: Optional[str] = None, fast_code: Optional[str] = None):
        self.email = email
        self.username = username
        self.password = self._get_hash(password)
        self.fast_name = fast_name.lower() if fast_name else None
        self.fast_code = self._get_hash(fast_code) if fast_code else None
    
    @commit_to_db
    @set_updated_at
    def set_email(self, email: str) -> None:
        self.email = email
    
    @commit_to_db
    @set_updated_at
    def set_username(self, username: str) -> None:
        self.username = username
    
    @commit_to_db
    @set_updated_at
    def set_password(self, plain_password: str) -> None:
        self.password = self._get_hash(plain_password)
    
    @commit_to_db
    @set_updated_at
    def set_fast_name(self, fast_name: str) -> None:
        self.fast_name = fast_name.lower()
    
    @commit_to_db
    @set_updated_at
    def set_fast_code(self, fast_code: str) -> None:
        self.fast_code = self._get_hash(fast_code)
    
    @commit_to_db
    def set_email_verified(self, verified: bool) -> None:
        self.email_verified = verified
    
    @commit_to_db
    def set_remember_me(self, remember: bool) -> None:
        self.remember_me = remember
    
    @commit_to_db
    def update_last_seen(self) -> None:
        self.last_seen_at = datetime.now(CET)
    
    @commit_to_db
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


def get_user_by_id(id_: int) -> Optional[User]:
    return server_db_.session.get(User, id_)


def get_user_by_email(email: str) -> Optional[User]:
    return server_db_.session.execute(
        select(User).filter_by(email=email)
    ).scalar_one_or_none()

    
def get_user_by_username(username: str) -> Optional[User]:
    return server_db_.session.execute(
        select(User).filter_by(username=username)
    ).scalar_one_or_none()


def get_user_by_email_or_username(email_or_username: str) -> Optional[User]:
    return server_db_.session.execute(
        select(User).filter(
            or_(User.email == email_or_username, User.username == email_or_username)
        )
    ).scalar_one_or_none()


def get_user_by_fast_name(fast_name: str) -> Optional[User]:
    return server_db_.session.execute(
        select(User).filter_by(fast_name=fast_name)
    ).scalar_one_or_none()


@commit_to_db
def add_new_user(email: str, username: str, password: str) -> None:
    new_user = User(email=email, username=username, password=password)
    server_db_.session.add(new_user)


def get_new_user(email: str, username: str, password: str) -> User:
    # noinspection PyArgumentList
    new_user = User(
        email=email,
        username=username,
        password=password,
    )
    server_db_.session.add(new_user)
    server_db_.session.commit()
    return new_user
