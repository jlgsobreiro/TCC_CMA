import unittest

from databases.databases_model import Databases
from databases.mongo_model import MongodbClient
from databases.mysql_model import MysqlClient
from databases.redis_model import RedisClient


class MyTestCase(unittest.TestCase):

    def setUp(self):
        mysql = MysqlClient(target='test', database='test_db', user='root', password='rootpassword')
        with mysql.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute('CREATE DATABASE IF NOT EXISTS test_db')
                cursor.execute('USE test_db')
                cursor.execute("DROP TABLE IF EXISTS test")
                cursor.execute('CREATE TABLE test (id VARCHAR(255), value VARCHAR(255))')
            connection.commit()
        mongo = MongodbClient(collection='test')
        mongo.db.drop_collection('test')
        redis = RedisClient(host='localhost', port=6379, collection=0)
        redis.connection.flushdb()

    def test_mongo_model(self):
        mongo_model = MongodbClient(collection='test')
        mongo_model.collection.insert_one({'key_test': 'value_test'})
        self.assertEqual(mongo_model.collection.find_one({'key_test': 'value_test'}).get('key_test'), 'value_test')

    def test_redis_model(self):
        redis_client = RedisClient(host='localhost', port=6379, collection=0)
        redis_client.connection.set('key_test', 'value_test')
        self.assertEqual(redis_client.connection.get('key_test'), b'value_test')

    def test_mysql_model(self):
        mysql_client = MysqlClient(target='test', user='root', password='rootpassword', database='test_db')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO test VALUES ('id', 'value')")
                cursor.execute("SELECT * FROM test;")
                assert (cursor.fetchone()) == ('id', 'value')
            connection.commit()

    def test_get_connection(self):
        set_list = [('mysql', 'test'), ('redis', 'test'), ('mongodb', 'test')]
        for target_database_type, target_database in set_list:
            database = Databases.objects(database_type=target_database_type).first()
            connection = database.get_connection()
            self.assertEqual(connection.__class__.__name__, f'{target_database_type.capitalize()}Client')

    def test_single_query_model_mysql(self):
        from query_model import QueryModel
        # set_list = [('mysql__Teste1', 'mysql'), ('redis__Teste2', 'redis'), ('mongodb__Teste3', 'mongodb')]
        mysql_client = MysqlClient(target='Test1', user='root', password='rootpassword', database='test_db')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute('CREATE DATABASE IF NOT EXISTS test_db')
                cursor.execute('USE test_db')
                cursor.execute('CREATE TABLE IF NOT EXISTS Teste1 (id VARCHAR(255), value VARCHAR(255))')
                cursor.execute("INSERT INTO Teste1 VALUES ('id', 'value')")
            connection.commit()
        request = {"mysql__test_db__Teste1": {"filter": {"id": "id"}}}
        query = QueryModel(query_request=request)
        print(query.result)
        assert query.result == {'mysql__test_db__Teste1': {'id': 'value'}}
        # for target_database, target in set_list:
        #     self.assertEqual(query.database.__class__.__name__, f'{target.capitalize()}Client')

    def test_single_query_model_redis(self):
        from query_model import QueryModel
        redis_client = RedisClient(host='localhost', port=6379, collection=0)
        redis_client.connection.set('key', 'value')
        request = {"redis__0": {"filter": {"key": "key"}}}
        query = QueryModel(query_request=request)
        assert query.result == {'redis__0': {'key': 'value'}}
        print(query.result)

    def test_single_query_model_mongo(self):
        from query_model import QueryModel
        mongo_client = MongodbClient(collection='test')
        mongo_client.collection.insert_one({'key': 'value'})
        request = {"mongodb__test_db__test": {"filter": {"key": "key"}}}
        query = QueryModel(query_request=request)
        assert query.result == {'mongodb__test_db__test': {'_id': 'key'}}
        print(query.result)

    def test_multiple_query_model_mysql_mongo(self):
        from query_model import QueryModel
        mysql_client = MysqlClient(target='test', user='root', password='rootpassword', database='test_db')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO test VALUES ('id', 'value')")
            connection.commit()
        mongo_client = MongodbClient(collection='test', database='test_db')
        mongo_client.collection.insert_one({'id': 'value'})
        request = {
            "mysql__test_db__test": {
                "filter": {"id": "id"},
                "on_result": {
                    "mongodb__test_db__test": {
                        "filter": {"id": {"mysql__test_db__test": "id"}}
                    }
                }
            }
        }
        query = QueryModel(query_request=request)
        assert query.result == {'mysql__test_db__test': {'id': 'value'}, 'mongodb__test_db__test': {'_id': 'id'}}
        print(query.result)

    def test_multiple_query_model_redis_mongo(self):
        from query_model import QueryModel
        redis_client = RedisClient(host='localhost', port=6379, collection=0)
        redis_client.connection.set('key', 'value')
        mongo_client = MongodbClient(collection='test')
        mongo_client.collection.insert_one({'key': 'value'})
        request = {
            "redis__0": {
                "filter": {"key": "key"},
                "on_result": {
                    "mongodb__test_db__test": {
                        "filter": {"key": {"redis__0": "key"}}
                    }
                }
            }
        }
        query = QueryModel(query_request=request)
        assert query.result == {'redis__0': {'key': 'value'}, 'mongodb__test_db__test': {'_id': 'key'}}
        print(query.result)

    def test_multiple_query_model_redis_mysql(self):
        from query_model import QueryModel
        redis_client = RedisClient(host='localhost', port=6379, collection=0)
        redis_client.connection.set('key', 'value')
        mysql_client = MysqlClient(target='test', user='root', password='rootpassword', database='test_db')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO test VALUES ('id', 'value')")
            connection.commit()
        request = {
            "redis__0": {
                "filter": {"key": "key"},
                "on_result": {
                    "mysql__test_db__test": {
                        "filter": {"value": {"redis__0": "key"}}
                    }
                }
            }
        }
        query = QueryModel(query_request=request)
        print(query.result)
        assert query.result == {'redis__0': {'key': 'value'}, 'mysql__test_db__test': {'id': 'value'}}

    def test_multiple_query_model_mongo_redis_mysql(self):
        from query_model import QueryModel
        mongo_client = MongodbClient(collection='test')
        mongo_client.collection.insert_one({'key': 'value'})
        redis_client = RedisClient(host='localhost', port=6379, collection=0)
        redis_client.connection.set('key', 'value')
        mysql_client = MysqlClient(target='test', user='root', password='rootpassword', database='test_db')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO test VALUES ('id', 'value')")
            connection.commit()
        request = {
            "mongodb__test_db__test": {
                "filter": {"key": "value"},
                "on_result": {
                    "redis__0": {
                        "filter": {"key": {"mongodb__test_db__test": "key"}},
                        "on_result": {
                            "mysql__test_db__test": {
                                "filter": {"value": {"redis__0": "key"}}
                            }
                        }
                    }
                }
            }
        }
        query = QueryModel(query_request=request)
        print(query.result)
        assert query.result == {'mongodb__test_db__test': {'_id': 'key'}, 'redis__0': {'key': 'value'}, 'mysql__test_db__test': {'id': 'value'}}

    def test_multiple_query_model_mysql_redis_mongo_with_alias(self):
        from query_model import QueryModel
        mysql_client = MysqlClient(target='test', user='root', password='rootpassword', database='test_db')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO test VALUES ('id', 'value')")
            connection.commit()
        redis_client = RedisClient(host='localhost', port=6379, collection=0)
        redis_client.connection.set('key', 'value')
        mongo_client = MongodbClient(collection='test')
        mongo_client.collection.insert_one({'key': 'value'})
        request = {
            "mongodb__test_db__test": {
                "filter": {"key": "value"},
                "alias" : "mongo",
                "on_result": {
                    "redis__0": {
                        "filter": {"key": {"mongo": "key"}},
                        "alias" : "redis",
                        "on_result": {
                            "mysql__test_db__test": {
                                "filter": {"value": {"redis": "key"}},
                                "alias" : "mysql"
                            }
                        }
                    }
                }
            }
        }
        query = QueryModel(query_request=request)
        print(query.result)
        assert query.result == {'mongo': {'_id': 'key'}, 'redis': {'key': 'value'}, 'mysql': {'id': 'value'}}

if __name__ == '__main__':
    unittest.main()
