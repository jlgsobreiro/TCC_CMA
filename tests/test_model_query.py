import unittest

from bson import ObjectId

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


    def test_single_query_model_mongo(self):
        from query_model import QueryModel
        mongo_client = MongodbClient(target='test')
        mongo_client.collection.insert_one({'_id': ObjectId('678930b7724bd3b29457beeb'), 'key': 'value'})
        request = {
            "service": "mongodb",
            "database": "test_db",
            "schema": "test",
            "filter": [{"key": "value"}]
        }
        query = QueryModel(query_request=request)
        query.execute_query()
        print(query.result)
        assert query.result == {'mongodb__test_db__test': [{'_id': ObjectId('678930b7724bd3b29457beeb'), 'key': 'value'}]}
        print(query.result)

    def test_single_query_model_redis(self):
        from query_model import QueryModel
        redis_client = RedisClient(host='localhost', port=6379, database=0)
        redis_client.connection.set('key', 'value')
        request = {
            "service": "redis",
            "database": "0",
            "filter": [{"key": "value"}]
        }
        query = QueryModel(query_request=request)
        query.execute_query()
        assert query.result == {'redis__0': [{'key': 'value'}]}
        print(query.result)

    def test_single_query_model_mysql(self):
        from query_model import QueryModel
        mysql_client = MysqlClient(target='test', user='root', password='rootpassword', database='test_db')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO test VALUES ('id', 'value')")
            connection.commit()
        request = {
            "service": "mysql",
            "database": "test_db",
            "schema": "test",
            "filter": [{"id": "id"}]
        }
        query = QueryModel(query_request=request)
        query.execute_query()
        print(query.result)
        assert query.result == {'mysql__test_db__test': [{'id':'id', 'value': 'value'}]}

    def test_multiple_query_model_mysql_mongo(self):
        from query_model import QueryModel
        mysql_client = MysqlClient(target='test', user='root', password='rootpassword', database='test_db')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO test VALUES ('id', 'value')")
            connection.commit()
        mongo_client = MongodbClient(target='test', database='test_db')
        mongo_client.collection.insert_one({'id': 'value'})
        request = {
            "service": "mysql",
            "database": "test_db",
            "schema": "test",
            "filter": [{"id": "id"}],
            "on_result": {
                "service": "mongodb",
                "database": "test_db",
                "schema": "test",
                "filter": [{"id": {"mysql__test_db__test": "id"}}]
            }
        }
        query = QueryModel(query_request=request)
        query.execute_query()
        assert query.result == {'mysql__test_db__test': {'id': 'value'}, 'mongodb__test_db__test': {'_id': 'id'}}
        print(query.result)

    def test_multiple_query_model_redis_mongo(self):
        from query_model import QueryModel
        redis_client = RedisClient(host='localhost', port=6379, database=0)
        redis_client.connection.set('key', 'value')
        mongo_client = MongodbClient(target='test')
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
        redis_client = RedisClient(host='localhost', port=6379, database=0)
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
        mongo_client = MongodbClient(target='test')
        mongo_client.collection.insert_one({'key': 'value'})
        redis_client = RedisClient(host='localhost', port=6379, database=0)
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
        redis_client = RedisClient(host='localhost', port=6379, database=0)
        redis_client.connection.set('key', 'value')
        mongo_client = MongodbClient(target='test')
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

    def test_single_query_model_mysql_with_project(self):
        from query_model import QueryModel
        mysql_client = MysqlClient(target='test', user='root', password='rootpassword', database='test_db')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO test VALUES ('id', 'value')")
            connection.commit()
        request = {"mysql__test_db__test": {"filter": {"id": "id"}, "project": ["value", "id"]}}
        query = QueryModel(query_request=request)
        print(query.result)
        assert query.result == {'mysql__test_db__test': {'value': 'value', 'id': 'id'}}


if __name__ == '__main__':
    unittest.main()
