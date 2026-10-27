from goulib.tests import *  # pylint: disable=wildcard-import, unused-wildcard-import
from goulib.units import *  # pylint: disable=wildcard-import, unused-wildcard-import

import collections

class Tests:
    def test001_simple_value(self):
        ureg.define('CHF = [Currency]')
        ureg.define('EUR = 1.21*CHF')
        ureg.define('USD = 0.93*CHF')
        dist = V(1000, 'm')
        assert str(dist) == '1000 meter'
        speed = V(10, 'm/s')
        assert str(speed) == '10 meter / second'
        time = dist/speed
        assert str(time) == '100.0 second'
        hourlyRate = V(50, 'USD/hour')
        cost = hourlyRate*time
        # warning : Py2 and Py3 have different precision for str(float)
        assert '{:f}'.format(cost.to('CHF')) == '1.291667 CHF'

    def test002_table(self):
        t = Table('mytable',      ['car',          'bus',                                     'pedestrian'],
                  ['speed',        V(120, 'km/hour'), V(100, 'km/hour'),                          V(5, 'km/hour'),
                   'acceleration', V(
                      1, 'm/s^2'),     V(0.1, 'm/s^2'),                            V(0.2, 'm/s^2'),
                   'autonomy',     V(600, 'km'), lambda: t['autonomy']['pedestrian'] *
                   10, lambda: t['speed']['pedestrian']*V(6, 'hour')  # coucou
                   ])
        assert collections.Counter(t.cols) == collections.Counter(
            ['car',        'bus',         'pedestrian'])
        assert collections.Counter(t.rowLabels) == collections.Counter([
            'speed', 'acceleration', 'autonomy'])
        from pprint import pformat  # otherwise it takes goulib.tests.pprint...
        logging.debug(pformat(t.rows))
        assert t['speed']['bus'] == V(100, 'km/hour')
        logging.debug(t._repr_html_())

        v = View(t, rows=['autonomy', 'speed'], cols=['car', 'pedestrian'], rowUnits={
                 'speed': 'mile/hour'}, name='my view')
        logging.debug(v._repr_html_())

        t.appendCol('cheval', {'speed': V(
            60, 'km/hour'), 'acceleration': V(0.3, 'm/s^2'), 'autonomy': V(40, 'km')})
        logging.debug(t._repr_html_())

        t.appendRow('length', [V(4552, 'mm'), V(20, 'm'),
                    V(50, 'cm'), V(100, 'inch')], unit='m')
        logging.debug(t._repr_html_())

    def test003_m(self):
        v = V(60, 'm/min')
        assert v('m/s') == 1

    def test004_TableCell(self):
        t = Table('test cell', [], [])
        t.setCell(('speed', 'km/hour'), 'car', V(100, 'mph'))
        t.setCell('speed', 'bus', V(100, 'km/hour'))
        assert (t['speed']['car'])('km/hour') == pytest.approx(160.9344)
        t.setCell('acceleration', 'car', V(1, 'm/s^2'))
        logging.info(t._repr_html_())


class TestMagnitudeIn:
    def test_magnitude_in(self):
        v = V(100, 'cm')
        assert magnitudeIn(v, 'm') == 1


class TestIsfunc:
    def test_isfunc(self):
        r = Row({'a': lambda: 42, 'b': 10})
        assert r.isfunc('a')
        assert not r.isfunc('b')
        assert not r.isfunc('c')


class TestSetCell:
    def test_set_cell(self):
        t = Table('T', ['c1'], [])
        t.setCell('r1', 'c1', V(5, 'm'))
        assert t['r1']['c1'] == V(5, 'm')


class TestAppendCol:
    def test_append_col(self):
        t = Table('T', ['c1'], ['r1', 1])
        t.appendCol('c2', {'r1': 2})
        assert t['r1']['c2'] == 2


class TestAppendRow:
    def test_append_row(self):
        t = Table('T', ['c1'], ['r1', 1])
        t.appendRow('r2', [2])
        assert t['r2']['c1'] == 2


class TestAppendColFromObj:
    def test_append_col_from_obj(self):
        class Dummy:
            r1 = 10
        t = Table('T', ['c1'], ['r1', 1])
        t.appendColFromObj('c2', Dummy())
        assert t['r1']['c2'] == 10

