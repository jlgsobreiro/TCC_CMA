from databases.databases_model import Databases


def setup_databases():
    db1 = Databases()
    db1.table = 'Teste1'
    db1.host = 'localhost'
    db1.port = 3306
    db1.database = 'mysql'
    db1.user = 'root'
    db1.password = 'rootpassword'
    db1.save()
    db2 = Databases()
    db2.table = 'Teste2'
    db2.host = 'localhost'
    db2.port = 6379
    db2.database = 'redis'
    db2.save()
    db3 = Databases()
    db3.table = 'Teste3'
    db3.host = 'localhost'
    db3.port = 27017
    db3.database = 'mongodb'
    db3.save()


def create_mysql_fixtures():
    db1 = Databases.objects(table='Teste1').first()
    mysql_client = db1.get_connection()
    with mysql_client.connection as connection:
        with connection.cursor() as cursor:
            cursor.execute('CREATE DATABASE IF NOT EXISTS test_db')
            cursor.execute('USE test_db')
            cursor.execute('CREATE TABLE test (id VARCHAR(255), value VARCHAR(255))')
            cursor.execute("INSERT INTO test VALUES ('id', 'value')")
            cursor.execute("INSERT INTO test VALUES ('id2', 'value2')")
            cursor.execute("INSERT INTO test VALUES ('id3', 'value3')")
        connection.commit()


def create_redis_fixtures():
    db2 = Databases.objects(table='Teste2').first()
    redis_client = db2.get_connection()
    redis_client.connection.set('key', 'value')
    redis_client.connection.set('key2', 'value2')
    redis_client.connection.set('key3', 'value3')


def create_mongo_fixtures():
    db3 = Databases.objects(table='Teste3').first()
    mongo_client = db3.get_connection()
    mongo_client.collection.insert_one({'key': 'value'})
    mongo_client.collection.insert_one({'key2': 'value2'})
    mongo_client.collection.insert_one({'key3': 'value3'})


def create_fixtures():
    setup_databases()
    create_mysql_fixtures()
    create_redis_fixtures()
    create_mongo_fixtures()

create_fixtures()