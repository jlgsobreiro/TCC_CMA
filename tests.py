import unittest

from databases.databases_model import Databases
from databases.mongo_model import MongodbClient
from databases.mysql_model import MysqlClient
from databases.redis_model import RedisClient


class MyTestCase(unittest.TestCase):

    def test_mongo_model(self):
        mongo_model = MongodbClient(collection='test')
        mongo_model.collection.insert_one({'key_test': 'value_test'})
        self.assertEqual(mongo_model.collection.find_one({'key_test': 'value_test'}).get('key_test'), 'value_test')

    def test_redis_model(self):
        redis_client = RedisClient(host='localhost', port=6379, collection=0)
        redis_client.connection.set('key_test', 'value_test')
        self.assertEqual(redis_client.connection.get('key_test'), b'value_test')

    def test_mysql_model(self):
        mysql_client = MysqlClient(target='test', user='root', password='rootpassword')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute('CREATE DATABASE IF NOT EXISTS test_db')
                cursor.execute('USE test_db')
                cursor.execute('CREATE TABLE IF NOT EXISTS test (id VARCHAR(255), value VARCHAR(255))')
                cursor.execute("INSERT INTO test VALUES ('id', 'value')")
                cursor.execute("SELECT * FROM test;")
                assert (cursor.fetchone()) == ('id', 'value')
            connection.commit()

    def test_get_connection(self):
        set_list = [('mysql__Teste1', 'mysql'), ('redis__Teste2', 'redis'), ('mongodb__Teste3', 'mongodb')]
        for target_database, target in set_list:
            database = Databases.objects(table=target_database.split('__')[1]).first()
            connection = database.get_connection()
            self.assertEqual(connection.__class__.__name__, f'{target.capitalize()}Client')

    def test_query_model(self):
        from query_model import QueryModel
        set_list = [('mysql__Teste1', 'mysql'), ('redis__Teste2', 'redis'), ('mongodb__Teste3', 'mongodb')]
        for target_database, target in set_list:
            query = QueryModel(target=target_database)
            self.assertEqual(query.database.__class__.__name__, f'{target.capitalize()}Client')


if __name__ == '__main__':
    unittest.main()
