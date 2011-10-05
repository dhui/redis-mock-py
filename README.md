redis-mock-py

A Python mock library for the redis-py client.

Note: This module is not thread safe
Currently only a few Redis sorted set commands are supported (ZADD, ZRANGE, ZRANGEBYSCORE, ZREVRANGE, ZREVRANGEBYSCORE)
I will be adding more commands in the future.
If you want more commands added, send me a message via github (username: dhui).


Usage:

To start using the Redis mock, you'll need to add the following imports:
import mock
import redis_mock

Then in your setUp() function in your unit test class, call:
redis_mock.flush_db()

In any of your test functions that use the redis-py library, add the decorator:
@mock.patch.object(redis.Redis, 'execute_command')

That same test function must take the argument:
mock_execute_command

Inside that same test function, set mock_execute_command's side effect:
mock_execute_command.side_effect = redis_mock.execute_command

Example:
class TestSuite(unittest.TestCase):
    def setUp(self):
        redis_mock.flush_db()

    @mock.patch.object(redis.Redis, 'execute_command')
    def simple_test(self, mock_execute_command):
        mock_execute_command.side_effect = redis_mock.execute_command
