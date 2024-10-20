import pymysql


class MysqlClient:
    def __init__(self, host='localhost', port=3306, target='test', user=None, password=None):
        self.host = host
        self.port = port
        self.table = target
        self.connection = pymysql.connect(host=host,port=port, user=user, password=password)

    def filter(self, query: dict, project: list[str]=None):
        if not query:
            where = '1=1'
        else:
            where = ' AND '.join([f'{k}="{v}"' for k, v in query.items()])

        if project:
            columns = ', '.join(project)
        else:
            columns = '*'

        query = f'SELECT {columns} FROM {self.table} WHERE {where}'

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


if __name__ == '__main__':
    mysql = MysqlClient('localhost', 3306, 'test')

    with mysql.connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS test;")
        cursor.execute("USE test;")
        cursor.execute("CREATE TABLE IF NOT EXISTS teste (id VARCHAR(100), nome VARCHAR(100) NOT NULL);")
        cursor.execute("INSERT INTO teste VALUES ('key', 'value');")
        cursor.execute('SELECT * FROM teste;')
        assert (cursor.fetchone()) == ('key', 'value')
    mysql.connection.close()
