from games.blackjack.blackjack import Blackjack
from games.bet import Bet
from .redis_session_manager import RedisSessionManager

class BlackjackSessionManager(RedisSessionManager):
    def create_session(self, user_id, game: Blackjack, bet: Bet):
        data = {
            "game": game.to_dict(),
            "bet": bet.to_dict()
        }
        return super().create_session(user_id, data)

    def get_game(self, user_id):
        session = self.get_session(user_id)
        return Blackjack.from_dict(session["game"]) if session else None

    def get_bet(self, user_id):
        session = self.get_session(user_id)
        return Bet.from_dict(session["bet"]) if session else None
