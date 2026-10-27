import time
import pytest
from goulib.tests import *
from goulib.decorators import *


class TestMemoize:
    def test_memoize(self):
        calls = 0

        @memoize
        def square(x):
            nonlocal calls
            calls += 1
            return x * x

        assert square(4) == 16
        assert calls == 1
        assert square(4) == 16
        assert calls == 1
        assert square(5) == 25
        assert calls == 2


class TestDebug:
    def test_debug(self):
        @debug
        def add(a, b):
            return a + b

        assert add(2, 3) == 5


class TestNodebug:
    def test_nodebug(self):
        @nodebug
        def sub(a, b):
            return a - b

        assert sub(5, 2) == 3


class TestTimeit:
    def test_timeit(self):
        @timeit
        def slow():
            time.sleep(0.01)
            return "done"

        assert slow() == "done"


class TestGetThreadPool:
    def test_get_thread_pool(self):
        pool = get_thread_pool()
        assert pool is not None
        assert pool is get_thread_pool()


class TestTimeout:
    def test_timeout(self):
        @timeout(0)
        def no_timeout(x):
            return x * 2

        assert no_timeout(5) == 10

        @timeout(1.0)
        def fast(x):
            return x + 1

        assert fast(3) == 4

        @timeout(0.05)
        def slow():
            time.sleep(0.5)
            return "too slow"

        with pytest.raises(TimeoutError):
            slow()


class TestItimeout:
    def test_itimeout(self):
        # finishes before timeout
        res = list(itimeout(range(5), 1.0))
        assert res == [0, 1, 2, 3, 4]

        # timeouts during iteration
        def infinite_gen():
            while True:
                time.sleep(0.02)
                yield 1

        with pytest.raises(TimeoutError):
            list(itimeout(infinite_gen(), 0.05))


class TestMultiMethod:
    def test_multimethod(self):
        @multimethod(int, int)
        def add_types(a, b):
            return "int"

        @multimethod(str, str)
        def add_types(a, b):
            return "str"

        assert add_types(1, 2) == "int"
        assert add_types("a", "b") == "str"

        with pytest.raises(TypeError):
            add_types(1, "a")

        with pytest.raises(TypeError):
            @multimethod(int, int)
            def add_types(a, b):
                return "duplicate"
