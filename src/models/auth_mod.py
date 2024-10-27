from datetime import datetime
from typing import Optional

from flask_login import UserMixin
from sqlalchemy import select, Boolean, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from config.settings import CET
from src.extensions import server_db_, login_manager_, argon2_


@login_manager_.user_loader
def load_user(user_id):
    return server_db_.session.get(User, user_id)


class User(server_db_.Model, UserMixin):
    """
    Stores the User login data and their relationships.

    - ID: Unique identifier for the user
    - EMAIL: User's email address
    - USERNAME: User's chosen username
    - PASSWORD: Hashed password for the user
    - FAST_NAME: User's fast name (optional)
    - FAST_CODE: User's fast code (optional)
    - EMAIL_VERIFIED: Boolean indicating if the email is verified
    - REMEMBER_ME: Boolean for "remember me" functionality
    - LAST_SEEN_AT: Timestamp of user's last activity
    - CREATED_AT: Timestamp of user account creation
    - UPDATED_AT: Timestamp of last update to user account
    - TOT_LOGINS: Total number of user logins
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

    last_seen_at: Mapped[datetime] = mapped_column(DateTime,
                                                   default=lambda: datetime.now(CET))
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=lambda: datetime.now(CET))
    updated_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=lambda: datetime.now(CET),
                                                 onupdate=lambda: datetime.now(CET))

    tot_logins: Mapped[int] = mapped_column(Integer, default=0)
    
    def __init__(self, email: str, username: str, password: str,
                 fast_name: Optional[str] = None, fast_code: Optional[str] = None):
        self.email = email
        self.username = username
        self.password = self._get_hash(password)
        self.fast_name = fast_name.lower() if fast_name else None
        self.fast_code = self._get_hash(fast_code) if fast_code else None
    
    @staticmethod
    def _get_hash(plain_password: str) -> str:
        return argon2_.hash(plain_password)
    
    def set_password(self, plain_password: str) -> None:
        self.password = self._get_hash(plain_password)
        server_db_.session.commit()
    
    def set_f_name(self, fast_name: str) -> None:
        self.fast_name = fast_name.lower()
        server_db_.session.commit()

    def increment_tot_logins(self):
        self.tot_logins += 1
        server_db_.session.commit()
    
    def set_remember_me(self, remember: bool) -> None:
        self.remember_me = remember
        server_db_.session.commit()

    def __repr__(self):
        return (f"User: "
                f"(id={self.id},"
                f" username={self.username},"
                f" email={self.email}")



def get_user_by_id(id_):
    return server_db_.session.get(User, id_)


def get_user_by_email(email):
    return server_db_.session.execute(
        select(User).filter_by(email=email)
    ).scalar_one_or_none()

    
def get_user_by_username(username):
    return server_db_.session.execute(
        select(User).filter_by(username=username)
    ).scalar_one_or_none()


def get_user_by_email_or_username(email_or_username):
    return server_db_.session.execute(
        select(User).filter(
            or_(User.email == email_or_username, User.username == email_or_username)
        )
    ).scalar_one_or_none()


def get_user_by_fast_name(fast_name):
    return server_db_.session.execute(
        select(User).filter_by(fast_name=fast_name)
    ).scalar_one_or_none()


def change_user_password(user: User, password: str) -> None:
    """
    Takes a user_id(int) and a hashed_password(str)
    Updates the password in the database.
    """
    user.set_password(password)  # noqa
    server_db_.session.commit()


def add_new_user(email, username, password) -> None:
    new_user = User(email=email, username=username, password=password)
    server_db_.session.add(new_user)
    server_db_.session.commit()


def get_new_user(email: str, username: str,
                 password: str) -> User:
    """Takes register_form input data and creates a new user."""
    # noinspection PyArgumentList
    new_user = User(
        email=email,
        username=username,
        password=password,
    )
    server_db_.session.add(new_user)
    server_db_.session.commit()
    return new_user


def update_user_last_seen(user, last_seen_at):
    user.last_seen_at = last_seen_at
    server_db_.session.commit()
