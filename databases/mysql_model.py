import pymysql


class MySQLConnection:
    def __init__(self, host='localhost', port=3306, target='test', user=None, password=None):
        self.host = host
        self.port = port
        self.table = target
        self.connection = pymysql.connect(host=host,port=port, user=user, password=password)


if __name__ == '__main__':
    mysql = MySQLConnection('localhost', 3306, 'test')

    with mysql.connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS test;")
        cursor.execute("USE test;")
        cursor.execute("CREATE TABLE IF NOT EXISTS teste (id VARCHAR(100), nome VARCHAR(100) NOT NULL);")
        cursor.execute("INSERT INTO teste VALUES ('key', 'value');")
        cursor.execute('SELECT * FROM teste;')
        assert (cursor.fetchone()) == ('key', 'value')
    mysql.connection.close()
