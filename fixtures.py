from databases.databases_model import Databases
from databases.mongo_model import MongodbClient
from databases.mysql_model import MySQLConnection
from databases.redis_model import RedisClient


def setup_databases():
    db1 = Databases(name='Teste1', host='localhost', port='3306', database='mysql')
    db1.save()
    db2 = Databases(name='Teste2', host='localhost', port='6379', database='redis')
    db2.save()
    db3 = Databases(name='Teste3', host='localhost', port='27017', database='mongodb')
    db3.save()


def create_mysql_fixtures():
    mysql_client = MySQLConnection(host='localhost', port='3306', target='Teste1')
    mysql_client.connection.execute('CREATE TABLE test (key VARCHAR(255), value VARCHAR(255))')
    mysql_client.connection.execute("INSERT INTO test VALUES ('key', 'value')")
    mysql_client.connection.execute("INSERT INTO test VALUES ('key2', 'value2')")
    mysql_client.connection.execute("INSERT INTO test VALUES ('key3', 'value3')")
    mysql_client.connection.commit()


def create_redis_fixtures():
    redis_client = RedisClient(host='localhost', port='6379', target='Teste2')
    redis_client.connection.set('key', 'value')
    redis_client.connection.set('key2', 'value2')
    redis_client.connection.set('key3', 'value3')


def create_mongo_fixtures():
    mongo_client = MongodbClient(host='localhost', port='27017', target='Teste3')
    mongo_client.collection.insert_one({'key': 'value'})
    mongo_client.collection.insert_one({'key2': 'value2'})
    mongo_client.collection.insert_one({'key3': 'value3'})


def create_fixtures():
    setup_databases()
    create_mysql_fixtures()
    create_redis_fixtures()
    create_mongo_fixtures()
