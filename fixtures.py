from databases.databases_model import Databases, find_database
from databases.mysql_model import MysqlClient


def setup_databases():
    Databases.drop_collection()
    db1 = Databases(
        database_type='mysql',
        database='',
        params={
            'host': 'localhost',
            'port': 3306,
            'target': 'test',
            'user': 'root',
            'password': 'rootpassword'
        }
    )
    db1.save()
    db2 = Databases(database_type='redis', database='0', params={'host': 'localhost', 'port': 6379})
    db2.save()
    db3 = Databases(
        database_type='mongodb',
        database='test_db',
        params={'host': 'localhost', 'port': 27017, 'target':'test',}
    )
    db3.save()


def create_mysql_fixtures():
    db1 = find_database({'database_type': 'mysql'})
    mysql_client: MysqlClient = db1.get_connection()
    with mysql_client.connection as connection:
        with connection.cursor() as cursor:
            cursor.execute('CREATE DATABASE IF NOT EXISTS test_db')
            cursor.execute('USE test_db')
            cursor.execute('CREATE TABLE IF NOT EXISTS test (id VARCHAR(255), value VARCHAR(255))')
        connection.commit()
        mysql_client.insert_data({'id': '1', 'value': 'value'})
        mysql_client.insert_data({'id': '2', 'value': 'value2'})
        mysql_client.insert_data({'id': '3', 'value': 'value3'})


def create_redis_fixtures():
    db2 = find_database({'database_type': 'redis', 'database': '0'})
    redis_client = db2.get_connection()
    redis_client.insert_data({'key': 'value'})
    redis_client.insert_data({'key2': 'value2'})
    redis_client.insert_data({'key3': 'value3'})


def create_mongo_fixtures():
    db3 = find_database({'database_type': 'mongodb', 'database': 'test_db'})
    mongo_client = db3.get_connection()
    mongo_client.insert_data({'key': 'value'})
    mongo_client.insert_data({'key2': 'value2'})
    mongo_client.insert_data({'key3': 'value3'})


def create_fixtures():
    setup_databases()
    create_mysql_fixtures()
    create_redis_fixtures()
    create_mongo_fixtures()

if __name__ == '__main__':
    create_fixtures()