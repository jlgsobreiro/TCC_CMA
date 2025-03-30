import unittest

from databases.databases_model import Databases
from databases.mongo_model import MongodbClient
from databases.mysql_model import MysqlClient
from databases.redis_model import RedisClient
from fixtures import setup_databases


class MyTestCase(unittest.TestCase):
    def setUp(self):
        setup_databases()
        mysql = MysqlClient(target='test', database='test_db', user='root', password='rootpassword')
        with mysql.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute('CREATE DATABASE IF NOT EXISTS test_db')
                cursor.execute('USE test_db')
                cursor.execute("DROP TABLE IF EXISTS test")
                cursor.execute('CREATE TABLE test (id VARCHAR(255), value VARCHAR(255))')
            connection.commit()
        mongo = MongodbClient(target='test', database='test_db')
        mongo.db.drop_collection('test')
        redis = RedisClient(host='localhost', port=6379, database=0)
        redis.connection.flushdb()

    def test_get_connection(self):
        set_list = [('mysql', 'test'), ('redis', 'test'), ('mongodb', 'test')]
        for target_database_type, target_database in set_list:
            database = Databases.objects(database_type=target_database_type).first()
            connection = database.get_connection()
            self.assertEqual(connection.__class__.__name__, f'{target_database_type.capitalize()}Client')

if __name__ == '__main__':
    unittest.main()
