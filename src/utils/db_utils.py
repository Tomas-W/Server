from src.extensions import server_db_
from src.models.auth_mod import User
from sqlalchemy import select, or_
from src.models.state_mod import State
from src.models.bakery_mod import BakeryItem

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


def add_new_user(email, username, password):
    new_user = User(email=email, username=username, password=password)
    server_db_.session.add(new_user)
    server_db_.session.commit()
    return new_user


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



def save_oauth_state(state):
    oauth_state = State(state=state)
    server_db_.session.add(oauth_state)
    server_db_.session.commit()
    return oauth_state


def get_and_delete_oauth_state(state):
    oauth_state = server_db_.session.execute(
        select(State).filter_by(state=state)
    ).scalar_one_or_none()
    if oauth_state:
        server_db_.session.delete(oauth_state)
        server_db_.session.commit()
    return oauth_state


def update_user_last_seen(user, last_seen_at):
    user.last_seen_at = last_seen_at
    server_db_.session.commit()


def get_bakery_programs(program) -> list[BakeryItem]:
    return server_db_.session.execute(
        select(BakeryItem).filter_by(program=program)
    ).scalars().all()
