"""
operations on [a..b[ intervals
"""
__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2012, Philippe Guglielmetti"
__credits__ = []
__license__ = "LGPL"

from sortedcontainers import SortedListWithKey


def _order(interval):
    """:return: (a,b) interval such that a<=b"""
    if interval[0] == interval[1]:  # allows to order None,None in Py3
        return (interval[0], interval[1])
    elif interval[0] < interval[1]:
        return (interval[0], interval[1])
    else:
        return (interval[1], interval[0])


def in_interval(interval, x, closed=True):
    """:return: bool True if x is in interval [a,b] or [b,a] (tuple)"""
    a, b = _order(interval)
    return (a <= x <= b) if closed else (a <= x < b)


def intersect(t1, t2):
    """:return: bool True if intervals [t1[ [t2[ intersect"""
    '''http://stackoverflow.com/questions/3721249/python-date-interval-intersection'''
    t1start, t1end = _order(t1)
    t2start, t2end = _order(t2)
    return (t1start <= t2start < t1end) or (t2start <= t1start < t2end)


def intersection(t1, t2):
    """
    :return: tuple intersection between 2 intervals (tuples), 
        or None if intervals don't intersect
    """
    t1start, t1end = _order(t1)
    t2start, t2end = _order(t2)
    start = max(t1start, t2start)
    end = min(t1end, t2end)
    if start > end:  # no intersection
        return None
    return (start, end)


def intersectlen(t1, t2, none=0):
    """
    :param t1: interval 1 (tuple)
    :param t2: interval 2 (tuple)
    :param none: value to return when t1 does not intersect t2
    :return: len of intersection between 2 intervals (tuples), 
        or none if intervals don't intersect
    """
    i = intersection(t1, t2)
    if i is None:
        return none  # the parameter...
    return i[1]-i[0]


class Interval(list):
    """
    Represents an interval. 
    Defined as half-open interval [start,end), 
    which includes the start position but not the end.
    Start and end do not have to be numeric types. 
    They might especially be time, date or timedate as used in datetime2

    inspired from http://code.activestate.com/recipes/576816-interval/
    alternatives could be https://pypi.python.org/pypi/interval/
    (outdated, no more doc)
    or https://pypi.python.org/pypi/pyinterval/
    """

    def __init__(self, start, end):
        """Construct, start must be <= end."""
        self[0:1] = _order((start, end))

    start = property(fget=lambda self: self[0], doc="The interval's start")
    end = property(fget=lambda self: self[1], doc="The interval's end")

    def __str__(self):
        return '[%s,%s)' % (self.start, self.end)

    def __repr__(self):
        return '[%s,%s)' % (self.start, self.end)

    def __hash__(self):
        return hash(self.start) ^ hash(self.end)

    def __lt__(self, other):
        return self.end < other.start  # it has to be < even if ==

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

    @property
    def size(self):
        return self.end-self.start

    @property
    def center(self):
        return (self.end+self.start)/2

    def _combine(self, other):
        """used in several methods below"""
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        return start, end

    def separation(self, other):
        """:return: distance between self and other, negative if overlap"""
        start, end = self._combine(other)
        return start-end  # yes, in this order ...

    def overlap(self, other, allow_contiguous=False):
        """:return: True iff self intersects other."""
        d = self.separation(other)
        zero = type(d)()
        if allow_contiguous and d == zero:
            return True
        else:
            return d < zero

    def intersection(self, other):
        """:return: Intersection with other, or None if no intersection."""
        start, end = self._combine(other)
        if start > end:  # no intersection
            return None
        return Interval(start, end)

    def __iadd__(self, other):
        """expands self to contain other."""
        if isinstance(other, Interval):
            s, e = other.start, other.end
        else:
            s, e = other, other
        self[0] = s if self.start is None else min(self.start, s)
        self[1] = e if self.end is None else max(self.end, e)
        return self

    def hull(self, other):
        """:return: new Interval containing both self and other."""
        res = Interval(self.start, self.end)
        res += other
        return res

    def __add__(self, other):
        if self.overlap(other, True):
            return self.hull(other)
        else:
            return Intervals([self, other])

    def __contains__(self, x):
        """:return: True if x in self."""
        if isinstance(x, Interval):
            return self.start <= x.start and x.end < self.end
        else:
            return self.start <= x and x < self.end

    def subset(self, other):
        ":return: True iff self is subset of other."
        return self.start >= other.start and self.end <= other.end

    def proper_subset(self, other):
        ":return: True iff self is proper subset of other."
        return self.start > other.start and self.end < other.end

    def empty(self):
        ":return: True iff self is empty."
        return self.start == self.end

    def __nonzero__(self):
        return not self.empty()

    def singleton(self):
        ":return: True iff self.end - self.start == 1."
        return self.size == 1


