from redis import Redis

class RedisClient:
    def __init__(self, host, port, collection):
        self.host = host
        self.port = port
        self.collection = collection
        print(f'Connecting to Redis at {host}:{port}')
        self.connection = Redis(host=host, port=port, db=0, protocol=3)