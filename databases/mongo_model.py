from pymongo import MongoClient

from databases.database_interface import DBInterface


class MongodbClient(DBInterface):
    def __init__(self, host='localhost', port=27017, database='test_db', target=None):
        self.host = host
        self.port = int(port)
        self.connection = self.connect()
        self.db = self.connection[database]
        self.collection = self.db[target]

    def connect(self):
        return MongoClient(self.host, self.port)

    def disconnect(self):
        self.connection.close()

    def get_data(self, **kwargs) -> list[dict]:
        query = kwargs.get('query')
        if not query:
            return self.collection.find()
        results = []
        for q in query:
            if isinstance(q, dict):
                results.append(self.collection.find(q).next())
            elif isinstance(q, list):
                for sub_q in q:
                    if isinstance(sub_q, dict):
                        results.append(self.collection.find(sub_q).next())
                    else:
                        raise ValueError(f'Invalid query type: {type(sub_q)}')
            else:
                raise ValueError(f'Invalid query type: {type(q)}')
        return results

    def insert_data(self, data):
        return self.collection.insert_one(data)

    def update_data(self, query, data):
        return self.collection.update_one(query, data)

    def delete_data(self, query):
        return self.collection.delete_one(query)

    def get_all(self):
        return self.collection.find()

    def filter(self, query: dict, project: list[str]=None):
        return [x for x in self.collection.find(filter=query, projection=project)]

if __name__ == '__main__':
    client = MongodbClient(target='test')
    client.collection.insert_one({'key': 'value'})
    assert (client.collection.find_one({'key': 'value'}).get('key')) == 'value'
    client.connection.close()
