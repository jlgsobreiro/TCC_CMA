import pymysql

from databases.database_interface import DBInterface


class MysqlClient(DBInterface):
    def __init__(self,database='test_db', host='localhost', port=3306, target='test', user=None, password=None):
        self.host = host
        self.port = int(port)
        self.table = target
        self.connection = self.connect(user, password, database)

    def get_data(self, **kwargs) -> list[dict]:
        query = kwargs.get('query')
        queries = []
        if not query:
            queries.append(self.create_query(None))
        else:
            for q in query:
                queries.append(self.create_query(q))
        query = ' UNION '.join(queries)
        print(f'Query: {query}')

        return self.execute_query(query)

    def create_query(self, query):
        if not query:
            where = '1=1'
        else:
            where = ' AND '.join([f'{k}="{v}"' for k, v in query.items()])
        query = f'SELECT * FROM {self.table} WHERE {where}'
        return query

    def execute_query(self, query):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            columns = [i[0] for i in cursor.description]
            final_result = [{columns[i]: value for i, value in enumerate(row)} for row in result]
        return final_result

    def insert_data(self, data: dict):
        columns = ', '.join(data.keys())
        values = ', '.join([f'"{v}"' for v in data.values()])
        query = f'INSERT INTO {self.table} ({columns}) VALUES ({values})'
        print(f'Query: {query}')

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            self.connection.commit()

    def update_data(self, query: dict, data: dict):
        where = ' AND '.join([f'{k}="{v}"' for k, v in query.items()])
        set = ', '.join([f'{k}="{v}"' for k, v in data.items()])
        query = f'UPDATE {self.table} SET {set} WHERE {where}'
        print(f'Query: {query}')

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            self.connection.commit()

    def delete_data(self, query: dict):
        where = ' AND '.join([f'{k}="{v}"' for k, v in query.items()])
        query = f'DELETE FROM {self.table} WHERE {where}'
        print(f'Query: {query}')

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            self.connection.commit()

    def disconnect(self):
        self.connection.close()

    def connect(self, user, password, database):
        self.connection = pymysql.connect(host=self.host,port=self.port, user=user, password=password, database=database)
        return self.connection

if __name__ == '__main__':
    mysql = MysqlClient(host='localhost', port=3306, target='teste', database='test_db', user='root', password='rootpassword')

    with mysql.connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS test_db;")
        cursor.execute("USE test_db;")
        cursor.execute("CREATE TABLE IF NOT EXISTS teste (id VARCHAR(100), nome VARCHAR(100) NOT NULL);")
        cursor.execute("COMMIT;")
    mysql.insert_data({'id': 'id', 'nome': 'value'})
    mysql.insert_data({'id': 'id2', 'nome': 'value2'})
    print(mysql.get_data())
    filtered = mysql.get_data([{'id': 'id'}])
    print(filtered)
    assert filtered == [{'id': 'id', 'nome': 'value'}]
    mysql.delete_data({'id': 'id'})
    mysql.delete_data({'id': 'id2'})
    print(mysql.get_data())
    mysql.connection.close()
