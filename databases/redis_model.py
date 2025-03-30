import redis
from databases.database_interface import DBInterface


class RedisClient(DBInterface):
    def __init__(self, database=0, host="localhost", port=6379):
        self.host = host
        self.port = int(port)
        self.db = int(database)
        self.connection: redis.Redis
        self.connect()

    def connect(self):
        try:
            self.connection = redis.Redis(host=self.host, port=self.port, db=self.db)
            print(f'Connected to Redis at {self.host}:{self.port}')
        except redis.ConnectionError as e:
            print(f'Failed to connect to Redis: {e}')
            self.connection = None

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print('Disconnected from Redis')

    def get_data(self, query: list[dict] = None) -> list[dict]:
        try:
            if not query:
                keys = self.connection.keys()
                return [{key.decode('utf-8'): self.connection.get(key).decode('utf-8')} for key in keys]
            result = []
            for q in query:
                key = list(q.keys())[0]
                value = self.connection.get(key)
                if value:
                    result.append({key: value.decode('utf-8')})
            return result
        except redis.RedisError as e:
            print(f'Error getting data: {e}')
            return []

    def insert_data(self, data: dict) -> list[dict]:
        key, value = list(data.items())[0]
        try:
            self.connection.set(key, value)
            return [{key: value}]
        except redis.RedisError as e:
            print(f'Error inserting data: {e}')
            return []

    def delete_data(self, query: dict) -> list[dict]:
        key = list(query.keys())[0]
        try:
            result = self.connection.delete(key)
            return [{key: result}]
        except redis.RedisError as e:
            print(f'Error deleting data: {e}')
            return []

    def update_data(self, query: dict, data: dict) -> list[dict]:
        key = list(query.keys())[0]
        value = list(data.values())[0]
        try:
            self.connection.set(key, value)
            return [{key: value}]
        except redis.RedisError as e:
            print(f'Error updating data: {e}')
            return []


if __name__ == '__main__':
    redis_client = RedisClient(database=0, host="localhost", port=6379)
    redis_client.insert_data({'key': 'value'})
    redis_client.insert_data({'key2': 'value2'})
    print(redis_client.get_data())  # Should print all keys and their values as a list of dictionaries
    print(redis_client.get_data([{'key': 'value'}]))  # Should print [{'key': 'value'}]
    print(redis_client.get_data([{'key2': 'value'}]))  # Should print [{'key': 'value'}]
    redis_client.disconnect()