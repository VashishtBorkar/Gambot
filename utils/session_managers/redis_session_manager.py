import json
import redis

class RedisSessionManager:
    def __init__(self, host="localhost", port=6379, db=0, ttl=3600):
        # ttl = session expiration in seconds (default: 1 hour)
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.ttl = ttl

    def create_session(self, user_id, data):
        # data should be serializable (dict, not custom object directly)
        self.r.setex(user_id, self.ttl, json.dumps(data))
        return data

    def has_session(self, user_id):
        return self.r.exists(user_id) == 1

    def get_session(self, user_id):
        session_data = self.r.get(user_id)
        return json.loads(session_data) if session_data else None

    def reset_session(self, user_id):
        self.r.delete(user_id)
