from typing import Any, Mapping

from bson import ObjectId
from pymongo import MongoClient
from pymongo.cursor import Cursor

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

    def get_data(self, **kwargs) -> Cursor[Mapping[str, Any] | Any] | list[Any]:
        query = kwargs.get('query')
        project = kwargs.get('project')
        projection = {field: 1 for field in project} if project else None
        if projection is not None and '_id' not in projection:
            projection['_id'] = 0
        results = []
        if not query:
            res = [x for x in self.collection.find(projection=projection)]
            results.extend(res)
        else:
            for q in query:
                if isinstance(q, dict):
                    results.extend([x for x in self.collection.find(q, projection=projection)])
                elif isinstance(q, list):
                    for sub_q in q:
                        if isinstance(sub_q, dict):
                            results.extend([x for x in self.collection.find(sub_q, projection=projection)])
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

    def delete_data_by_id(self, target_id: str):
        if ObjectId.is_valid(target_id):
            res = self.collection.delete_one({'_id': ObjectId(target_id)})
            if res.deleted_count > 0:
                return res
        return self.collection.delete_one({'id': target_id})

    def get_all(self):
        return self.collection.find()

    def filter(self, query: dict, project: list[str]=None):
        return [x for x in self.collection.find(filter=query, projection=project)]

    def get_data_by_id(self, target_id: str):
        if ObjectId.is_valid(target_id):
            res = self.collection.find_one({'_id': ObjectId(target_id)})
            if res:
                return res
        return self.collection.find_one({'id': target_id})

    def update_data_by_id(self, target_id: str, data: dict):
        if ObjectId.is_valid(target_id):
            res = self.collection.update_one({'_id': ObjectId(target_id)}, {'$set': data})
            if res.matched_count > 0:
                return res
        return self.collection.update_one({'id': target_id}, {'$set': data})

if __name__ == '__main__':
    client = MongodbClient(target='test')
    client.collection.insert_one({'key': 'value'})
    assert (client.collection.find_one({'key': 'value'}).get('key')) == 'value'
    client.connection.close()
