from goulib.tests import *
from goulib.workdays import *
from datetime import datetime


class TestWorkCalendar:
    @classmethod
    def setup_class(self):
        self.base = WorkCalendar()
        # derive a specific calendar, with "inherited" weekends for deeper tests
        self.cal = WorkCalendar([8, 16], parent=self.base, weekends=[])
        self.cal.addholidays(date(1, 12, 25))  # Christmas was a SUN in 2011
        # NewYear was also a SUN in 2012...
        self.cal.addholidays(date(1, 1, 1))
        self.cal.addholidays(date(2012, 1, 2))  # ...so the 2th was holiday
        start = date(2011, 12, 18)  # start of holidays
        end = date(2012, 1, 8)  # the company was closed 3 weeks
        closed = self.base.range(end, start)
        self.cal.addholidays(closed)

    def test___init__(self):
        pass  # tested above

    def test_addholidays(self):
        date1 = date(2011, 12, 16)  # a FRI close to year end and holidays
        date2 = date(2012, 1, 9)  # a MON close to next year begin
        # calendar is inited with addholidays in setup_class above
        assert self.cal.networkdays(date1, date2) == 2

    def test_cast(self):
        cal = WorkCalendar([8, 16])
        assert cal.cast(datetime(2012, 1, 9, 10)) == datetime(2012, 1, 9, 10)
        assert cal.cast(datetime(2012, 1, 9, 3)) == datetime(2012, 1, 9, 8)
        assert cal.cast(datetime(2012, 1, 9, 3), retro=True) == datetime(
            2012, 1, 6, 16)  # TODO: check if it's correct
        assert cal.cast(datetime(2012, 1, 9, 17)) == datetime(2012, 1, 10, 8)
        # cast friday 19h to next monday 8h
        assert cal.cast(datetime(2011, 12, 16, 19)
                        ) == datetime(2011, 12, 19, 8)
        assert cal.cast(datetime(2011, 12, 16, 19),
                        retro=True) == datetime(2011, 12, 16, 16)

    def test_diff(self):
        date1 = date(2011, 12, 16)  # a FRI close to year end and holidays
        date2 = date(2012, 1, 9)  # a MON close to next year begin
        assert self.cal.diff(date1, date2) == timedelta(hours=8)
        assert self.cal.diff(date2, date1) == timedelta(hours=-8)

    def test_gethours(self):
        date1 = date(2011, 12, 16)  # a FRI close to year end and holidays
        date2 = date(2012, 1, 9)  # a MON close to next year begin
        assert self.cal.gethours(date1, date2) == 8

    def test_isworkday(self):
        assert self.cal.isworkday(date(2011, 12, 16))
        assert not self.cal.isworkday(date(2011, 12, 17))

    def test_isworktime(self):
        assert self.cal.isworktime(datetime(2012, 1, 9, 8, 0, 0))
        assert not self.cal.isworktime(datetime(2012, 1, 9, 7, 59, 59))

    def test_minus(self):
        start = date(2012, 1, 9)
        assert isinstance(self.cal.minus(start, timedelta(days=1)), (date, datetime))

    def test_networkdays(self):
        date1 = date(2011, 12, 16)  # a FRI close to year end and holidays
        assert self.cal.networkdays(date1, date1) == 1
        assert self.cal.networkdays(date1, date(2011, 12, 17)) == 1
        assert self.cal.networkdays(date1, date(2011, 12, 18)) == 1
        assert self.cal.networkdays(date1, date(2011, 12, 19)) == 1

    def test_nextworkday(self):
        assert self.cal.nextworkday(date(2011, 12, 16)) == date(2012, 1, 9)

    def test_plus(self):
        start = date(2011, 12, 19)
        end = self.base.plus(start, timedelta(days=21))
        assert end is not None

    def test_prevworkday(self):
        assert self.cal.prevworkday(date(2012, 1, 9)) == date(2011, 12, 16)

    def test_range(self):
        r = list(self.base.range(date(2012, 1, 2), date(2012, 1, 6)))
        assert len(r) == 4

    def test_setworktime(self):
        c = WorkCalendar()
        c.setworktime([9, 17])
        assert c.worktime(date(2020, 1, 1)) == (time(9, 0), time(17, 0))

    def test_workdatetime(self):
        assert self.cal.workdatetime(date(2012, 1, 9)) is not None

    def test_workday(self):
        date1 = date(2011, 12, 16)  # a FRI close to year end and holidays
        date2 = date(2012, 1, 9)  # a MON close to next year begin
        assert self.cal.networkdays(date1, date2) == 2
        assert self.cal.workday(date1, 1) == date2
        assert self.cal.workday(date2, -1) == date1

    def test_workdays(self):
        days = list(self.cal.workdays(date(2011, 12, 16), 2))
        assert len(days) == 3

    def test_worktime(self):
        assert self.cal.worktime(date(2012, 1, 9)) == (time(8, 0), time(16, 0))


class TestWorkday:
    def test_workday(self):
        pass  # tested above


class TestNetworkdays:
    def test_networkdays(self):
        assert networkdays(date(2020, 1, 6), date(2020, 1, 10)) == 5

