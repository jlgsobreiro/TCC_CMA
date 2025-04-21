import unittest

from bson import ObjectId

from databases.databases_model import Databases
from databases.mongo_model import MongodbClient
from fixtures import setup_databases


class MyTestCase(unittest.TestCase):
    def setUp(self):
        setup_databases()
        mongo = MongodbClient(target='test', database='test_db')
        mongo.db.drop_collection('test')

    def test_mongo_model(self):
        mongo_model = MongodbClient(target='test')
        mongo_model.insert_data({'key_test': 'value_test'})
        # mongo_model.collection.insert_one({'key_test': 'value_test'})
        self.assertEqual(mongo_model.collection.find_one({'key_test': 'value_test'}).get('key_test'), 'value_test')

    def test_mongo_model_get_data(self):
        mongo_model = MongodbClient(target='test')
        mongo_model.collection.insert_one({'key_test': 'value_test'})
        data = mongo_model.get_data(query=[{'key_test': 'value_test'}])
        self.assertEqual(data[0].get('key_test'), 'value_test')

    def test_mongo_model_get_data_return_many_rows(self):
        mongo_model = MongodbClient(target='test')
        mongo_model.collection.insert_many([
            {'key_test': 'value_test'},
            {'key_test2': 'value_test2'},
            {'key_test3': 'value_test3'}
        ])
        data = mongo_model.get_data()
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0].get('key_test'), 'value_test')
        self.assertEqual(data[1].get('key_test2'), 'value_test2')
        self.assertEqual(data[2].get('key_test3'), 'value_test3')


if __name__ == '__main__':
    unittest.main()
