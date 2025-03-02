#!/usr/bin/env python
# coding: utf8
"""
utilities for unit tests (using pytest)
"""


__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2014-, Philippe Guglielmetti"
__license__ = "LGPL"

import logging
import itertools
import unittest
import pytest

from goulib import itertools2, decorators


def pprint_gen(iterable, indices=[0, 1, 2, -3, -2, -1], sep='...'):
    """generates items at specified indices"""
    try:
        l = len(iterable)
        indices = (i if i >= 0 else l+i for i in indices if i < l)
    except:  # infinite iterable
        l = None
        indices = filter(lambda x: x >= 0, indices)
    indices = list(itertools2.unique(indices))  # to remove overlaps
    indices.sort()

    j = 0
    hole = 0
    for i, item in enumerate(iterable):
        if i == indices[j]:
            yield item
            j += 1
            hole = 0
            if j == len(indices):
                if l is None:
                    yield sep
                break  # finished
        else:
            hole += 1
            if hole == 1:
                if sep:
                    yield sep


def pprint(iterable, indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, -3, -2, -1], timeout=1):
    sep = '...'
    s = []
    try:
        items = pprint_gen(iterable, indices, sep)
        for item in decorators.itimeout(items, timeout):
            if isinstance(item, str):
                s.append(item)  # to keep unicode untouched
            else:
                s.append(str(item))
    except decorators.TimeoutError:
        if s[-1] != sep:
            s.append(sep)
    return ','.join(s)


class TestCase(unittest.TestCase):

    def assertSequenceEqual(self, seq1, seq2, msg=None, seq_type=None, places=7, delta=None, reltol=None):
        """
        An equality assertion for ordered sequences (like lists and tuples).
        constraints on seq1,seq2 from unittest.TestCase.assertSequenceEqual are mostly removed

        :param seq1, seq2: iterables to compare for (quasi) equality
        :param msg: optional string message to use on failure instead of a list of differences
        :param places: int number of digits to consider in float comparisons.
                If None, enforces strict equality
        :param delta: optional float absolute tolerance value
        :param reltol: optional float relative tolerance value
        """

        # we must tee or copy sequences in order to exhaust generators in pprint
        # TODO: find a way (if any...) to move this in pprint
        seq1, p1 = itertools2.tee(seq1, copy=None)
        seq2, p2 = itertools2.tee(seq2, copy=None)
        seq1_repr = pprint(p1)
        seq2_repr = pprint(p2)

        if seq_type is not None:
            seq_type_name = seq_type.__name__
            if not isinstance(seq1, seq_type):
                raise self.failureException(
                    'First sequence is not a %s: %s' % (seq_type_name, seq1_repr))
            if not isinstance(seq2, seq_type):
                raise self.failureException(
                    'Second sequence is not a %s: %s' % (seq_type_name, seq2_repr))
        else:
            seq_type_name = "sequence"

        elements = (seq_type_name.capitalize(), seq1_repr, seq2_repr)
        differing = '%ss differ: %s != %s\n' % elements

        class End(object):
            def __repr__(self):
                return '(end)'
        end = End()  # a special object is appended to detect mismatching lengths

        i = 0
        for item1, item2 in zip(itertools.chain(seq1, [end]), itertools.chain(seq2, [end])):
            m = (msg if msg else differing) + \
                'First differing element %d: %s != %s\n' % (i, item1, item2)
            self.assertEqual(item1, item2, places=places,
                             msg=m, delta=delta, reltol=reltol)
            i += 1
        return i  # number of elements checked

    base_types = (int, str, str, bool, set, dict)

    def assertEqual(self, first, second, places=7, msg=None, delta=None, reltol=None):
        """automatically calls assertAlmostEqual when needed
        :param first, second: objects to compare for (quasi) equality
        :param places: int number of digits to consider in float comparisons.
                        If None, forces strict equality
        :param msg: optional string error message to display in case of failure
        :param delta: optional float absolute tolerance value
        :param reltol: optional float relative tolerance value
        """
        # inspired from http://stackoverflow.com/a/3124155/190597 (KennyTM)
        import typing

        if delta is None:
            if places is None or (isinstance(first, self.base_types) and isinstance(second, self.base_types)):
                return super(TestCase, self).assertEqual(first, second, msg=msg)

        else:
            places = None

        if (isinstance(first, typing.Iterable) and isinstance(second, typing.Iterable)):
            try:
                self.assertSequenceEqual(
                    first, second, msg=msg, places=places, delta=delta, reltol=reltol)
            except TypeError as e:  # for some classes like pint.Quantity
                super(TestCase, self).assertEqual(first, second, msg=msg)
        elif reltol:
            ratio = first/second if second else second/first
            msg = '%s != %s within %.2f%%' % (first, second, reltol*100)
            super(TestCase, self).assertAlmostEqual(
                ratio, 1, places=None, msg=msg, delta=reltol)
        else:  # float and classes
            try:
                super(TestCase, self).assertAlmostEqual(
                    first, second, places=places, msg=msg, delta=delta)
            except TypeError as e:  # unsupported operand type(s) for -
                super(TestCase, self).assertEqual(first, second, msg=msg)

    def assertCountEqual(self, seq1, seq2, msg=None):
        """compare iterables converted to sets : order has no importance"""
        self.assertEqual(set(seq1), set(seq2), msg=msg)

    def assertMatch(self, value, pattern, flags=0, msg=None):
        import re
        value = str(value)
        if msg is None:
            msg = 'string %s does not match regex %s' % (value, pattern)

        self.assertTrue(re.match(pattern, value, flags), msg)


def setlog(level=logging.INFO, fmt='%(levelname)s:%(filename)s:%(funcName)s: %(message)s'):
    """initializes logging
    :param level: logging level
    :param fmt: string
    """
    logging.basicConfig(level=level, format=fmt)
    logger = logging.getLogger()

    logger.setLevel(level)
    logger.handlers[0].setFormatter(logging.Formatter(fmt))
    return logger


setlog()


def runmodule(level=logging.INFO, verbosity=1, argv=None):
    """
    mocks a nose call to run the current module as a test suite
    :param argv: optional list of string with additional options passed to pytest.main
    see http://nose.readthedocs.org/en/latest/usage.html
    see https://docs.pytest.org/en/stable/how-to/usage.html
    """
    import sys
    module_name = sys.modules["__main__"].__file__

    if argv is None:
        return pytest.main([module_name])

    setlog(level)

    """ ensures stdout is printed after the tests results"""
    import sys
    from io import StringIO

    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    result = pytest.main(
        [module_name]+argv
    )

    sys.stdout = old_stdout
    print(mystdout.getvalue())
