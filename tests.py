"""
Unit tests for the Redis mock

To run tests, simply go to the redis_mock directory and run:
python tests.py
"""

import redis
import redis_mock
import mock
import unittest

redis_c = redis.Redis()  # connect with the defaults (it doesn't matter in the unittest b/c a connection will never be created with the mocks)


class RedisMockTest(unittest.TestCase):

    def setUp(self):
        redis_mock.flush_db()

    @mock.patch.object(redis.Redis, 'execute_command')
    def test_zadd_single_member(self, mock_execute_command):
        mock_execute_command.side_effect = redis_mock.execute_command

        # Test simple zadd
        self.assertTrue(redis_c.zadd("mykey1", "member1", 5))

        # Test getting all elements back with zrange (with and without scores)
        self.assertEqual(redis_c.zrange("mykey1", 0, -1), ["member1"])
        self.assertEqual(redis_c.zrange("mykey1", 0, -1, withscores=True), [("member1", 5)])

        # Test simple zadd with kwarg syntax
        self.assertTrue(redis_c.zadd("mykey1", member2=10))
        self.assertEqual(redis_c.zrange("mykey1", 0, -1, withscores=True), [("member1", 5), ("member2", 10)])

        # Test that overwritting a member works (it should return false though b/c the member was not created)
        self.assertFalse(redis_c.zadd("mykey1", "member1", 6))
        self.assertEqual(redis_c.zrange("mykey1", 0, -1, withscores=True), [("member1", 6), ("member2", 10)])
        self.assertFalse(redis_c.zadd("mykey1", "member1", 5))
        self.assertEqual(redis_c.zrange("mykey1", 0, -1, withscores=True), [("member1", 5), ("member2", 10)])

    @mock.patch.object(redis.Redis, 'execute_command')
    def test_zadd_multiple_members(self, mock_execute_command):
        mock_execute_command.side_effect = redis_mock.execute_command

        expected_data = []

        # Test multiple zadd
        for i in xrange(10):
            self.assertTrue(redis_c.zadd("mykey", "member%s" % i, i))
            expected_data.append(("member%s" % i, i))
        self.assertEqual(redis_c.zrange("mykey", 0, -1, withscores=True), expected_data)

    @mock.patch.object(redis.Redis, 'execute_command')
    def test_zrange(self, mock_execute_command):
        mock_execute_command.side_effect = redis_mock.execute_command

        # setup the data
        expected_data = []

        for i in xrange(10):
            self.assertTrue(redis_c.zadd("mykey", "member%s" % i, i))
            expected_data.append(("member%s" % i, i))

        # Test getting the whole range
        self.assertEqual(redis_c.zrange("mykey", 0, -1, withscores=True), expected_data)
        self.assertEqual(redis_c.zrange("mykey", 0, -1), [member for member, score in expected_data])

        # Test getting a single element via zrange
        self.assertEqual(redis_c.zrange("mykey", 0, 0), ["member0"])
        self.assertEqual(redis_c.zrange("mykey", 0, 0, withscores=True), [("member0", 0)])
        self.assertEqual(redis_c.zrange("mykey", 4, 4), ["member4"])
        self.assertEqual(redis_c.zrange("mykey", 4, 4, withscores=True), [("member4", 4)])
        self.assertEqual(redis_c.zrange("mykey", -1, -1), ["member9"])
        self.assertEqual(redis_c.zrange("mykey", -1, -1, withscores=True), [("member9", 9)])
        self.assertEqual(redis_c.zrange("mykey", -3, -3), ["member7"])
        self.assertEqual(redis_c.zrange("mykey", -3, -3, withscores=True), [("member7", 7)])

        # Test getting a range
        range = redis_c.zrange("mykey", 2, 7, withscores=True)
        self.assertEqual(len(range), 6)
        self.assertEqual(range, expected_data[2:8])

        # Test getting a range where the end is out of bounds
        range = redis_c.zrange("mykey", 5, 999, withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[5:])

        # Test getting a range with wrap around
        range = redis_c.zrange("mykey", 7, -2, withscores=True)
        self.assertEqual(len(range), 2)
        self.assertEqual(range, expected_data[7:9])

        # Test getting negative range
        range = redis_c.zrange("mykey", -7, -2, withscores=True)
        self.assertEqual(len(range), 6)
        self.assertEqual(range, expected_data[3:9])

        # Test getting negative range with wrap around
        range = redis_c.zrange("mykey", -7, 2, withscores=True)
        self.assertEqual(len(range), 0)
        self.assertEqual(range, [])

        # Test getting a range where the start is out of bounds
        range = redis_c.zrange("mykey", -999, 2, withscores=True)
        self.assertEqual(len(range), 0)
        self.assertEqual(range, [])

        # Test getting a range where the start and end are out of bounds
        range = redis_c.zrange("mykey", -999, 999, withscores=True)
        self.assertEqual(len(range), 0)
        self.assertEqual(range, [])

        # Test getting a range where the start and end are out of bounds
        range = redis_c.zrange("mykey", -9999, -999, withscores=True)
        self.assertEqual(len(range), 0)
        self.assertEqual(range, [])


    @mock.patch.object(redis.Redis, 'execute_command')
    def test_zrevrange(self, mock_execute_command):
        mock_execute_command.side_effect = redis_mock.execute_command

        # setup the data
        expected_data = []

        for i in xrange(10):
            self.assertTrue(redis_c.zadd("mykey", "member%s" % i, i))
            expected_data.append(("member%s" % i, i))
        expected_data.reverse()

        # Test basic zrevrange
        self.assertEqual(redis_c.zrevrange("mykey", 0, -1, withscores=True), expected_data)
        self.assertEqual(redis_c.zrevrange("mykey", 0, -1), [member for member, score in expected_data])

        # Test getting a range where the end is out of bounds
        range = redis_c.zrevrange("mykey", 5, 999, withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[5:])

        # Test getting a range with wrap around
        range = redis_c.zrevrange("mykey", 7, -2, withscores=True)
        self.assertEqual(len(range), 2)
        self.assertEqual(range, expected_data[7:9])

        # Test getting negative range
        range = redis_c.zrevrange("mykey", -7, -2, withscores=True)
        self.assertEqual(len(range), 6)
        self.assertEqual(range, expected_data[3:9])

        # Test getting negative range with wrap around
        range = redis_c.zrevrange("mykey", -7, 2, withscores=True)
        self.assertEqual(len(range), 0)
        self.assertEqual(range, [])

        # Test getting a range where the start is out of bounds
        range = redis_c.zrevrange("mykey", -999, 2, withscores=True)
        self.assertEqual(len(range), 0)
        self.assertEqual(range, [])

        # Test getting a range where the start and end are out of bounds
        range = redis_c.zrevrange("mykey", -999, 999, withscores=True)
        self.assertEqual(len(range), 0)
        self.assertEqual(range, [])

        # Test getting a range where the start and end are out of bounds
        range = redis_c.zrevrange("mykey", -9999, -999, withscores=True)
        self.assertEqual(len(range), 0)
        self.assertEqual(range, [])

    @mock.patch.object(redis.Redis, 'execute_command')
    def test_zrangebyscore(self, mock_execute_command):
        mock_execute_command.side_effect = redis_mock.execute_command

        # setup the data
        expected_data = []

        for i in xrange(10):
            self.assertTrue(redis_c.zadd("mykey", "member%s" % i, i))
            expected_data.append(("member%s" % i, i))

        # Test getting the whole range
        self.assertEqual(redis_c.zrangebyscore("mykey", "-inf", "+inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrangebyscore("mykey", "-inf", "+inf"), [member for member, score in expected_data])
        self.assertEqual(redis_c.zrangebyscore("mykey", "-inf", "inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrangebyscore("mykey", "-inf", "inf"), [member for member, score in expected_data])

        self.assertEqual(redis_c.zrangebyscore("mykey", "-inf", "(+inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrangebyscore("mykey", "-inf", "(+inf"), [member for member, score in expected_data])
        self.assertEqual(redis_c.zrangebyscore("mykey", "-inf", "(inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrangebyscore("mykey", "-inf", "(inf"), [member for member, score in expected_data])

        self.assertEqual(redis_c.zrangebyscore("mykey", "(-inf", "(+inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrangebyscore("mykey", "(-inf", "(+inf"), [member for member, score in expected_data])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(-inf", "(inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrangebyscore("mykey", "(-inf", "(inf"), [member for member, score in expected_data])

        self.assertEqual(redis_c.zrangebyscore("mykey", "(-inf", "+inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrangebyscore("mykey", "(-inf", "+inf"), [member for member, score in expected_data])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(-inf", "inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrangebyscore("mykey", "(-inf", "inf"), [member for member, score in expected_data])

        # Test getting invalid or empty ranges
        self.assertEqual(redis_c.zrangebyscore("mykey", "+inf", "-inf"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "inf", "-inf"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "inf", "inf"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "-inf", "-inf"), [])

        self.assertEqual(redis_c.zrangebyscore("mykey", "+inf", "(-inf"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "inf", "(-inf"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "inf", "(inf"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "-inf", "(-inf"), [])

        self.assertEqual(redis_c.zrangebyscore("mykey", "(+inf", "(-inf"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(inf", "(-inf"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(inf", "(inf"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(-inf", "(-inf"), [])

        self.assertEqual(redis_c.zrangebyscore("mykey", "(+inf", "-inf"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(inf", "-inf"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(inf", "inf"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(-inf", "-inf"), [])

        self.assertEqual(redis_c.zrangebyscore("mykey", "(0", 0), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", 0, "(0"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", -9999, -999), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", 999, 9999), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", 9999, 999), [])

        self.assertEqual(redis_c.zrangebyscore("mykey", "(-9999", -999), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(999", 9999), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(9999", 999), [])

        self.assertEqual(redis_c.zrangebyscore("mykey", "(-9999", "(-999"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(999", "(9999"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(9999", "(999"), [])

        self.assertEqual(redis_c.zrangebyscore("mykey", -9999, "(-999"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", 999, "(9999"), [])
        self.assertEqual(redis_c.zrangebyscore("mykey", 9999, "(999"), [])


        # Test getting a single element via zrangebyscore
        self.assertEqual(redis_c.zrangebyscore("mykey", 0, 0), ["member0"])
        self.assertEqual(redis_c.zrangebyscore("mykey", 0, 0, withscores=True), [("member0", 0)])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(0", 1), ["member1"])
        self.assertEqual(redis_c.zrangebyscore("mykey", -10, 0), ["member0"])
        self.assertEqual(redis_c.zrangebyscore("mykey", 0, "(1"), ["member0"])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(-10", 0), ["member0"])
        self.assertEqual(redis_c.zrangebyscore("mykey", "(-10", "(1"), ["member0"])

        # Test parsing of start and end scores
        self.assertEqual(redis_c.zrangebyscore("mykey", 0, 0), ["member0"])
        self.assertEqual(redis_c.zrangebyscore("mykey", "0", 0), ["member0"])
        self.assertEqual(redis_c.zrangebyscore("mykey", 0, "0"), ["member0"])
        self.assertEqual(redis_c.zrangebyscore("mykey", "0", "0"), ["member0"])
        self.assertEqual(redis_c.zrangebyscore("mykey", -10, 0), ["member0"])
        self.assertEqual(redis_c.zrangebyscore("mykey", "-10", 0), ["member0"])
        self.assertEqual(redis_c.zrangebyscore("mykey", -10, "0"), ["member0"])
        self.assertEqual(redis_c.zrangebyscore("mykey", "-10", "0"), ["member0"])

        # Test getting a range
        range = redis_c.zrangebyscore("mykey", 2, 7, withscores=True)
        self.assertEqual(len(range), 6)
        self.assertEqual(range, expected_data[2:8])

        range = redis_c.zrangebyscore("mykey", "(2", 7, withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[3:8])

        range = redis_c.zrangebyscore("mykey", 2, "(7", withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[2:7])

        range = redis_c.zrangebyscore("mykey", "(2", "(7", withscores=True)
        self.assertEqual(len(range), 4)
        self.assertEqual(range, expected_data[3:7])

        # Test getting a range where the max is out of bounds
        range = redis_c.zrangebyscore("mykey", 5, 999, withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[5:])

        range = redis_c.zrangebyscore("mykey", "(5", 999, withscores=True)
        self.assertEqual(len(range), 4)
        self.assertEqual(range, expected_data[6:])

        range = redis_c.zrangebyscore("mykey", 5, "(999", withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[5:])

        range = redis_c.zrangebyscore("mykey", "(5", "(999", withscores=True)
        self.assertEqual(len(range), 4)
        self.assertEqual(range, expected_data[6:])

        # Test getting a range where the min is out of bounds
        range = redis_c.zrangebyscore("mykey", -999, 5, withscores=True)
        self.assertEqual(len(range), 6)
        self.assertEqual(range, expected_data[:6])

        range = redis_c.zrangebyscore("mykey", "(-999", 5, withscores=True)
        self.assertEqual(len(range), 6)
        self.assertEqual(range, expected_data[:6])

        range = redis_c.zrangebyscore("mykey", -999, "(5", withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[:5])

        range = redis_c.zrangebyscore("mykey", "(-999", "(5", withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[:5])

        # TODO: test limit with offset and count

    @mock.patch.object(redis.Redis, 'execute_command')
    def test_zrevrangebyscore(self, mock_execute_command):
        mock_execute_command.side_effect = redis_mock.execute_command

        # setup the data
        expected_data = []

        for i in xrange(10):
            self.assertTrue(redis_c.zadd("mykey", "member%s" % i, i))
            expected_data.append(("member%s" % i, i))
        expected_data.reverse()

        # Test getting the whole range
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "+inf", "-inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "+inf", "-inf"), [member for member, score in expected_data])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "inf", "-inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "inf", "-inf"), [member for member, score in expected_data])

        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(+inf", "-inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(+inf", "-inf"), [member for member, score in expected_data])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(inf", "-inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(inf", "-inf"), [member for member, score in expected_data])

        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(+inf", "(-inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(+inf", "(-inf"), [member for member, score in expected_data])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(inf", "(-inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(inf", "(-inf"), [member for member, score in expected_data])

        self.assertEqual(redis_c.zrevrangebyscore("mykey", "+inf", "(-inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "+inf", "(-inf"), [member for member, score in expected_data])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "inf", "(-inf", withscores=True), expected_data)
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "inf", "(-inf"), [member for member, score in expected_data])



        # Test getting invalid or empty ranges
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "-inf", "+inf"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "-inf", "inf"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "inf", "inf"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "-inf", "-inf"), [])

        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(-inf", "+inf"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(-inf", "inf"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(inf", "inf"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(-inf", "-inf"), [])

        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(-inf", "(+inf"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(-inf", "(inf"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(inf", "(inf"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(-inf", "(-inf"), [])

        self.assertEqual(redis_c.zrevrangebyscore("mykey", "-inf", "(+inf"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "-inf", "(inf"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "inf", "(inf"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "-inf", "(-inf"), [])

        self.assertEqual(redis_c.zrevrangebyscore("mykey", 0, "(0"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(0", 0), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", -999, -9999), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", 9999, 999), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", 999, 9999), [])

        self.assertEqual(redis_c.zrevrangebyscore("mykey", -999, "(-9999"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", 9999, "(999"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", 999, "(9999"), [])

        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(-999", "(-9999"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(9999", "(999"), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(999", "(9999"), [])

        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(-999", -9999), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(9999", 999), [])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(999", 9999), [])


        # Test getting a single element via zrevrangebyscore
        self.assertEqual(redis_c.zrevrangebyscore("mykey", 0, 0), ["member0"])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", 0, 0, withscores=True), [("member0", 0)])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", 1, "(0"), ["member1"])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", 0, -10), ["member0"])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(1", 0), ["member0"])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", 0, "(-10"), ["member0"])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "(1", "(-10"), ["member0"])

        # Test parsing of start and end scores
        self.assertEqual(redis_c.zrevrangebyscore("mykey", 0, 0), ["member0"])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", 0, "0"), ["member0"])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "0", 0), ["member0"])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "0", "0"), ["member0"])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", 0, -10), ["member0"])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", 0, "-10"), ["member0"])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "0", -10), ["member0"])
        self.assertEqual(redis_c.zrevrangebyscore("mykey", "0", "-10"), ["member0"])

        # Test getting a range
        range = redis_c.zrevrangebyscore("mykey", 7, 2, withscores=True)
        self.assertEqual(len(range), 6)
        self.assertEqual(range, expected_data[2:8])

        range = redis_c.zrevrangebyscore("mykey", 7, "(2", withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[2:7])

        range = redis_c.zrevrangebyscore("mykey", "(7", 2, withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[3:8])

        range = redis_c.zrevrangebyscore("mykey", "(7", "(2", withscores=True)
        self.assertEqual(len(range), 4)
        self.assertEqual(range, expected_data[3:7])

        # Test getting a range where the max is out of bounds
        range = redis_c.zrevrangebyscore("mykey", 999, 5, withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[:5])

        range = redis_c.zrevrangebyscore("mykey", 999, "(5", withscores=True)
        self.assertEqual(len(range), 4)
        self.assertEqual(range, expected_data[:4])

        range = redis_c.zrevrangebyscore("mykey", "(999", 5, withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[:5])

        range = redis_c.zrevrangebyscore("mykey", "(999", "(5", withscores=True)
        self.assertEqual(len(range), 4)
        self.assertEqual(range, expected_data[:4])

        # Test getting a range where the min is out of bounds
        range = redis_c.zrevrangebyscore("mykey", 5, -999, withscores=True)
        self.assertEqual(len(range), 6)
        self.assertEqual(range, expected_data[4:])

        range = redis_c.zrevrangebyscore("mykey", 5, "(-999", withscores=True)
        self.assertEqual(len(range), 6)
        self.assertEqual(range, expected_data[4:])

        range = redis_c.zrevrangebyscore("mykey", "(5", -999, withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[5:])

        range = redis_c.zrevrangebyscore("mykey", "(5", "(-999", withscores=True)
        self.assertEqual(len(range), 5)
        self.assertEqual(range, expected_data[5:])

        # TODO: test limit with offset and count

    @mock.patch.object(redis.Redis, 'execute_command')
    def test_sadd_and_smembers(self, mock_execute_command):
        mock_execute_command.side_effect = redis_mock.execute_command

        # Test sadd with a single argument
        self.assertEqual(redis_c.sadd("mykey", "member1"), 1)
        self.assertEqual(redis_c.smembers("mykey"), set(["member1"]))

        # Test sadd with multiple arguments
        self.assertEqual(redis_c.sadd("mykey", "member2", "member3", "member4"), 3)
        self.assertEqual(redis_c.smembers("mykey"), set(["member1", "member2", "member3", "member4"]))

    @mock.patch.object(redis.Redis, 'execute_command')
    def test_sismember(self, mock_execute_command):
        mock_execute_command.side_effect = redis_mock.execute_command

        self.assertEqual(redis_c.sadd("mykey", "member1", "member2", "member3", "member4"), 4)
        self.assertTrue(redis_c.sismember("mykey", "member3"))
        self.assertFalse(redis_c.sismember("mykey", "member5"))

    @mock.patch.object(redis.Redis, 'execute_command')
    def test_scard(self, mock_execute_command):
        mock_execute_command.side_effect = redis_mock.execute_command

        self.assertEqual(redis_c.sadd("mykey", "member1", "member2", "member3", "member4"), 4)
        self.assertEqual(redis_c.scard("mykey"), 4)

    @mock.patch.object(redis.Redis, 'execute_command')
    def test_sdiff(self, mock_execute_command):
        mock_execute_command.side_effect = redis_mock.execute_command

        # Test edge cases
        self.assertEqual(redis_c.sdiff("non_existant_key"), set())

        self.assertEqual(redis_c.sadd("mykey1", "member1", "member2", "member3", "member4"), 4)
        # Test empty set (i.e. non-existant set) diff
        self.assertEqual(redis_c.sdiff("non_existant_key", "mykey1"), set())
        # Test diff with empty set
        self.assertEqual(redis_c.sdiff("mykey1", "non_existant_key"), redis_c.smembers("mykey1"))

        self.assertEqual(redis_c.sadd("mykey2", "member3", "member4", "member5", "member6"), 4)
        # Test normal diff with the 2nd set containing elements not in the 1st set
        self.assertEqual(redis_c.sdiff("mykey1", "mykey2"), set(["member1", "member2"]))

        self.assertEqual(redis_c.sadd("mykey3", "member3", "member4"), 2)
        # Test normal diff with the 2nd set not containing any extra elements
        self.assertEqual(redis_c.sdiff("mykey1", "mykey3"), set(["member1", "member2"]))
        # Test multiple diff with overlapping key ranges
        self.assertEqual(redis_c.sdiff("mykey1", "mykey2", "mykey3"), set(["member1", "member2"]))

        self.assertEqual(redis_c.sadd("mykey4", "member5", "member6"), 2)
        # Test diff with the 2nd set only containing elements not in the 1st set
        self.assertEqual(redis_c.sdiff("mykey1", "mykey4"), redis_c.smembers("mykey1"))
        # Test diff with multiple sets having overlapping key ranges
        self.assertEqual(redis_c.sdiff("mykey1", "mykey2", "mykey3", "mykey4"), set(["member1", "member2"]))

        self.assertEqual(redis_c.sadd("mykey5", "member1", "member2"), 2)
        # Test diff where other sets make the 1st one empty
        self.assertEqual(redis_c.sdiff("mykey1", "mykey3", "mykey5"), set())
        # Test diff where other sets make the 1st one empty and the other sets contain extra elements
        self.assertEqual(redis_c.sdiff("mykey1", "mykey2", "mykey3", "mykey4", "mykey5"), set())

        self.assertEqual(redis_c.sadd("mykey6", "member1", "member2", "member3", "member4"), 4)
        # Test diff where the 2nd set contains all of the elements in the first set
        self.assertEqual(redis_c.sdiff("mykey1", "mykey6"), set())

        self.assertEqual(redis_c.sadd("mykey7", "member1", "member2", "member3", "member4", "member5"), 5)
        # Test diff where the 2nd set contains all of the elements in the first set and some extra elements
        self.assertEqual(redis_c.sdiff("mykey1", "mykey7"), set())

if __name__ == "__main__":
    unittest.main()
