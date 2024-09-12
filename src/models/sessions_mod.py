from src import server_db_


class SessionModel(server_db_.Model):
    __tablename__ = 'sessions'

    id = server_db_.Column(server_db_.String(255), primary_key=True)
    data = server_db_.Column(server_db_.LargeBinary)
    modified = server_db_.Column(server_db_.DateTime)

    def __repr__(self):
        return f"SessionModel(id={self.id}, modified={self.modified})"
