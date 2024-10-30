from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column

from src.extensions import server_db_


class State(server_db_.Model):
    """
    Stores the model for OAuth states.
    
    - ID (int): Identifier [Primary Key]
    - STATE (str): OAuth state [Unique]
    """

    __tablename__ = "oauth_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    state: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    def __init__(self, state: Mapped[str]):
        self.state = state

    def __repr__(self) -> str:
        return (f"State:"
                f" (id={self.id!r},"
                f" state={self.state!r})"
                )


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
