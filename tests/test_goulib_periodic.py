import pytest
from goulib.expr import Expr
from goulib.periodic import Periodic


def test_periodic():
    e = Expr('x % 2')
    p = Periodic(e, (0, 2))
    assert p.period() == 2
    assert 'period=2' in str(p)
    assert 'period=2' in repr(p)
    assert p(0) == 0
    assert p(1) == 1
    assert p(2) == 0
    assert p(3) == 1

    p2 = Periodic(e, 4)
    assert p2.period() == 4

    p_inf = Periodic(e, (0, float('inf')))
    assert p_inf.period() == 0
