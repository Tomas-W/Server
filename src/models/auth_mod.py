
from flask_login import UserMixin
from sqlalchemy import Boolean

from src.extensions import server_db_, login_manager_, argon2_


@login_manager_.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(server_db_.Model, UserMixin):
    """
    Stores the User login data and their relationships.
    """
    __tablename__ = 'auth'  # noqa

    id = server_db_.Column(server_db_.Integer, primary_key=True)
    email = server_db_.Column(server_db_.String(75), unique=True, nullable=False)
    username = server_db_.Column(server_db_.String(75), nullable=False)
    password = server_db_.Column(server_db_.String(75), nullable=False)
    fast_name = server_db_.Column(server_db_.String(16), unique=True)
    fast_code = server_db_.Column(server_db_.String(5), unique=False)

    email_verified = server_db_.Column(Boolean)
    remember_me = server_db_.Column(Boolean)

    def __repr__(self):
        return (f"User: "
                f"(id={self.id},"
                f" username={self.username},"
                f" email={self.email}")
