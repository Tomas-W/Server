from datetime import datetime

import pytz
from flask_login import UserMixin
from sqlalchemy import Boolean

from config.settings import CET
from src.extensions import server_db_, login_manager_, argon2_


@login_manager_.user_loader
def load_user(user_id):
    return User.query.get(user_id)


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

    id = server_db_.Column(server_db_.Integer, primary_key=True)
    email = server_db_.Column(server_db_.String(75), unique=True, nullable=False)
    username = server_db_.Column(server_db_.String(75), unique=True, nullable=False)
    password = server_db_.Column(server_db_.String(128), nullable=False)
    fast_name = server_db_.Column(server_db_.String(16), unique=True)
    fast_code = server_db_.Column(server_db_.String(5))

    email_verified = server_db_.Column(Boolean)
    remember_me = server_db_.Column(Boolean, default=False)

    last_seen_at = server_db_.Column(server_db_.DateTime,
                                     default=lambda: datetime.now(CET))
    created_at = server_db_.Column(server_db_.DateTime,
                                   default=lambda: datetime.now(CET))
    updated_at = server_db_.Column(server_db_.DateTime,
                                   default=lambda: datetime.now(CET),
                                   onupdate=lambda: datetime.now(CET))

    tot_logins = server_db_.Column(server_db_.Integer, default=0)

    def __repr__(self):
        return (f"User: "
                f"(id={self.id},"
                f" username={self.username},"
                f" email={self.email}")
