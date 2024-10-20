import unittest

from databases.databases_model import Databases
from databases.mongo_model import MongodbClient
from databases.mysql_model import MySQLConnection
from databases.redis_model import RedisClient


class MyTestCase(unittest.TestCase):

    def test_mongo_model(self):
        mongo_model = MongodbClient(collection='test')
        mongo_model.collection.insert_one({'key_test': 'value_test'})
        self.assertEqual(mongo_model.collection.find_one({'key_test': 'value_test'}).get('key_test'), 'value_test')

    def test_redis_model(self):
        redis_client = RedisClient('test')
        redis_client.connection.set('key_test', 'value_test')
        self.assertEqual(redis_client.connection.get('key_test'), b'value_test')

    def test_mysql_model(self):
        mysql_client = MySQLConnection(target='test',user='root',password='rootpassword')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute('CREATE DATABASE IF NOT EXISTS test_db')
                cursor.execute('USE test_db')
                cursor.execute('CREATE TABLE test (id VARCHAR(255), value VARCHAR(255))')
                cursor.execute("INSERT INTO test VALUES ('id', 'value')")
                cursor.execute("SELECT * FROM test;")
                assert (cursor.fetchone()) == ('id', 'value')
            connection.commit()
        self.assertEqual(True, False)

    def test_get_connection(self):
        database_mysql = Databases.objects(table='Teste1').first()
        connection = database_mysql.get_connection()
        self.assertEqual(connection.__class__.__name__, 'MySQLConnection')
        dabase_redis = Databases.objects(table='Teste2').first()
        connection = dabase_redis.get_connection()
        self.assertEqual(connection.__class__.__name__, 'RedisClient')
        database_mongodb = Databases.objects(table='Teste3').first()
        connection = database_mongodb.get_connection()
        self.assertEqual(connection.__class__.__name__, 'MongodbClient')

    def test_query_model(self):
        from query_model import QueryModel
        query = QueryModel(target_database='mysql__Teste1')
        self.assertEqual(query.database.__class__.__name__, 'MySQLConnection')
        query = QueryModel(target_database='redis__Teste2')
        self.assertEqual(query.database.__class__.__name__, 'RedisClient')
        query = QueryModel(target_database='mongodb__Teste3')
        self.assertEqual(query.database.__class__.__name__, 'MongodbClient')


if __name__ == '__main__':
    unittest.main()
