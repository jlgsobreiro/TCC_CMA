from redis import Redis

from databases.database_interface import DBInterface


class RedisClient(DBInterface):
    def __init__(self, database=0, host="localhost", port=6379):
        self.host = host
        self.port = int(port)
        self.db = int(database)
        print(f'Connecting to Redis at {host}:{port}')
        self.connection = Redis(host=self.host, port= self.port, db=self.db)

    def get_data(self, query: dict):
        if not query:
            return None
        key = list(query.keys())[0]
        return {key: str(self.connection.get(key), encoding='utf-8')}

    def get_all(self):
        return self.connection.keys()

    def insert_data(self, data: dict):
        key, value = list(data.items())[0]
        self.connection.set(key, value)
        return {key: value}

    def delete_data(self, query: dict):
        key = list(query.keys())[0]
        return self.connection.delete(key)

    def update_data(self, query: dict, data: dict):
        key = list(query.keys())[0]
        value = list(data.values())[0]
        self.connection.set(key, value)
        return {key: value}

    def filter(self, query: dict, project: list[str]=None):
        key = list(query.keys())[0]
        return {key: str(self.connection.get(key), encoding='utf-8')}

    def disconnect(self):
        self.connection.close()

    def connect(self):
        self.connection = Redis(host=self.host, port=self.port, db=self.db)
        return self.connection


if __name__ == '__main__':
    redis = RedisClient(database=0, host="localhost", port=6379)
    redis.insert_data({'key': 'value'})
    assert redis.get_data({'key':'value'}) == {'key': 'value'}
    # redis.connection.set('key', 'value')
    # assert redis.connection.get('key') == b'value'
    redis.disconnect()
