from redis import Redis

class RedisClient:
    def __init__(self, host="localhost", port=6379, collection=None):
        self.host = host
        self.port = port
        self.collection = collection
        print(f'Connecting to Redis at {host}:{port}')
        self.connection = Redis(host=self.host, port= self.port, db=self.collection)

    def filter(self, query: dict, project: list[str]=None):
        if not query:
            return None
        key = list(query.keys())[0]
        return self.connection.get(key)


if __name__ == '__main__':
    redis = RedisClient('localhost', 6379, 0)
    redis.connection.set('key', 'value')
    assert redis.connection.get('key') == b'value'
    redis.connection.close()
