from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    LargeBinary,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from src.extensions import server_db_


class SessionModel(server_db_.Model):
    """
    Represents a session in the database.

    - ID (str): Identifier [Primary Key]
    - DATA (bytes): Binary data associated with the session
    - MODIFIED (datetime): Timestamp of when the session was last modified
    """

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    data: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    modified: Mapped[datetime] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return (f"SessionModel(id={self.id!r},"
                f" modified={self.modified!r})")
