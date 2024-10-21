from pymongo import MongoClient


class MongodbClient:
    def __init__(self, host='localhost', port=27017, database='test_db' , collection=None):
        self.client = MongoClient(host, port)
        self.db = self.client[database]
        self.collection = self.db[collection]

    def filter(self, query: dict, project: list[str]=None):
        return self.collection.find(filter=query, projection=project)

if __name__ == '__main__':
    client = MongodbClient(collection='test')
    client.collection.insert_one({'key': 'value'})
    assert (client.collection.find_one({'key': 'value'}).get('key')) == 'value'
    client.client.close()
