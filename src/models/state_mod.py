from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.extensions import server_db_


class State(server_db_.Model):
    """Represents an OAuth state in the database."""

    __tablename__ = 'oauth_states'

    id: Mapped[int] = mapped_column(primary_key=True)
    state: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    def __init__(self, state: str):
        self.state = state

    def __repr__(self) -> str:
        return f'State(id={self.id!r}, state={self.state!r})'