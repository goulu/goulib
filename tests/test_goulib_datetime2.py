from goulib.tests import *      # pylint: disable=wildcard-import, unused-wildcard-import
from goulib.datetime2 import *  # pylint: disable=wildcard-import, unused-wildcard-import


class TestDatef:
    def test_datef(self):
        d = date(year=1963, month=12, day=25)
        assert datef(d) == d
        assert datef('1963-12-25') == d
        assert datef('25/12/1963', fmt='%d/%m/%Y') == d
        # http://answers.oreilly.com/topic/1694-how-excel-stores-date-and-time-values/
        assert datef(40179, fmt=None) == date(year=2010, month=1, day=1)
        # http://answers.oreilly.com/topic/1694-how-excel-stores-date-and-time-values/
        assert (datef(40179, fmt='Excel') ==
                date(year=2010, month=1, day=1))


class TestTimef:
    def test_timef(self):
        t = time(hour=12, minute=34, second=56)
        assert timef(t) == t
        assert timef('12:34:56') == t
        # http://answers.oreilly.com/topic/1694-how-excel-stores-date-and-time-values/
        t = timef(0.503473, fmt='%d')
        assert equal(t, time(hour=12, minute=5))


class TestDatetimef:
    def test_datetimef(self):
        d = datetime(year=1963, month=12, day=25,
                     hour=12, minute=34, second=56)
        t = d.time()
        assert datetimef(d) == d
        assert datetimef('1963-12-25', t) == d
        assert datetimef('25/12/1963', t, fmt='%d/%m/%Y') == d
        # http://answers.oreilly.com/topic/1694-how-excel-stores-date-and-time-values/
        assert equal(datetimef(40179.503472, fmt=None), datetime(
            year=2010, month=0o1, day=0o1, hour=12, minute=0o5))


class TestTimedeltaf:
    def test_timedeltaf(self):
        td = timedelta(days=25, hours=12, minutes=34, seconds=56)
        s = str(td)
        s = timedeltaf(s)
        assert s == td
        # check with hours > 24
        s = ('%d:%d:%d' % (25*24+12, 34, 56))
        s = timedeltaf(s)
        assert s == td
        # check microseconds
        td = timedelta(0, 0, 123456)
        s = str(td)
        s = timedeltaf(s)
        assert s == td
        # check miliseconds
        td = timedeltaf('00:00:00.123')
        assert td.microseconds == 123000
        # check negative values
        td = timedeltaf('-1 day, 00:00:00')
        assert str(td) == '-1 day, 0:00:00'

        td = timedelta(microseconds=-1)
        s = str(td)
        s = timedeltaf(s)
        assert s == td


class TestStrftimedelta:
    def test_strftimedelta(self):
        d1 = datetime(year=1963, month=12, day=25,
                      hour=12, minute=34, second=56)
        d2 = datetime(year=1965, month=6, day=13,
                      hour=0o1, minute=23, second=45)
        td = d2-d1
        assert strftimedelta(td) == '12852:48:49'


class TestTdround:
    def test_tdround(self):
        td = timedelta(seconds=10000)
        assert tdround(td, 60) == timedelta(seconds=10020)


class TestMinutes:
    def test_minutes(self):
        td = timedelta(seconds=10000)
        assert minutes(td) == 10000./60


class TestHours:
    def test_hours(self):
        td = timedelta(seconds=10000)
        assert hours(td) == 10000./3600


class TestDaysgen:
    def test_daysgen(self):
        start = datetime(year=1963, month=12, day=25,
                         hour=12, minute=34, second=56)
        for d in daysgen(start, 10):
            pass
        assert d == datetime(year=1964, month=1,
                             day=3, hour=12, minute=34, second=56)
        for d in daysgen(start, 15, onehour):
            pass
        assert d == datetime(year=1963, month=12,
                             day=26, hour=2, minute=34, second=56)


class TestDays:
    def test_days(self):
        r = days(datetime.today(), 21)
        assert len(r) == 21


class TestTimedeltaSum:
    def test_timedelta_sum(self):
        td = timedelta(seconds=10000)
        assert timedelta_sum([td]*6) == timedelta(seconds=60000)
        assert timedelta_sum([]) == timedelta0


class TestTimedeltaDiv:
    def test_timedelta_div(self):
        assert timedelta_div(oneday, onehour) == 24


class TestTimedeltaMul:
    def test_timedelta_mul(self):
        assert timedelta_mul(onehour, 24) == oneday


class TestTimeSub:
    def test_time_sub(self):
        t1 = time(hour=12, minute=34, second=56)
        t2 = time(hour=0o1, minute=23, second=45)
        assert time_sub(t1, t2) == timedelta(seconds=40271)


class TestTimeAdd:
    def test_time_add(self):
        t1 = time(hour=12, minute=34, second=56)
        t2 = time(hour=0o1, minute=23, second=45)
        assert time_add(t2, timedelta(seconds=40271)) == t1


class TestDatetimeIntersect:
    def test_datetime_intersect(self):
        start = datetime(year=1963, month=12, day=25,
                         hour=12, minute=34, second=56)
        td = timedelta(seconds=40271)
        d = [d for d in daysgen(start, 4, td)]
        assert datetime_intersect([d[0], d[2]], [d[1], d[3]]) == td


class TestTimeIntersect:
    def test_time_intersect(self):
        start = time(hour=12, minute=34, second=56)
        td = timedelta(seconds=1271)
        d = [d for d in daysgen(start, 4, td)]
        assert time_intersect([d[0], d[2]], [d[1], d[3]]) == td


class TestAddMonths:
    def test_add_months(self):
        # assert_equal(expected, add_months(date, months))
        # month wrap with end-of-month handling and leap year
        d = date(year=2020, month=1, day=31)
        assert add_months(d, 1) == date(year=2020, month=2, day=29)
        assert add_months(date(year=2019, month=12, day=15),
                          2) == date(year=2020, month=2, day=15)


class TestDateAdd:
    def test_date_add(self):
        # assert_equal(expected, date_add(date, years, months, weeks, days))
        d = date(year=2019, month=1, day=31)
        res = date_add(d, years=1, months=1, weeks=1, days=1)
        # expected = add_months(d, years*12+months) + (weeks*7+days)*oneday
        expected = add_months(d, 1*12 + 1) + (1*7 + 1) * oneday
        assert res == expected
