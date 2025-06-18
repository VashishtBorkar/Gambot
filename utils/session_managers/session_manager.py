class SessionManager:
    def __init__(self):
        self._sessions = {}  #{user_id: {game: Game(), bet: Bet()}}

    def create_session(self, user_id, data):
        self._sessions[user_id] = data
        return data

    def has_session(self, user_id):
        return user_id in self._sessions

    def get_session(self, user_id):
        return self._sessions.get(user_id)

    def reset_session(self, user_id):
        self._sessions.pop(user_id, None)
