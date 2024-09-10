import redis


class RedisClient:
    def __init__(self, host, port, target):
        self.host = host
        self.port = port
        self.collection = target
        self.connection = redis.Redis(host=host, port=port)
