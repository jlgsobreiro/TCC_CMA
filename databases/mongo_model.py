from pymongo import MongoClient


class MongodbClient:
    def __init__(self, host='localhost', port=27017, collection=None):
        self.client = MongoClient(host, port)
        self.db = self.client['test']
        self.collection = self.db[collection]

if __name__ == '__main__':
    client = MongodbClient(collection='test')
    client.collection.insert_one({'key': 'value'})
    assert (client.collection.find_one({'key': 'value'}).get('key')) == 'value'
    client.client.close()
