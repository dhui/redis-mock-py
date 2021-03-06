"""
A mock for Redis.
This mock only works with the redis-py library.

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


"""

import types

ScoreTypes = (types.IntType, types.LongType, types.FloatType)


class RedisSortedSetMock:
    """
    Mocks Redis Sorted Sets
    """

    def __init__(self):
        self.dict = {}

    def add(self, *args):
        """
        Performs the same functionality as ZADD
        """
        if len(args) < 2:
            raise Exception("You need to specify member and score when adding to a Redis sorted set. args: %s" % args)

        ret = []
        # go through the arguments 2 at a time
        for score, member in zip(args[0::2], args[1::2]):
            if not isinstance(member, types.StringTypes):
                raise Exception("Redis sorted set member must be a string")
            if not isinstance(score, ScoreTypes):
                raise Exception("Redis sorted set score must be an integer or float")
            local_ret = True
            if member in self.dict:
                local_ret = False
            self.dict[member] = score
            ret.append(local_ret)

        # special case: if there is only element added
        if len(ret) == 1:
            ret = ret[0]
        return ret

    def __get_sorted_by_score(self, reverse=False):
        """
        Helper function to sort the internal dictionary by the score
        """
        all_items = [(key, float(value)) for key, value in self.dict.iteritems()]
        all_items.sort(key=lambda x: x[1], reverse=reverse)  # sort by score
        return all_items

    def range(self, start, end, withscores=False, reverse=False):
        """
        Performs the same functionality as ZRANGE and ZREVRANGE
        """
        # The way Redis sorted sets range works is slightly different for slices so it's not a direct translation.
        all_items = self.__get_sorted_by_score(reverse=reverse)
        if start >= 0 and end >= 0:
            end += 1
            all_items = all_items[start:end]
        if start < 0 and end < 0:
            # both negative
            range_size = end - start
            if range_size < 0:
                return []  # end is greater than start, so this is not valid
            if abs(start) >= len(all_items):
                return []  # the start is too negative
            all_items = all_items[start:][:range_size + 1]
        if start < 0 and end >= 0:
            return []  # Redis doesn't return anything for this
        if start >= 0 and end < 0:
            end = len(all_items) + end + 1 # calculate the new end index
            if end <= start:
                return []
            all_items = all_items[start:end]

        if withscores:
            return all_items
        return [member for member, score in all_items]

    def rangebyscore(self, min, max, withscores=False, offset=None, count=None, reverse=False):
        """
        Performs the same functionality as ZRANGEBYSCORE and ZREVRANGEBYSCORE
        """
        min_inclusive = True
        max_inclusive = True
        if isinstance(min, types.StringTypes):
            parse_str = min
            if min[0] == '(':
                parse_str = min[1:]
                min_inclusive = False
            min_value = float(parse_str)
        elif isinstance(min, ScoreTypes):
            min_value = float(min)
        else:
            raise Exception("min in Redis sorted set rangebyscore must be a string, integer, or float")
        if isinstance(max, types.StringTypes):
            parse_str = max
            if max[0] == '(':
                parse_str = max[1:]
                max_inclusive = False
            max_value = float(parse_str)
        elif isinstance(max, ScoreTypes):
            max_value = float(max)
        else:
            raise Exception("max in Redis sorted set rangebyscore must be a string, integer, or float")

        if min_value > max_value:
            return []

        all_items = self.__get_sorted_by_score(reverse=reverse)
        if min_inclusive:
            all_items = filter(lambda x: x[1] >= min_value, all_items)
        else:
            all_items = filter(lambda x: x[1] > min_value, all_items)
        if max_inclusive:
            all_items = filter(lambda x: x[1] <= max_value, all_items)
        else:
            all_items = filter(lambda x: x[1] < max_value, all_items)

        if offset is not None and count is not None:
            all_items = all_items[offset:count+offset]

        if withscores:
            return all_items
        return [member for member, score in all_items]

    def __repr__(self):
        """
        Overwritten so you can print the sorted set
        """
        return str(self.dict)


class RedisMock:
    db = {}


def flush_db():
    """
    Helper function to flush the RedisMock db between test runs
    """
    RedisMock.db = {}


def print_db():
    """
    Helper function to print the RedisMock db. Used for debugging purposes.
    """
    print RedisMock.db


def __parse_range_command(*args, **options):
    """
    Internal helper function to parse the arguments out of a RANGE type command
    """
    key = str(args[1])
    start = args[2]
    stop = args[3]
    withscores = False
    if 'withscores' in options:
        withscores = options['withscores']
    return (key, start, stop, withscores)


