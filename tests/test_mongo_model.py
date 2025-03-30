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


if __name__ == '__main__':
    unittest.main()
