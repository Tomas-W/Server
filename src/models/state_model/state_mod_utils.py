from sqlalchemy import select

from src.extensions import server_db_
from src.models.state_model.state_mod import State


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
