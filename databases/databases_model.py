from mongoengine import Document, StringField, connect, IntField, DictField

from databases.database_interface import DBInterface
from databases.mongo_model import MongodbClient
from databases.mysql_model import MysqlClient
from databases.redis_model import RedisClient


class Databases(Document):
    connect('databases')
    database_type = StringField(required=True)
    database = StringField(required=True)
    params = DictField()
    # table = StringField(required=True)

    def __init__(self, *args, **values):
        super(Databases, self).__init__()
        self.database_type = values.get('database_type')
        self.database = values.get('database')
        self.params = values.get('params')

    def get_connection(self) -> DBInterface:
        existing_clients = {
            "MongodbClient": MongodbClient,
            "MysqlClient": MysqlClient,
            "RedisClient": RedisClient
        }
        client_found = existing_clients.get(f"{self.database_type.capitalize()}Client")
        if client_found is None:
            raise ValueError(f'No client found for {self.database_type}')
        return client_found(database=self.database, **self.params)


        # if self.database_type == 'mysql':
        #     return MysqlClient(
        #         host=self.host,
        #         port=self.port,
        #         target = self.table,
        #         user=self.user,
        #         password=self.password,
        #         database=self.database
        #     )
        # elif self.database_type == 'redis':
        #     return RedisClient(host=self.host, port=self.port, collection=self.table)
        # elif self.database_type == 'mongodb':
        #     return MongodbClient(host=self.host, port=self.port, database=self.database, collection=self.table)
        # else:
        #     raise ValueError(f'Database {self.database_type} not supported')

def find_database(params) -> Databases:
    return Databases.objects(**params).first()