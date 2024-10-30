from datetime import datetime
from typing import Optional, List

from flask_login import UserMixin
from sqlalchemy import select, Boolean, Integer, String, DateTime, or_, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.exc import IntegrityError

from src.extensions import server_db_, argon2_
from src.models.mod_utils import commit_to_db, set_updated_at

from config.settings import CET


class AuthenticationToken(server_db_.Model):
    """
    Stores AuthenticationToken data for various authentication purposes.
    
    - ID (int): Identifier [Primary Key]
    - USER_ID (int): User ID [Foreign Key]
    - TOKEN_TYPE (str): Type of token
    - TOKEN (str): Token
    - CREATED_AT (datetime): Timestamp of creation [Default]
    """
    __tablename__ = "authentication_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth.id"))
    token_type: Mapped[str] = mapped_column(String(32))
    token: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tokens")


# @commit_to_db
# def delete_verification_token(id_: int):
#     server_db_.session.query(AuthenticationToken).filter_by(
#         user_id=id_, token_type="verification").delete()
    
    
def reset_password_reset_token(email: str, token: str):
    id_ = get_user_by_email(email).id
    existing_token = server_db_.session.query(AuthenticationToken).filter_by(
        user_id=id_, token_type="password_verification").first()
    if existing_token:
        existing_token.token = token
    else:
        new_token = AuthenticationToken(user_id=id_,
                                        token_type="password_verification", token=token)
        server_db_.session.add(new_token)
        server_db_.session.commit()


@commit_to_db
def delete_password_reset_token(id_: int):
    server_db_.session.query(AuthenticationToken).filter_by(
        user_id=id_, token_type="password_verification").delete()


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
    - LAST_SETTING_UPDATE (str): Name of last updated setting [Default] [Optional]
    - UPDATED_SETTING_AT (datetime): Timestamp of last update to settings [Default]
    
    - LAST_SEEN_AT (datetime): Timestamp of last activity [Default]
    - TOT_LOGINS (int): Total number of logins [Default]
    - CREATED_AT (datetime): Timestamp of account creation [Default]
    - VERIFIED_AT (datetime): Timestamp of email verification [Default] [Optional]
    
    - TOKENS (List[AuthenticationToken]): List of AuthenticationTokens [Default] [Optional]
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
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    tokens: Mapped[List[AuthenticationToken]] = relationship("AuthenticationToken", back_populates="user")
    
    def __init__(self, email: str, username: str, password: str,
                 fast_name: Optional[str] = None, fast_code: Optional[str] = None):
        self.email = email
        self.username = username
        self.password = self._get_hash(password)
        self.fast_name = fast_name.lower() if fast_name else None
        self.fast_code = self._get_hash(fast_code) if fast_code else None
    
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


def get_user_by_id(id_: int) -> User | None:
    return server_db_.session.get(User, id_)


def get_user_by_email(email: str) -> User | None:
    return server_db_.session.execute(
        select(User).filter_by(email=email)
    ).scalar_one_or_none()

    
def get_user_by_username(username: str) -> User | None:
    return server_db_.session.execute(
        select(User).filter_by(username=username)
    ).scalar_one_or_none()


def get_user_by_email_or_username(email_or_username: str) -> User | None:
    return server_db_.session.execute(
        select(User).filter(
            or_(User.email == email_or_username, User.username == email_or_username)
        )
    ).scalar_one_or_none()


def get_user_by_fast_name(fast_name: str) -> User | None:
    return server_db_.session.execute(
        select(User).filter_by(fast_name=fast_name)
    ).scalar_one_or_none()


@commit_to_db
def delete_user_by_id(id_: int) -> None:
    server_db_.session.delete(server_db_.session.get(User, id_))


@commit_to_db
def add_new_user(email: str, username: str, password: str) -> bool:
    try:
        new_user = User(email=email, username=username, password=password)
        server_db_.session.add(new_user)
        return True
    except IntegrityError:
        return False


def get_new_user(email: str, username: str, password: str) -> User | None:
    # noinspection PyArgumentList
    try:
        new_user = User(
            email=email,
            username=username,
            password=password,
        )
        server_db_.session.add(new_user)
        server_db_.session.commit()
        return new_user
    except IntegrityError:
        return None


def _init_user() -> User | None:
    if not server_db_.session.query(User).count():
        new_user = User(
            email="100pythoncourse@gmail.com",
            username="100python",
            password="TomasTomas1!",
            fast_name="tomas",
            fast_code=("00000"),
        )
        server_db_.session.add(new_user)
        server_db_.session.commit()
        return repr(new_user)
    
    return None
