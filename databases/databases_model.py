from mongoengine import Document, StringField, connect, IntField

from databases.mongo_model import MongodbClient
from databases.mysql_model import MySQLConnection
from databases.redis_model import RedisClient


class Databases(Document):
    connect('databases')
    table = StringField(required=True)
    host = StringField(required=True)
    port = IntField(required=True)
    database = StringField(required=True)
    user = StringField()
    password = StringField()

    def get_connection(self):
        if self.database == 'mysql':
            return MySQLConnection(
                host=self.host,
                port=self.port,
                target = self.table,
                user=self.user,
                password=self.password
            )
        elif self.database == 'redis':
            return RedisClient(host=self.host, port=self.port, collection=self.table)
        elif self.database == 'mongodb':
            return MongodbClient(host=self.host, port=self.port, collection=self.table)
        else:
            raise ValueError('Database not supported')
