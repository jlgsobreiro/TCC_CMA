from mongoengine import Document, StringField, connect, IntField

from databases.mongo_model import MongodbClient
from databases.mysql_model import MysqlClient
from databases.redis_model import RedisClient


class Databases(Document):
    connect('databases')
    table = StringField(required=True)
    host = StringField(required=True)
    port = IntField(required=True)
    database = StringField(required=True)
    database_type = StringField(required=True)
    user = StringField()
    password = StringField()

    def get_connection(self):
        if self.database_type == 'mysql':
            return MysqlClient(
                host=self.host,
                port=self.port,
                target = self.table,
                user=self.user,
                password=self.password,
                database=self.database
            )
        elif self.database_type == 'redis':
            return RedisClient(host=self.host, port=self.port, collection=self.table)
        elif self.database_type == 'mongodb':
            return MongodbClient(host=self.host, port=self.port, database=self.database, collection=self.table)
        else:
            raise ValueError(f'Database {self.database_type} not supported')
