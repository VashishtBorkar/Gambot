from games.blackjack.blackjack import Blackjack
from games.bet import Bet
_sessions = {}  #{user_id: {game: Blackjack(), bet: Bet()}}

def create_blackjack_session(user_id, bet):
    _sessions[user_id] = {
        "game": Blackjack(),
        "bet": bet
    }
    return _sessions[user_id]["game"]

def has_blackjack_session(user_id):
    return user_id in _sessions

def get_blackjack_session(user_id):
    return _sessions[user_id]["game"] if user_id in _sessions else None

def get_blackjack_bet(user_id):
    return _sessions[user_id]["bet"] if user_id in _sessions else None

def reset_blackjack_session(user_id):
    _sessions.pop(user_id, None)
