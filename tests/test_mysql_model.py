import unittest

from databases.databases_model import Databases
from databases.mysql_model import MysqlClient
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

    def test_mysql_model(self):
        mysql_client = MysqlClient(target='test', user='root', password='rootpassword', database='test_db')
        with mysql_client.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO test VALUES ('id', 'value')")
                cursor.execute("SELECT * FROM test;")
                assert (cursor.fetchone()) == ('id', 'value')
            connection.commit()

if __name__ == '__main__':
    unittest.main()
