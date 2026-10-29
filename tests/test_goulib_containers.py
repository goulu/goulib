from goulib.tests import *      # pylint: disable=wildcard-import, unused-wildcard-import
from goulib.containers import *  # pylint: disable=wildcard-import, unused-wildcard-import

class TestRecord:
    @classmethod
    def setup_class(cls):
        cls.d = {'first': 'Albert', 'last': 'Einstein'}
        cls.r = Record(cls.d)
        # assert_raises(AttributeError, lambda: cls.r.birth)

    def test___init__(self):
        pass

    def test___getattr__(self):
        assert self.r.first == self.d['first']
        assert self.r['first'] == self.d['first']

    def test___setattr__(self):
        self.r.born = 1879
        assert self.r['born'] == 1879

        r2 = self.r.copy()
        r2.first = 'Franck'  # Franck Enstein ;-)
        # check the fields are copied
        assert self.r.first == self.d['first']

    def test___repr__(self):
        # record = Record(*args, **kwargs)
        # assert_equal(expected, record.__str__())
        pytest.skip("not yet implemented")  # TODO: implement

def test_SortedCollection():
    #copied from https://code.activestate.com/recipes/577197-sortedcollection/
    def ve2no(f, *args):
        'Convert ValueError result to -1'
        try:
            return f(*args)
        except ValueError:
            return -1

    def slow_index(seq, k):
        'Location of match or -1 if not found'
        for i, item in enumerate(seq):
            if item == k:
                return i
        return -1

    def slow_find(seq, k):
        'First item with a key equal to k. -1 if not found'
        for item in seq:
            if item == k:
                return item
        return -1

    def slow_find_le(seq, k):
        'Last item with a key less-than or equal to k.'
        for item in reversed(seq):
            if item <= k:
                return item
        return -1

    def slow_find_lt(seq, k):
        'Last item with a key less-than k.'
        for item in reversed(seq):
            if item < k:
                return item
        return -1

    def slow_find_ge(seq, k):
        'First item with a key-value greater-than or equal to k.'
        for item in seq:
            if item >= k:
                return item
        return -1

    def slow_find_gt(seq, k):
        'First item with a key-value greater-than or equal to k.'
        for item in seq:
            if item > k:
                return item
        return -1

    from random import choice
    pool = [1.5, 2, 2.0, 3, 3.0, 3.5, 4, 4.0, 4.5]
    for i in range(500):
        for n in range(6):
            s = [choice(pool) for i in range(n)]
            sc = SortedCollection(s)
            s.sort()
            for probe in pool:
                assert repr(ve2no(sc.index, probe)) == repr(slow_index(s, probe))
                assert repr(ve2no(sc.find, probe)) == repr(slow_find(s, probe))
                assert repr(ve2no(sc.find_le, probe)) == repr(slow_find_le(s, probe))
                assert repr(ve2no(sc.find_lt, probe)) == repr(slow_find_lt(s, probe))
                assert repr(ve2no(sc.find_ge, probe)) == repr(slow_find_ge(s, probe))
                assert repr(ve2no(sc.find_gt, probe)) == repr(slow_find_gt(s, probe))
            for i, item in enumerate(s):
                assert repr(item) == repr(sc[i])        # test __getitem__
                assert item in sc                       # test __contains__ and __iter__
                assert s.count(item) == sc.count(item)  # test count()
            assert len(sc) == n                         # test __len__
            assert list(map(repr, reversed(sc))) == list(map(repr, reversed(s)))    # test __reversed__
            assert list(sc.copy()) == list(sc)          # test copy()
            sc.clear()                                  # test clear()
            assert len(sc) == 0

    sd = SortedCollection('The quick Brown Fox jumped'.split(), key=str.lower)
    assert sd._keys == ['brown', 'fox', 'jumped', 'quick', 'the']
    assert sd._items == ['Brown', 'Fox', 'jumped', 'quick', 'The']
    assert sd._key == str.lower
    assert repr(sd) == "SortedCollection(['Brown', 'Fox', 'jumped', 'quick', 'The'], key=lower)"
    sd.key = str.upper
    assert sd._key == str.upper
    assert len(sd) == 5
    assert list(reversed(sd)) == ['The', 'quick', 'jumped', 'Fox', 'Brown']
    for item in sd:
        assert item in sd
    for i, item in enumerate(sd):
        assert item == sd[i]
    sd.insert('jUmPeD')
    sd.insert_right('QuIcK')
    assert sd._keys ==['BROWN', 'FOX', 'JUMPED', 'JUMPED', 'QUICK', 'QUICK', 'THE']
    assert sd._items == ['Brown', 'Fox', 'jUmPeD', 'jumped', 'quick', 'QuIcK', 'The']
    assert sd.find_le('JUMPED') == 'jumped', sd.find_le('JUMPED')
    assert sd.find_ge('JUMPED') == 'jUmPeD'
    assert sd.find_le('GOAT') == 'Fox'
    assert sd.find_ge('GOAT') == 'jUmPeD'
    assert sd.find('FOX') == 'Fox'
    assert sd[3] == 'jumped'
    assert sd[3:5] ==['jumped', 'quick']
    assert sd[-2] == 'QuIcK'
    assert sd[-4:-2] == ['jumped', 'quick']
    for i, item in enumerate(sd):
        assert sd.index(item) == i
    try:
        sd.index('xyzpdq')
    except ValueError:
        pass
    else:
        assert 0, 'Oops, failed to notify of missing value'
    sd.remove('jumped')
    assert list(sd) == ['Brown', 'Fox', 'jUmPeD', 'quick', 'QuIcK', 'The']


