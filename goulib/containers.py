"""
advanced containers : 
- Record (struct) 
- INFINITE Sequence
- SortedCollection
"""
__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2015, Philippe Guglielmetti"
__credits__ = []
__license__ = "LGPL"

from bisect import bisect_left, bisect_right
from collections import OrderedDict
import operator
from itertools import count, tee, islice, chain

from . import itertools2, decorators, tests


class Record(OrderedDict):
    """mimics a Pascal record or a C struct"""

    # https://stackoverflow.com/a/5491708/1395973
    def __init__(self, *args, **kwargs):
        super(Record, self).__init__(*args, **kwargs)
        self._initialized = True

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if not name:
            return
        if '_initialized' in self.__dict__:
            super(Record, self).__setitem__(name, value)
        else:
            super(Record, self).__setattr__(name, value)

    def __repr__(self):
        res = ['%s:%s' % (k, self[k]) for k in self]
        return '{{%s}}' % (','.join(res))


class Sequence(object):
    """Container representing a finite or infinite numeric sequence.

    Inspired by the On-Line Encyclopedia of Integer Sequences (OEIS),
    ``Sequence`` unifies three complementary programming concepts into a single
    transparent object:

    1. **Generator / Iterable**: ``for x in seq: ...`` iterates through the terms
       sequentially (potentially indefinitely).
    2. **Indexable sequence**: ``seq[i]`` accesses the *i*-th element directly,
       and slicing ``seq[start:stop:step]`` returns an iterator over the requested range.
    3. **Set / Membership container**: ``x in seq`` tests whether an integer belongs
       to the sequence.

    Any combination of ``iterf``, ``itemf``, and ``containf`` can be provided to
    the constructor. When multiple functions are available, ``Sequence`` leverages
    the most efficient one for each operation:

    * If ``itemf`` is given, ``seq[i]`` runs in :math:`O(1)` or without iterating from 0.
    * If ``containf`` is given, ``x in seq`` performs a fast direct membership check.
    * If ``iterf`` is given, iteration is generated sequentially via the iterator.

    Computations are fully **lazy**: transformations (filtering, mapping, arithmetic,
    set combinations) build new ``Sequence`` instances without immediate evaluation.
    Terms are only computed when consumed.

    Examples:
        Defining the prime numbers (OEIS `A000040 <https://oeis.org/A000040>`_)
        using only a primality test:

        >>> from goulib.containers import Sequence
        >>> from goulib import math2
        >>> primes = Sequence(containf=math2.is_prime, desc="Prime numbers")
        >>> 201420142013 in primes
        True
        >>> primes.index(7)
        3

        Defining the Fibonacci numbers (OEIS `A000045 <https://oeis.org/A000045>`_)
        with optimal algorithms for generation, direct indexing, and membership:

        >>> fib = Sequence(
        ...     iterf=math2.fibonacci_gen,
        ...     itemf=math2.fibonacci,
        ...     containf=math2.is_fibonacci,
        ...     desc="Fibonacci numbers"
        ... )
        >>> fib[10]
        55
        >>> [fib[i] for i in range(7)]
        [0, 1, 1, 2, 3, 5, 8]

        Deriving new sequences using arithmetic and higher-order methods:

        >>> import operator
        >>> # Differences between consecutive primes / prime gaps (OEIS A001223):
        >>> prime_gaps = primes.pairwise(operator.sub)

        >>> # Fermat numbers 2^(2^n) + 1 (OEIS A000215) by adding scalar 1:
        >>> # fermat = Sequence(itemf=lambda n: 2**(2**n)) + 1

        >>> # Filter primes to Mersenne exponents (OEIS A000043):
        >>> # mersenne_exp = primes.filter(math2.lucas_lehmer)

        >>> # Set operations between sequences:
        >>> # single_primes = primes % twin_primes  # terms in primes not in twin_primes
        >>> # binary_primes = A007088 & primes      # primes written with 0 and 1 only
        >>> # merged = seq1 | seq2                 # union of sorted sequences

    See also:
        `Suites infinies et OEIS en Python (Dr. Goulu) <https://drgoulu.com/2017/06/26/series-infinies-et-oeis-en-python/>`_
    """

    def __init__(self, iterf=None, itemf=None, containf=None, desc='', timeout=0):
        """Initialize a numeric Sequence.

        :param iterf: Optional iterator, callable returning an iterator, or int offset.
            Generates the sequence terms sequentially. If an integer is supplied,
            it specifies the starting offset for a counting sequence.
        :param itemf: Optional callable ``itemf(i)`` returning the *i*-th element.
            Enables direct :math:`O(1)` or fast indexing.
        :param containf: Optional callable ``containf(n)`` returning ``True`` if *n*
            belongs to the sequence. Enables fast membership testing (``n in self``).
        :param desc: String description of the sequence. If omitted and ``itemf``
            is provided, defaults to ``itemf.__doc__``.
        :param timeout: Optional float maximum computation time in seconds allowed
            when iterating through terms. A :exc:`~goulib.decorators.TimeoutError`
            is raised if exceeded.
        """
        self.name = self.__class__.__name__  # by default

        if isinstance(iterf, int):
            self.offset = iterf
            self.iterf = None
        else:
            try:
                iterf = iterf()
            except TypeError as e:
                pass
            self.offset = 0
            self.iterf = iterf
        self.itemf = itemf
        if itemf and not desc:
            desc = itemf.__doc__
        self.containf = containf

        self.desc = desc
        self.timeout = timeout
        self._repr = ''

    def __repr__(self):
        """Return a string representation showing the first computed terms.

        Evaluates up to the first 10 terms within a 1-second timeout using
        :func:`goulib.tests.pprint` to avoid blocking debuggers or interactive shells.
        """
        if not self._repr:  # cache for speed
            # must be very quick for debugger
            s = tests.pprint(self, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 1)
            self._repr = '%s = (%s)' % (self.name, s)
        return self._repr

    def save(self, filename, comment=None, n=1000, maxtime=60):
        """Save the first *n* terms of the sequence to a text file.

        Exports lines formatted as ``index value``, compatible with OEIS b-file format.

        :param filename: Path to the output text file.
        :param comment: Optional header comment line. Defaults to sequence description
            and current date.
        :param n: Maximum number of terms to export (default: 1000).
        :param maxtime: Maximum time allowed in seconds for generating the terms.
        """
        with open(filename, 'wt') as f:
            from datetime import date
            comment = comment or "%s %s" % (self.desc, date.today())
            print('#' + comment, file=f)
            for i, v in enumerate(self):
                if i > n:
                    break
                print(i + self.offset, v, file=f)

    def __iter__(self):
        """Return an independent generator iterating from the beginning of the sequence.

        If ``iterf`` is provided, it is duplicated using :func:`itertools.tee`.
        Otherwise, an iterator is constructed from ``itemf`` or by filtering
        integers using ``containf``. Iteration can be optionally protected by ``timeout``.

        :return: Generator yielding sequence elements.
        """
        if self.iterf:
            self.iterf, res = tee(self.iterf)
            if self.timeout:
                res = decorators.itimeout(res, self.timeout)
        else:
            it = count(self.offset)
            if self.timeout:
                it = decorators.itimeout(it, self.timeout)
            if self.itemf:
                res = map(lambda i: self[i], it)
            else:
                res = filter(lambda n: n in self, it)  # uses containf
        return res

    def __getitem__(self, i):
        """Get the *i*-th element or a slice of the sequence.

        :param i: Zero-based integer index or :class:`slice` object.
        :return: The *i*-th value if *i* is an integer, or an :func:`itertools.islice`
            iterator if *i* is a slice.
        """
        if not isinstance(i, slice):
            if self.itemf:
                return self.itemf(i)
            else:
                return itertools2.index(i, self)
        else:
            return islice(self, i.start, i.stop, i.step)

    def index(self, v):
        """Find the index of value *v* in a strictly growing sequence.

        Scans the sequence sequentially. As the sequence is assumed to be monotonically
        increasing, searching stops as soon as a term exceeds *v*.

        :param v: Value to locate.
        :return: Integer index of *v*, or -1 if *v* is not in the sequence.
        """
        # assume sequence is growing
        for i, n in enumerate(self):
            if v == n:
                return i
            if n > v:
                return -1

    def __contains__(self, n):
        """Test whether *n* belongs to the sequence.

        Uses ``containf(n)`` if defined; otherwise falls back to ``self.index(n) >= 0``.

        :param n: Value to test.
        :return: ``True`` if *n* is in the sequence, ``False`` otherwise.
        """
        if self.containf:
            return self.containf(n)
        else:
            return self.index(n) >= 0

    def __add__(self, other):
        """Add a scalar integer or another Sequence element-wise.

        If *other* is an integer :math:`k`, translates the sequence by :math:`k`:
        each term :math:`a_n` becomes :math:`a_n + k`.
        If *other* is another Sequence, returns a new Sequence yielding :math:`a_n + b_n`.

        :param other: Integer scalar or :class:`Sequence`.
        :return: New :class:`Sequence`.
        """
        if type(other) is int:
            return self.apply(
                lambda n: n + other,
                containf=lambda n: n - other in self,
                desc='%s+%d' % (self.name, other)
            )

        def _():
            for (a, b) in zip(self, other):
                yield a + b

        return Sequence(_, lambda i: self[i] + other[i])

    def __sub__(self, other):
        """Subtract a scalar integer or another Sequence element-wise.

        If *other* is an integer :math:`k`, translates the sequence by :math:`-k`:
        each term :math:`a_n` becomes :math:`a_n - k`.
        If *other* is another Sequence, returns a new Sequence yielding :math:`a_n - b_n`.

        :param other: Integer scalar or :class:`Sequence`.
        :return: New :class:`Sequence`.
        """
        if type(other) is int:
            return self + (-other)

        def _():
            for (a, b) in zip(self, other):
                yield a - b

        return Sequence(_, lambda i: self[i] - other[i])

    def __mul__(self, other):
        """Multiply by a scalar integer or another Sequence element-wise.

        :param other: Integer scalar or :class:`Sequence`.
        :return: New :class:`Sequence`.
        """
        if type(other) is int:
            return self.apply(
                lambda n: n * other,
                containf=lambda n: other / n in self,
                desc='%d*%s' % (other, self.name)
            )

        def _():
            for (a, b) in zip(self, other):
                yield a * b

        return Sequence(_, lambda i: self[i] * other[i])

    def __div__(self, other):
        """Perform integer division by a scalar or another Sequence element-wise.

        :param other: Integer scalar or :class:`Sequence`.
        :return: New :class:`Sequence`.
        """
        if type(other) is int:
            return self.apply(
                lambda n: n // other,
                containf=lambda n: other * n in self,
                desc='%s//%d' % (self.name, other)
            )

        def _():
            for (a, b) in zip(self, other):
                yield a // b

        return Sequence(_, lambda i: self[i] // other[i])

    def __truediv__(self, other):
        """Perform division by a scalar or another Sequence element-wise (using Fractions).

        :param other: Integer scalar or :class:`Sequence`.
        :return: New :class:`Sequence`.
        """
        if type(other) is int:
            return self.apply(
                lambda n: n / other,
                containf=lambda n: other * n in self,
                desc='%s/%d' % (self.name, other)
            )

        def _():
            from fractions import Fraction
            for (a, b) in zip(self, other):
                yield Fraction(a, b)

        return Sequence(_, lambda i: self[i] / other[i])

    def __or__(self, other):
        """Return the union of two sorted sequences without duplicates.

        Merges two monotonically increasing sequences using :func:`heapq.merge`
        and removes duplicates with :func:`~goulib.itertools2.unique`.

        Example:
            Numbers with 4 divisors (OEIS `A030513 <https://oeis.org/A030513>`_)
            as the union of semiprimes (product of two distinct primes) and
            cubes of primes:

            >>> # A030513 = prime_cubes | semiprimes

        :param other: Monotonically increasing :class:`Sequence`.
        :return: Merged :class:`Sequence`.
        """
        return Sequence(
            itertools2.unique(itertools2.merge(self, other)),
            None,
            lambda x: x in self or x in other
        )

    def __and__(self, other):
        """Return the intersection of two sequences.

        Filters the left sequence using the membership predicate of the right sequence
        (or vice versa).

        Example:
            Primes with digits 0 and 1 only (OEIS `A020449 <https://oeis.org/A020449>`_):

            >>> # A020449 = binary_numbers & primes

        :param other: :class:`Sequence` with a defined ``containf``.
        :return: Filtered :class:`Sequence` containing items common to both operands.
        """
        if other.containf:
            return self.filter(other.containf)
        if self.containf:
            return other.filter(self.containf)
        raise (NotImplementedError)

    def __mod__(self, other):
        """Return the set difference (self \\\\ other) of two sorted sequences.

        Yields terms from *self* that are not present in *other*.

        Example:
            Isolated primes (OEIS `A007510 <https://oeis.org/A007510>`_),
            i.e. primes that are not twin primes:

            >>> # A007510 = primes % twin_primes

        :param other: Monotonically increasing :class:`Sequence`.
        :return: Difference :class:`Sequence`.
        """
        return Sequence(
            itertools2.diff(self.__iter__(), other.__iter__()), None,
            lambda x: x in self and x not in other
        )

    def apply(self, f, containf=None, desc=''):
        """Apply a function to each term of the sequence (function composition).

        Example:
            Squares of primes (OEIS `A001248 <https://oeis.org/A001248>`_):

            >>> # A001248 = primes.apply(lambda n: n * n)

        :param f: Callable to map over every element.
        :param containf: Optional membership predicate for the resulting sequence.
        :param desc: Optional description string.
        :return: Transformed :class:`Sequence`.
        """
        return Sequence(
            map(f, self),
            lambda i: f(self[i]),
            containf,
            desc
        )

    def __call__(self, other):
        """Compose this sequence's item function with another sequence.

        Equivalent to ``other.apply(self.itemf)``.

        :param other: :class:`Sequence` to transform.
        :return: Composed :class:`Sequence`.
        """
        return other.apply(self.itemf)

    def filter(self, f, desc=''):
        """Filter the sequence by a predicate function.

        Example:
            Mersenne exponents (OEIS `A000043 <https://oeis.org/A000043>`_),
            primes :math:`p` such that :math:`2^p - 1` is prime:

            >>> # A000043 = primes.filter(math2.lucas_lehmer)

        :param f: Predicate callable returning ``True`` for terms to retain.
        :param desc: Optional description string.
        :return: Filtered :class:`Sequence`.
        """
        return Sequence(
            filter(f, self),
            None,
            lambda n: f(n) and n in self,
            desc
        )

    def __le__(self, other):
        """Select terms from self where self[i] <= other[i]."""
        return Sequence(
            itertools2.select(self, other, operator.le)
        )

    def __gt__(self, other):
        """Select terms from self where self[i] > other[i]."""
        return Sequence(
            itertools2.select(self, other, operator.gt)
        )

    def accumulate(self, op=operator.add, init=[]):
        """Return a sequence of partial reductions / running accumulations.

        By default, computes the prefix sums (:math:`s_n = \\\\sum_{k=0}^n a_k`).

        Example:
            Sum of the first *n* primes (OEIS `A007504 <https://oeis.org/A007504>`_):

            >>> # A007504 = primes.accumulate()

        :param op: Binary operator function (default: :func:`operator.add`).
        :param init: Optional initial elements sequence prepended to the result.
        :return: Accumulated :class:`Sequence`.
        """
        return Sequence(chain(init, itertools2.accumulate(self, op, False)))

    def pairwise(self, op, skip_first=False):
        """Apply a binary operator to consecutive terms :math:`(a_n, a_{n+1})`.

        Note that :func:`goulib.itertools2.pairwise` calls ``op(current, prev)``
        (e.g., :func:`operator.sub` computes :math:`a_{n+1} - a_n`).

        Example:
            Differences between consecutive primes / prime gaps
            (OEIS `A001223 <https://oeis.org/A001223>`_):

            >>> # A001223 = primes.pairwise(operator.sub)

        :param op: Binary operator applied to consecutive pairs.
        :param skip_first: If ``True``, omits the first pair.
        :return: :class:`Sequence` of pairwise results.
        """
        return Sequence(itertools2.pairwise(self, op))

    def sort(self, key=None, buffer=100):
        """Sort an almost-sorted (monotonically growing) infinite sequence.

        Maintains a sliding buffer of size *buffer* using
        :func:`goulib.itertools2.sorted_iterable`. As long as elements are not
        displaced by more than *buffer* positions, the output sequence is
        guaranteed to be strictly sorted.

        Example:
            Ordered areas of primitive Pythagorean triangles
            (OEIS `A024406 <https://oeis.org/A024406>`_):

            >>> # A024406 = Sequence(math2.primitive_triples).apply(
            ... #     lambda x: x[0] * x[1] // 2
            ... # ).sort()

        :param key: Optional sort key function.
        :param buffer: Size of the lookahead buffer (default: 100).
        :return: Sorted :class:`Sequence`.
        """
        return Sequence(itertools2.sorted_iterable(self, key, buffer))

    def unique(self, buffer=100):
        """Remove redundant duplicate elements from an almost-sorted sequence.

        Maintains a history of the last *buffer* elements using
        :func:`goulib.itertools2.unique`.

        Example:
            Twin prime members (OEIS `A001097 <https://oeis.org/A001097>`_)
            from flattened twin prime pairs (where 5 appears in both (3,5) and (5,7)):

            >>> # A001097 = A077800.unique()

        :param buffer: Number of recent elements to track for duplicates (default: 100).
            If duplicate elements are separated by more than *buffer* terms, they might
            be emitted more than once.
        :return: :class:`Sequence` of unique elements.
        """
        return Sequence(itertools2.unique(self, None, buffer))

    def product(self, other, op=sum, buffer=100):
        """Compute the Cartesian product of two sequences, transformed and sorted.

        Generates pairs from *self* and *other* using
        :func:`goulib.itertools2.product`, applies reduction *op* (default: :func:`sum`),
        and sorts the stream with a buffer of size *buffer*.

        :param other: Second :class:`Sequence`.
        :param op: Function applied to each pair (default: :func:`sum`).
        :param buffer: Size of sorting buffer (default: 100).
        :return: Transformed and sorted :class:`Sequence`.
        """
        it = itertools2.product(self, other)
        return Sequence(it).apply(op).sort(buffer=buffer)


# copied from https://code.activestate.com/recipes/577197-sortedcollection/


class SortedCollection(object):
    '''Sequence sorted by a key function.

    SortedCollection() is much easier to work with than using bisect() directly.
    It supports key functions like those use in sorted(), min(), and max().
    The result of the key function call is saved so that keys can be searched
    efficiently.

    Instead of returning an insertion-point which can be hard to interpret, the
    five find-methods return a specific item in the sequence. They can scan for
    exact matches, the last item less-than-or-equal to a key, or the first item
    greater-than-or-equal to a key.

    Once found, an item's ordinal position can be located with the index() method.
    New items can be added with the insert() and insert_right() methods.
    Old items can be deleted with the remove() method.

    The usual sequence methods are provided to support indexing, slicing,
    length lookup, clearing, copying, forward and reverse iteration, contains
    checking, item counts, item removal, and a nice looking repr.

    Finding and indexing are O(log n) operations while iteration and insertion
    are O(n).  The initial sort is O(n log n).

    The key function is stored in the 'key' attibute for easy introspection or
    so that you can assign a new key function (triggering an automatic re-sort).

    In short, the class was designed to handle all of the common use cases for
    bisect but with a simpler API and support for key functions.

    >>> from pprint import pprint
    >>> from operator import itemgetter

    >>> s = SortedCollection(key=itemgetter(2))
    >>> for record in [
    ...         ('roger', 'young', 30),
    ...         ('angela', 'jones', 28),
    ...         ('bill', 'smith', 22),
    ...         ('david', 'thomas', 32)]:
    ...     s.insert(record)

    >>> pprint(list(s))         # show records sorted by age
    [('bill', 'smith', 22),
     ('angela', 'jones', 28),
     ('roger', 'young', 30),
     ('david', 'thomas', 32)]

    >>> s.find_le(29)           # find oldest person aged 29 or younger
    ('angela', 'jones', 28)
    >>> s.find_lt(28)           # find oldest person under 28
    ('bill', 'smith', 22)
    >>> s.find_gt(28)           # find youngest person over 28
    ('roger', 'young', 30)

    >>> r = s.find_ge(32)       # find youngest person aged 32 or older
    >>> s.index(r)              # get the index of their record
    3
    >>> s[3]                    # fetch the record at that index
    ('david', 'thomas', 32)

    >>> s.key = itemgetter(0)   # now sort by first name
    >>> pprint(list(s))
    [('angela', 'jones', 28),
     ('bill', 'smith', 22),
     ('david', 'thomas', 32),
     ('roger', 'young', 30)]

    '''

    def __init__(self, iterable=(), key=None):
        self._given_key = key
        key = (lambda x: x) if key is None else key
        decorated = sorted((key(item), item) for item in iterable)
        self._keys = [k for k, item in decorated]
        self._items = [item for k, item in decorated]
        self._key = key

    def _getkey(self):
        return self._key

    def _setkey(self, key):
        if key is not self._key:
            self.__init__(self._items, key=key)

    def _delkey(self):
        self._setkey(None)

    key = property(_getkey, _setkey, _delkey, 'key function')

    def clear(self):
        self.__init__([], self._key)

    def copy(self):
        return self.__class__(self, self._key)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def __setitem__(self, _, item):
        k = self._key(item)
        i = bisect_left(self._keys, k)
        self._items[i] = item

    def __iter__(self):
        return iter(self._items)

    def __reversed__(self):
        return reversed(self._items)

    def __repr__(self):
        return '%s(%r, key=%s)' % (
            self.__class__.__name__,
            self._items,
            getattr(self._given_key, '__name__', repr(self._given_key))
        )

    def __reduce__(self):
        return self.__class__, (self._items, self._given_key)

    def __contains__(self, item):
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return item in self._items[i:j]

    def index(self, item):
        'Find the position of an item.  Raise ValueError if not found.'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].index(item) + i

    def count(self, item):
        'Return number of occurrences of item'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].count(item)

    def insert(self, item):
        'Insert a new item.  If equal keys are found, add to the left'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        self._keys.insert(i, k)
        self._items.insert(i, item)

    def insert_right(self, item):
        'Insert a new item.  If equal keys are found, add to the right'
        k = self._key(item)
        i = bisect_right(self._keys, k)
        self._keys.insert(i, k)
        self._items.insert(i, item)

    def remove(self, item):
        'Remove first occurence of item.  Raise ValueError if not found'
        i = self.index(item)
        del self._keys[i]
        del self._items[i]

    def find(self, k):
        'Return first item with a key == k.  Raise ValueError if not found.'
        i = bisect_left(self._keys, k)
        if i != len(self) and self._keys[i] == k:
            return self._items[i]
        raise ValueError('No item found with key equal to: %r' % (k,))

    def find_le(self, k):
        'Return last item with a key <= k.  Raise ValueError if not found.'
        i = bisect_right(self._keys, k)
        if i:
            return self._items[i-1]
        raise ValueError('No item found with key at or below: %r' % (k,))

    def find_lt(self, k):
        'Return last item with a key < k.  Raise ValueError if not found.'
        i = bisect_left(self._keys, k)
        if i:
            return self._items[i-1]
        raise ValueError('No item found with key below: %r' % (k,))

    def find_ge(self, k):
        'Return first item with a key >= equal to k.  Raise ValueError if not found'
        i = bisect_left(self._keys, k)
        if i != len(self):
            return self._items[i]
        raise ValueError('No item found with key at or above: %r' % (k,))

    def find_gt(self, k):
        'Return first item with a key > k.  Raise ValueError if not found'
        i = bisect_right(self._keys, k)
        if i != len(self):
            return self._items[i]
        raise ValueError('No item found with key above: %r' % (k,))
