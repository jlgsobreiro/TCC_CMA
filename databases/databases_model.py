from mongoengine import Document, StringField

from databases.mongo_model import MongodbClient
from databases.mysql_model import MySQLConnection
# from databases.redis_model import RedisClient


class Databases(Document):
    name = StringField(required=True)
    host = StringField(required=True)
    port = StringField(required=True)
    database = StringField(required=True)

    def instantiate(self):
        if self.database == 'mysql':
            return MySQLConnection(
                host=self.host,
                port=self.port,
                target = self.name
            )
        elif self.database == 'redis':
            print(f'Connecting to Redis at {self.host}:{self.port}:{self.name}')
            # return RedisClient(host=self.host, port=self.port, collection=self.name)
        elif self.database == 'mongodb':
            return MongodbClient(host=self.host, port=self.port, target=self.name)
        else:
            raise ValueError('Database not supported')
