from src import server_db_


class SessionModel(server_db_.Model):
    """Represents a session in the database.

    - ID: Unique identifier for the session
    - DATA: Binary data associated with the session
    - MODIFIED: Timestamp of when the session was last modified
    """

    __tablename__ = 'sessions'

    id = server_db_.Column(server_db_.String(255), primary_key=True)
    data = server_db_.Column(server_db_.LargeBinary)
    modified = server_db_.Column(server_db_.DateTime)

    def __repr__(self):
        return f"SessionModel(id={self.id}, modified={self.modified})"
