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

    def get_data(self, **kwargs) -> list[dict]:
        query = kwargs.get('query')
        try:
            if not query:
                keys = self.connection.keys()
                return [
                    {'id': key.decode('utf-8'), 'value': self.connection.get(key).decode('utf-8')}
                    for key in keys
                ]
            result = []
            for q in query:
                key = list(q.values())[0]
                value = self.connection.get(key)
                if value:
                    result.append({'id': key, 'value': value.decode('utf-8')})
            return result
        except redis.RedisError as e:
            print(f'Error getting data: {e}')
            return []

    def insert_data(self, data: dict) -> list[dict]:
        key = data.get('id')
        value = data.get('external_id')
        try:
            self.connection.set(key, value)
            return [{'id': key, 'value': value}]
        except redis.RedisError as e:
            print(f'Error inserting data: {e}')
            return []

    def delete_data(self, query: dict) -> list[dict]:
        key = list(query.keys())[0]
        try:
            result = self.connection.delete(key)
            return [{'id': key, 'deleted': bool(result)}]
        except redis.RedisError as e:
            print(f'Error deleting data: {e}')
            return []

    def update_data(self, query: dict, data: dict) -> list[dict]:
        key = list(query.keys())[0]
        value = list(data.values())[0]
        try:
            self.connection.set(key, value)
            return [{'id': key, 'value': value}]
        except redis.RedisError as e:
            print(f'Error updating data: {e}')
            return []

    def get_all(self) -> list[dict]:
        try:
            keys = self.connection.keys()
            return [
                {'id': key.decode('utf-8'), 'value': self.connection.get(key).decode('utf-8')}
                for key in keys
            ]
        except redis.RedisError as e:
            print(f'Error getting all data: {e}')
            return []

    def delete_data_by_id(self, target_id: str) -> dict:
        try:
            result = self.connection.delete(target_id)
            return {'id': target_id, 'deleted': bool(result)}
        except redis.RedisError as e:
            print(f'Error deleting data by id: {e}')
            return {'id': target_id, 'deleted': False, 'error': str(e)}

    def get_data_by_id(self, target_id: str) -> dict:
        value = self.connection.get(target_id)
        if value:
            return {'id': target_id, 'value': value.decode('utf-8')}
        return {'id': target_id, 'value': None}

    def update_data_by_id(self, target_id: str, data: dict) -> dict:
        try:
            value = list(data.values())[0]
            self.connection.set(target_id, value)
            return {'id': target_id, 'value': value}
        except redis.RedisError as e:
            print(f'Error updating data by id: {e}')
            return {'id': target_id, 'error': str(e)}


if __name__ == '__main__':
    redis_client = RedisClient(database=0, host="localhost", port=6379)
    redis_client.insert_data({'key': 'value'})
    redis_client.insert_data({'key2': 'value2'})
    print(redis_client.get_data())  # Should print all keys and their values as a list of dictionaries
    print(redis_client.get_data([{'key': 'value'}]))  # Should print [{'key': 'value'}]
    print(redis_client.get_data([{'key2': 'value'}]))  # Should print [{'key': 'value'}]
    redis_client.disconnect()