class Intervals(SortedListWithKey):
    """a list of intervals kept in ascending order"""

    def update(self, iterable):
        """Update the list by adding all elements from *iterable*."""
        # overload needed because SortedListWithKey doesn't call add/insert
        for item in iterable:
            self.add(item)

    _update = update  # defined and used in SortedListWithKey.__init__

    def add(self, item):
        k = self._key(item)
        # item starts before self[i], but overlaps maybe with i, i+1, ... th intervals
        i = self.bisect_left(k)
        if i < len(self) and self[i].overlap(item, True):
            item = self.pop(i).hull(item)
            return self.add(item)

        super(Intervals, self).add(item)
        return self

    def insert(self, item):
        raise DeprecationWarning('use add method instead')

    def __iadd__(self, item):
        return self.add(item)

    def __add__(self, item):
        return Intervals(self).add(item)

    def __call__(self, x):
        """ returns intervals containing x"""
        for interval in self:
            if x in interval:
                return interval
        return None

    def __str__(self):
        """ string representation : like a list of Intervals"""
        return str([x for x in self])


class Box(list):
    """a N dimensional rectangular box defined by a list of N Intervals"""

    def __init__(self, *args):
        if len(args) == 1 and type(args[0]) is int:
            super(Box, self).__init__(
                [Interval(None, None) for _ in range(args[0])])
            return
        if isinstance(args[0], Interval):  # works also as copy constructor
            super(Box, self).__init__(args)
        else:  # consider data as points in the box (as in a bounding box)
            super(Box, self).__init__([Interval(None, None) for _ in args[0]])
            for pt in args:
                self += pt

    def corner(self, n):
        """return n-th corner of box
        0-th corner is "start" made of all minimal values of intervals
        -1.th corner is "end", made of all maximal values of intervals
        """
        return tuple(inter.end if n & (1 << i) else inter.start for i, inter in enumerate(self))

    @property
    def start(self):
        return tuple(i.start for i in self)

    @property
    def end(self):
        return tuple(i.end for i in self)

    min, max = start, end  # alias

    @property
    def size(self):
        return tuple(i.size for i in self)

    @property
    def center(self):
        return tuple(i.center for i in self)

    def __call__(self):
        """:return: tuple of all intervals as tuples"""
        return tuple(i() for i in self)

    def __iadd__(self, other):
        """
        enlarge box if required to contain specified point
        :param other: :class:`Box` or (list of) N-tuple point(s)
        """
        for interval, x in zip(self, other):
            interval += x
        return self

    def __add__(self, other):
        """
        enlarge box if required to contain specified point
        :param other: :class:`Box` or (list of) N-tuple point(s)
        :return: new Box containing both
        """
        res = Box(self)
        res += other
        return res

    def __contains__(self, other):
        """:return: True if x in self."""
        return all(x in i for i, x in zip(self, other))

    def __nonzero__(self):
        return any(self)

    def empty(self):
        ":return: True iff Box is empty."
        return not self