class TestSequence:
    def test_basic_sequence(self):
        # Sequence defined by formula f(i) = 2*i
        s = Sequence(itemf=lambda i: 2 * i, desc="even numbers")
        assert repr(s).startswith("Sequence = (0,2,4,6,8,10,12,14,16,18")
        assert s[0] == 0
        assert s[5] == 10
        assert 10 in s
        assert 11 not in s
        assert s.index(10) == 5
        assert s.index(11) == -1
        assert list(islice(s, 5)) == [0, 2, 4, 6, 8]

    def test_arithmetic(self):
        s1 = Sequence(itemf=lambda i: 2 * i)
        s2 = Sequence(itemf=lambda i: i)

        s_add = s1 + s2
        assert list(islice(s_add, 5)) == [0, 3, 6, 9, 12]
        assert s_add[4] == 12

        s_sub = s1 - s2
        assert list(islice(s_sub, 5)) == [0, 1, 2, 3, 4]
        assert s_sub[4] == 4

        s_mul = s1 * s2
        assert list(islice(s_mul, 5)) == [0, 2, 8, 18, 32]
        assert s_mul[4] == 32

        s_plus_int = s2 + 10
        assert list(islice(s_plus_int, 5)) == [10, 11, 12, 13, 14]
        assert 12 in s_plus_int

        s_sub_int = s2 - 5
        assert list(islice(s_sub_int, 5)) == [-5, -4, -3, -2, -1]

    def test_filter_and_apply(self):
        s = Sequence(itemf=lambda i: i)
        s_even = s.filter(lambda x: x % 2 == 0)
        assert list(islice(s_even, 5)) == [0, 2, 4, 6, 8]

        s_sq = s.apply(lambda x: x * x)
        assert list(islice(s_sq, 5)) == [0, 1, 4, 9, 16]

    def test_accumulate_pairwise(self):
        s = Sequence(itemf=lambda i: 1)
        acc = s.accumulate()
        assert list(islice(acc, 5)) == [1, 2, 3, 4, 5]

        s_nats = Sequence(itemf=lambda i: i)
        import operator
        diffs = s_nats.pairwise(operator.sub)
        assert list(islice(diffs, 5)) == [1, 1, 1, 1, 1]