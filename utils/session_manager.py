_sessions = {}  # user_id -> game instance

def get_blackjack_session(user_id):
    from games.blackjack.blackjack import Blackjack
    
    if user_id not in _sessions:
        _sessions[user_id] = Blackjack()
    
    return _sessions[user_id]

def reset_blackjack_session(user_id):
    _sessions.pop(user_id, None)
