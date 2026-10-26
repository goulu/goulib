"""
useful decorators
"""
__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2015, Philippe Guglielmetti"
__credits__ = ["http://include.aorcsik.com/2014/05/28/timeout-decorator/"]
__license__ = "LGPL + MIT"

import multiprocessing
from multiprocessing import TimeoutError
from threading import Timer
import weakref
import threading
import _thread as thread
from multiprocessing.pool import ThreadPool
import logging
import functools
import sys
import logging

_gettrace = getattr(sys, 'gettrace', None)
debugger = _gettrace and _gettrace()
logging.info('debugger ' + ('ACTIVE' if debugger else 'INACTIVE'))


# http://wiki.python.org/moin/PythonDecoratorLibrary
def memoize(obj):
    """speed up repeated calls to a function by caching its results in a dict index by params
    :see: https://en.wikipedia.org/wiki/Memoization
    """
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
        
    return memoizer


def debug(func):
    # Customize these messages
    ENTRY_MESSAGE = 'Entering {}'
    EXIT_MESSAGE = 'Exiting {}'

    @functools.wraps(func)
    def wrapper(*args, **kwds):
        logger = logging.getLogger()
        logger.info(ENTRY_MESSAGE.format(func.__name__))
        level = logger.getEffectiveLevel()
        logger.setLevel(logging.DEBUG)
        f_result = func(*args, **kwds)
        logger.setLevel(level)
        logger.info(EXIT_MESSAGE.format(func.__name__))
        return f_result

    return wrapper


def nodebug(func):

    @functools.wraps(func)
    def wrapper(*args, **kwds):
        logger = logging.getLogger()
        level = logger.getEffectiveLevel()
        logger.setLevel(logging.INFO)
        f_result = func(*args, **kwds)
        logger.setLevel(level)
        return f_result

    return wrapper


# https://medium.com/pythonhive/python-decorator-to-measure-the-execution-time-of-methods-fa04cb6bb36d
def timeit(method):
    import time
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        logging.info('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result

    return timed

# http://include.aorcsik.com/2014/05/28/timeout-decorator/
# BUT read http://eli.thegreenplace.net/2011/08/22/how-not-to-set-a-timeout-on-a-computation-in-python


thread_pool = None


def get_thread_pool():
    global thread_pool
    if thread_pool is None:
        # fix for python <2.7.2
        if not hasattr(threading.current_thread(), "_children"):
            threading.current_thread()._children = weakref.WeakKeyDictionary()
        thread_pool = ThreadPool(processes=1)
    return thread_pool


def timeout(timeout):

    def wrap_function(func):
        if not timeout:
            return func

        @functools.wraps(func)
        def __wrapper(*args, **kwargs):
            try:
                async_result = get_thread_pool().apply_async(func, args=args, kwds=kwargs)
                return async_result.get(timeout)
            except thread.error:
                return func(*args, **kwargs)

        return __wrapper

    return wrap_function

# https://gist.github.com/goulu/45329ef041a368a663e5


def itimeout(iterable, timeout):
    """timeout for loops
    :param iterable: any iterable
    :param timeout: float max running time in seconds 
    :yield: items in iterator until timeout occurs
    :raise: multiprocessing.TimeoutError if timeout occured
    """
    if False:  # handle debugger better one day ...
        n = 100 * timeout
        for i, x in enumerate(iterable):
            yield x
            if i > n:
                break
    else:
        timer = Timer(timeout, lambda: None)
        timer.start()
        for x in iterable:
            yield x
            if timer.finished.is_set():
                raise TimeoutError
        # don't forget it, otherwise the thread never finishes...
        timer.cancel()

# https://www.artima.com/weblogs/viewpost.jsp?thread=101605


registry = {}


class MultiMethod(object):

    def __init__(self, name):
        self.name = name
        self.typemap = {}

    def __call__(self, *args):
        types = tuple(arg.__class__ for arg in args)  # a generator expression!
        function = self.typemap.get(types)
        if function is None:
            raise TypeError("no match")
        return function(*args)

    def register(self, types, function):
        if types in self.typemap:
            raise TypeError("duplicate registration")
        self.typemap[types] = function


def multimethod(*types):
    """
    Allows to overload functions for various parameter types::

        @multimethod(int, int)
        def foo(a, b):
            pass  # code for two ints

        @multimethod(float, float)
        def foo(a, b):
            pass  # code for two floats

        @multimethod(str, str)
        def foo(a, b):
            pass  # code for two strings
    """

    def register(function):
        name = function.__name__
        mm = registry.get(name)
        if mm is None:
            mm = registry[name] = MultiMethod(name)
        mm.register(types, function)
        return mm

    return register
