from src.extensions import server_db_


class State(server_db_.Model):
    __tablename__ = 'oauth_states'

    id = server_db_.Column(server_db_.Integer, primary_key=True)
    state = server_db_.Column(server_db_.String(64), unique=True, nullable=False)

    def __init__(self, state):
        self.state = state

    def __repr__(self):
        return f'<State {self.state}>'