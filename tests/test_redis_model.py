import unittest

from databases.databases_model import Databases
from databases.redis_model import RedisClient
from fixtures import setup_databases


class MyTestCase(unittest.TestCase):
    def setUp(self):
        setup_databases()
        redis = RedisClient(host='localhost', port=6379, database=0)
        redis.connection.flushdb()

    def test_redis_model(self):
        redis_client = RedisClient(host='localhost', port=6379, database=0)
        redis_client.connection.set('key_test', 'value_test')
        self.assertEqual(redis_client.connection.get('key_test'), b'value_test')


if __name__ == '__main__':
    unittest.main()