def execute_command(*args, **options):
    """
    Function used to overrite the Redis execute_command function so we can mock redis
    """
    command = args[0]
    # Redis Sorted Set commands
    if command == "ZADD":
        key = str(args[1])
        if key not in RedisMock.db:
            RedisMock.db[key] = RedisSortedSetMock()
            return RedisMock.db[key].add(*args[2:])
        else:
            sorted_set = RedisMock.db[key]
            if not isinstance(sorted_set, RedisSortedSetMock):
                raise Exception("Calling ZADD on key %s should be of type sorted set. current type: %s" % (key, type(sorted_set)))
            return sorted_set.add(*args[2:])
    elif command == "ZRANGE":
        key, start, stop, withscores = __parse_range_command(*args, **options)
        if key not in RedisMock.db:
            return []
        else:
            return RedisMock.db[key].range(start, stop, withscores)
    elif command == "ZREVRANGE":
        key, start, stop, withscores = __parse_range_command(*args, **options)
        if key not in RedisMock.db:
            return []
        else:
            return RedisMock.db[key].range(start, stop, withscores, reverse=True)
    elif command == "ZRANGEBYSCORE":
        key, min, max, withscores = __parse_range_command(*args, **options)
        offset = None
        count = None
        if len(args) == 6:
            offset = args[4]
            count = args[5]
        if key not in RedisMock.db:
            return []
        else:
            return RedisMock.db[key].rangebyscore(min, max, withscores, offset, count)
    elif command == "ZREVRANGEBYSCORE":
        # the ordering for min and max are flipped for ZREVRANGEBYSCORE
        key, max, min, withscores = __parse_range_command(*args, **options)
        offset = None
        count = None
        if len(args) == 6:
            offset = args[4]
            count = args[5]
        if key not in RedisMock.db:
            return []
        else:
            return RedisMock.db[key].rangebyscore(min, max, withscores, offset, count, reverse=True)
    # Redis Set commands
    elif command == "SADD":
        key = str(args[1])
        members = [str(member) for member in args[2:]]
        if key not in RedisMock.db:
            RedisMock.db[key] = set(members)
            return len(members)
        else:
            current_set = RedisMock.db[key]
            if not isinstance(current_set, set):
                raise Exception("Calling SADD on key %s should be of type set. current type: %s" % (key, type(current_set)))
            num_added = 0
            for member in members:
                if member in current_set:
                    continue
                current_set.add(member)
                num_added += 1
            return num_added
    elif command == "SISMEMBER":
        key = str(args[1])
        member = str(args[2])
        if key not in RedisMock.db:
            return False
        else:
            current_set = RedisMock.db[key]
            if not isinstance(current_set, set):
                raise Exception("Calling SISMEMBER on key %s should be of type set. current type: %s" % (key, type(current_set)))
            return member in current_set
    elif command == "SMEMBERS":
        key = str(args[1])
        if key not in RedisMock.db:
            return set()
        else:
            current_set = RedisMock.db[key]
            if not isinstance(current_set, set):
                raise Exception("Calling SMEMBERS on key %s should be of type set. current type: %s" % (key, type(current_set)))
            return current_set
    elif command == "SCARD":
        key = str(args[1])
        if key not in RedisMock.db:
            return 0
        else:
            current_set = RedisMock.db[key]
            if not isinstance(current_set, set):
                raise Exception("Calling SCARD on key %s should be of type set. current type: %s" % (key, type(current_set)))
            return len(current_set)
    elif command == "SDIFF":
        key = str(args[1])
        keys = []
        if len(args) > 2:
            keys = [str(arg) for arg in args[2:]]
        # Redis loads all of the sets before returning
        current_set = set()
        try:
            current_set = RedisMock.db[key]
        except KeyError:
            pass
        if not isinstance(current_set, set):
            raise Exception("Calling SDIFF on key %s should be of type set. current type: %s" % (key, type(current_set)))
        # accumulate the sets that we'll be diffing with
        accumulator_set = set()
        for key in keys:
            try:
                next_set = RedisMock.db[key]
                if not isinstance(next_set, set):
                    raise Exception("Calling SDIFF on key %s should be of type set. current type: %s" % (key, type(next_set)))
                accumulator_set.update(next_set)
            except KeyError:
                pass
        return current_set - accumulator_set
    raise Exception("Unimplemented Redis command: %s" % command)
