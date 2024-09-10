from pymongo import MongoClient


class MongodbClient:
    def __init__(self, host='localhost', port=27017, target=None):
        self.client = MongoClient(host, port)
        self.db = self.client['test']
        self.collection = self.db[target]

