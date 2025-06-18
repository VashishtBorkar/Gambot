from .session_manager import SessionManager

class RouletteSessionManager(SessionManager):
    def __init__(self):
        super().__init__()  # correctly initializes self._sessions

    def create_session(self, user_id, game, bet):
        data = {
            "game": game,
            "bet": bet
        }
        return super().create_session(user_id, data)
    
    def get_game(self, user_id):
        session = self.get_session(user_id)
        return session["game"] if session else None
    
    def get_bet(self, user_id):
        session = self.get_session(user_id)
        return session["bet"] if session else None
