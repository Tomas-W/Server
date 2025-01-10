from sqlalchemy import String
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
