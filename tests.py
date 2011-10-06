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



if __name__ == "__main__":
    unittest.main()
