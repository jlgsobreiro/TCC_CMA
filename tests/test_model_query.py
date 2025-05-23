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
        assert query.result == {
            'mongodb__test_db__test': [{'_id': ObjectId('678930b7724bd3b29457beeb'), 'key': 'value'}]}
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
        assert query.result == {'mysql__test_db__test': [{'id': 'id', 'value': 'value'}]}

    def test_multiple_query_model_mysql_mongo(self):
        from query_model import QueryModel
        mongo_client = MongodbClient(target='test', database='test_db')
        inserted = mongo_client.collection.insert_one({'id': 'id2'})
        mysql_client = MysqlClient(target='test', user='root', password='rootpassword', database='test_db')
        request = {
            "service": "mysql",
            "database": "test_db",
            "schema": "test",
            "filter": [{"id": "id2"}],
            "on_result": {
                "service": "mongodb",
                "database": "test_db",
                "schema": "test",
                "filter": [{"id": {"mysql__test_db__test": "id"}}]
            }
        }
        query = QueryModel(query_request=request)
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO test VALUES ('id2', 'value2')")
            connection.commit()
            query.execute_query()

            print(query.result)
            expexted = {
                'mysql__test_db__test':
                    [{'id': 'id2', 'value': 'value2'}],
                'mongodb__test_db__test': [
                    {'_id': inserted.inserted_id, 'id': 'id2'}
                ]
            }
            assert query.result == expexted

    def test_multiple_query_model_redis_mongo(self):
        from query_model import QueryModel
        redis_client = RedisClient(host='localhost', port=6379, database=0)
        redis_client.connection.set('key', 'value')
        mongo_client = MongodbClient(target='test')
        inserted = mongo_client.collection.insert_one({'key': 'value'})
        request = {
            "service": "redis",
            "database": "0",
            "filter": [{"key": "key"}],
            "on_result": {
                "service": "mongodb",
                "database": "test_db",
                "schema": "test",
                "filter": [{"key": {"redis__0": "key"}}]
            }
        }
        query = QueryModel(query_request=request)
        query.execute_query()
        print(query.result)
        assert query.result == {'redis__0': [{'key': 'value'}],
                                'mongodb__test_db__test': [{'_id': inserted.inserted_id, 'key': 'value'}]}

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
            "service": "redis",
            "database": "0",
            "filter": [{"key": "key"}],
            "on_result": {
                "service": "mysql",
                "database": "test_db",
                "schema": "test",
                "filter": [{"value": {"redis__0": "key"}}]
            }
        }
        query = QueryModel(query_request=request)
        query.execute_query()
        print(query.result)
        assert query.result == {'redis__0': [{'key': 'value'}],
                                'mysql__test_db__test': [{'id': 'id', 'value': 'value'}]}

    def test_multiple_query_model_mongo_redis_mysql(self):
        from query_model import QueryModel
        mongo_client = MongodbClient(target='test')
        inserted = mongo_client.collection.insert_one({'key': 'value'})
        redis_client = RedisClient(host='localhost', port=6379, database=0)
        redis_client.connection.set('key', 'value')
        mysql_client = MysqlClient(target='test', user='root', password='rootpassword', database='test_db')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO test VALUES ('id', 'value')")
            connection.commit()
        request = {
            "service": "mongodb",
            "database": "test_db",
            "schema": "test",
            "filter": [{"key": "value"}],
            "on_result": {
                "service": "redis",
                "database": "0",
                "filter": [{"key": {"mongodb__test_db__test": "key"}}],
                "on_result": {
                    "service": "mysql",
                    "database": "test_db",
                    "schema": "test",
                    "filter": [{"value": {"redis__0": "key"}}]
                }
            }
        }
        query = QueryModel(query_request=request)
        query.execute_query()
        print(query.result)
        assert query.result == {
            'mongodb__test_db__test': [{'_id': inserted.inserted_id, 'key': 'value'}],
            'redis__0': [{'key': 'value'}],
            'mysql__test_db__test': [{'id': 'id', 'value': 'value'}]
        }

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
        inserted = mongo_client.collection.insert_one({'key': 'value'})
        request = {
            "service": "mongodb",
            "database": "test_db",
            "schema": "test",
            "alias": "mongodb",
            "filter": [{"key": "value"}],
            "on_result": {
                "service": "redis",
                "database": "0",
                "alias": "redis",
                "filter": [{"key": {"mongodb": "key"}}],
                "on_result": {
                    "service": "mysql",
                    "database": "test_db",
                    "schema": "test",
                    "alias": "mysql",
                    "filter": [{"value": {"redis": "key"}}]
                }
            }
        }
        query = QueryModel(query_request=request)
        query.execute_query()
        print(query.result)
        assert query.result == {
            'mongodb': [{'_id': inserted.inserted_id, 'key': 'value'}],
            'redis': [{'key': 'value'}],
            'mysql': [{'id': 'id', 'value': 'value'}]
        }

    def test_single_query_model_mysql_with_project(self):
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
            "project": ["value"],
            "filter": [{"id": "id"}]
        }
        query = QueryModel(query_request=request)
        query.execute_query()
        print(query.result)
        assert query.result == {'mysql__test_db__test': [{'value': 'value'}]}

    def test_single_query_model_mysql_with_project_and_alias(self):
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
            "project": ["value"],
            "alias": "mysql",
            "filter": [{"id": "id"}]
        }
        query = QueryModel(query_request=request)
        query.execute_query()
        print(query.result)
        assert query.result == {'mysql': [{'value': 'value'}]}

    def test_single_query_model_mysql_with_project_and_alias_and_on_result(self):
        from query_model import QueryModel
        mysql_client = MysqlClient(target='test', user='root', password='rootpassword', database='test_db')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO test VALUES ('id', 'value')")
            connection.commit()
        mongo_client = MongodbClient(target='test')
        inserted = mongo_client.collection.insert_one({'key': 'value'})
        request = {
            "service": "mysql",
            "database": "test_db",
            "schema": "test",
            "project": ["value"],
            "alias": "mysql",
            "filter": [{"id": "id"}],
            "on_result": {
                "service": "mongodb",
                "database": "test_db",
                "schema": "test",
                "filter": [{"key": {"mysql": "value"}}]
            }
        }
        query = QueryModel(query_request=request)
        query.execute_query()
        print(query.result)
        assert query.result == {'mysql': [{'value': 'value'}],
                                'mongodb__test_db__test': [{'_id': inserted.inserted_id, 'key': 'value'}]}


if __name__ == '__main__':
    unittest.main()
