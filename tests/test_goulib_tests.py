from goulib.tests import *  # a module that tests itself using itself... cool :-)


class TestPprint:
    def test_pprint(self):
        import itertools
        assert pprint(range(100)) == '0,1,2,3,4,5,6,7,8,9,...,97,98,99'
        assert pprint(range(4)) == '0,1,2,3'
        assert pprint(itertools.count()) == '0,1,2,3,4,5,6,7,8,9,...'
        assert '...' in pprint(itertools.count(), timeout=0.0001)


class TestRunmodule:
    def test_runmodule(self):
        from unittest.mock import patch
        with patch('pytest.main', return_value=0):
            runmodule(argv=None)
            runmodule(argv=['-q'])


class TestSetlog:
    def test_setlog(self):
        logger = setlog(logging.INFO)
        assert logger is not None


class TestPprintGen:
    def test_pprint_gen(self):
        items = list(pprint_gen(range(5), (0, 1, 2, 3, 4), '...'))
        assert items == [0, 1, 2, 3, 4]


class TestTestCase(TestCase):
    def test_assertSequenceEqual(self):
        self.assertSequenceEqual([1, 2, 3], [1, 2, 3], seq_type=list)
        self.assertSequenceEqual((1.0, 2.0), (1.00000001, 2.00000001), places=6)

    def test_assertEqual(self):
        self.assertEqual(1, 1)
        self.assertEqual([1, 2], [1, 2])
        self.assertEqual(1.0, 1.05, delta=0.1)
        self.assertEqual(100.0, 101.0, reltol=0.02)

    def test_assertCountEqual(self):
        self.assertCountEqual([1, 2, 3], [3, 2, 1])

    def test_assertMatch(self):
        self.assertMatch('abc123', r'abc\d+')
