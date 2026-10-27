from goulib.tests import *
from goulib.table import *
import datetime
import os
import operator


class TestTable:

    @classmethod
    def setup_class(self):
        self.path = os.path.dirname(os.path.abspath(__file__))

        # test reading an Excel file
        # from http://www.contextures.com/xlSampleData01.html
        self.table = Table(self.path+'/data/test.xls')
        assert self.table.titles == ['OrderDate', 'Région', 'Rep', 'Item', 'Unités', 'Cost', 'Total']

        # format some columns
        self.table.applyf('Cost', float)
        self.table.applyf('Total', lambda x: float(x) if isinstance(
            x, (int, float)) else float(x.replace(',', '')))

        # converts using fmts in sequence
        self.table.to_date('OrderDate', fmt=['%m/%d/%Y', 'Excel'])
        assert self.table[0][0] == datetime.date(2012, 6, 1)
        assert self.table[1][0] == datetime.date(2012, 1, 23)

        # add a column to test timedeltas
        d = self.table.col('OrderDate')
        d = list(map(operator.sub, d, [d[0]]+d[:-1]))
        self.table.addcol('timedelta', d)

    def setup_method(self):
        # reset table to initial state
        self.t=Table(self.table)

    def test___init__(self):
        # most tests are above, but some more are here:
        # lists or tuples can be used
        t1 = Table(([1, 2], (3, 4)))
        t2 = Table([(1, 2), [3, 4]])
        assert t1 == t2
        # check Table is mutable even if instantiated with tuples
        t2[0][0] = 2
        assert t1 != t2
        # and also generators, even for a single column
        assert Table((i for i in range(10))) == Table((range(10)))

    def test___repr__(self):
        assert 'Table' in repr(self.t)

    def test___str__(self):
        assert str(self.t) is not None

    def test_applyf(self):
        self.t.applyf('Unités', int)
        assert isinstance(self.t[0, 'Unités'], int)

    def test_read_csv(self):
        # test that t can be written to csv, then re-read in t2 without loss
        self.t.save(self.path+'/results/table/test.csv')

        t = Table(self.path+'/results/table/test.csv')
        t.to_date('OrderDate')
        t.to_timedelta('timedelta')
        assert t == self.t

    def test_write_csv(self):
        pass  # tested in test_read_csv

    def test_write_json(self):

        self.t.save(self.path+'/results/table/test.json', indent=True)
        t = Table(titles=self.t.titles)  # to keep column order
        t.load(self.path+'/results/table/test.json')
        t.to_date('OrderDate')
        t.to_timedelta('timedelta')
        assert t == self.t

    def test_read_xls(self):
        pytest.skip("tested in setup")

    def test_write_xlsx(self):
        self.t.save(self.path+'/results/table/test.xlsx')

    def test_to_date(self):
        pytest.skip("tested in setup and test_html")

    def test_to_datetime(self):
        pytest.skip("tested in setup")

    def test_html(self):

        t = self.t.save(self.path+'/results/table/test.htm')

        t = Table(self.path+'/results/table/test.htm')
        assert t._i('OrderDate') == 0  # check the column exists

        t.to_date('OrderDate')
        t.to_timedelta('timedelta')
        assert t == self.t

        # a table with objects in cells
        from goulib.stats import Normal
        t = Table(titles=['A', 'B'], data=[[Normal(), 2], [3, 'last']])
        h = t.html()
        assert h

        # table with LaTex should not convert r'\right' in '\r ight'
        # and should add extra $$ to avoid line wraps in cells
        cell = r'${\left(x\right)}$'
        t = Table([[cell]])
        h = t.html()
        import re
        assert re.match('<table.*><tr.*><td.*>' +re.escape('$'+cell+'$')+'</td></tr>\n</table>\n',h)

    def test_append(self):
        ta = Table()
        ta.append({'col1': 1, 'col2': 2})
        assert len(ta) == 1 and ta.ncols() == 2
        ta.append([3, 4])
        assert len(ta) == 2 and ta.ncols() == 2

    def test_col(self):
        assert self.t.col('Cost') == self.t[:, 'Cost']

    def test_sort(self):
        self.t.sort('Cost')
        col = self.t.col('Cost')
        assert col[0] == 1.29
        assert col[-1] == 275

    def test_ncols(self):
        assert self.t.ncols() == 8

    def test_setcol(self):
        pass  # tested by test_addcol

    def test_addcol(self):
        t = Table(self.t)
        n = len(t)
        t.addcol('Discount', 0.15, 4)
        assert len(t) == n  # check we don't change the lines
        assert t.ncols() == 9

    def test_find_col(self):
        assert self.t.find_col('Date') == self.t._i('OrderDate')

    def test_get(self):
        assert self.t.get(3, 'Cost') == self.t[3, 5]
        assert self.t.get(-1, 'Total') == 139.72

    def test_groupby(self):
        d = self.t.groupby('Région')
        assert sum([len(d[k]) for k in d]) == len(self.t)
        assert len(d['East']) == 13

    def test___eq__(self):
        t1 = Table([[1, 2], [3, 4]], titles=['A', 'B'])
        t2 = Table([[1, 2], [3, 4]], titles=['A', 'B'])
        assert t1 == t2
        assert t1 != Table([[1, 2], [3, 5]], titles=['A', 'B'])

    def test_hierarchy(self):
        t = Table([
            [1, 'Root'],
            [2, 'Child 1'],
            [2, 'Child 2'],
        ], titles=['Level', 'Name'])
        h = t.hierarchy()
        assert h is not None

    def test_icol(self):
        col_vals = list(self.t.icol('Rep'))
        assert len(col_vals) == len(self.t)
        assert col_vals[0] == 'Jones'

    def test_read_element(self):
        pass  # tested via html reading

    def test_read_html(self):
        t = Table(self.path+'/results/table/test.htm')
        assert len(t) > 0

    def test_remove_lines_where(self):
        import copy
        t = copy.deepcopy(self.t)  # so we can play with it
        i = t._i('Rep')
        l = len(t)
        r = t.remove_lines_where(lambda line: line[i] == 'Jones')
        assert r == 8
        assert len(t) == l-r

    def test_rowasdict(self):
        r = self.t.rowasdict(6)
        assert r == {'Cost': 1.99,
                     'Item': 'Pencil',
                     'OrderDate': date(2012, 4, 18),
                     'Rep': 'Andrews',
                     'Région': 'Central',
                     'Total': 149.25,
                     'Unités': 75,
                     'timedelta': timedelta(days=105)}

    def test_set(self):
        self.t.set(0, 'Cost', 99.99)
        assert self.t.get(0, 'Cost') == 99.99

    def test_total(self):
        tot = self.t.total([None, None, None, None, sum])
        assert tot is not None

    def test_index(self):
        idx = self.t.index('Jones', 'Rep')
        assert idx == 0
        assert self.t.index('NonExistent', 'Rep') is None

    def test_transpose(self):
        t = self.t.transpose()
        assert t[1, 1] == 'Jones'

    def test___getitem__(self):
        assert self.t[0] is not None
        assert self.t[0, 0] is not None
        assert len(self.t[0:3, 'Rep']) == 3

    def test_asdict(self):
        dicts = list(self.t.asdict())
        assert len(dicts) == len(self.t)
        assert 'Rep' in dicts[0]

    def test_cols(self):
        cols = list(self.t.cols())
        assert len(cols) == self.t.ncols()

    def test_groupby_gen(self):
        groups = list(self.t.groupby_gen('Région'))
        assert len(groups) > 0

    def test_json(self):
        js = self.t.json()
        assert 'OrderDate' in js

    def test_load(self):
        t = Table()
        t.load(self.path+'/results/table/test.csv')
        assert len(t) == len(self.t)

    def test_read_json(self):
        t = Table()
        t.read_json(self.path+'/results/table/test.json')
        assert len(t) == len(self.t)

    def test_save(self):
        pass  # already tested in write_csv, write_json, write_xlsx

    def test_to_time(self):
        t = Table([['12:30:00']], titles=['T'])
        t.to_time('T')
        assert isinstance(t[0, 0], time)

    def test_to_timedelta(self):
        t = Table([['1 day, 0:00:00']], titles=['TD'])
        t.to_timedelta('TD')
        assert isinstance(t[0, 0], timedelta)


class TestAttr:
    def test_attr(self):
        res = attr({'_class': 'myclass', 'id': 'myid'})
        assert 'class="myclass"' in res
        assert 'id="myid"' in res


class TestCell:
    def test___init__(self):
        c = Cell('test', align='left', fmt='{}', style={'color': 'red'})
        assert c.data == 'test'
        assert c.align == 'left'

    def test___repr__(self):
        c = Cell('hello')
        assert repr(c) is not None
        assert c.data == 'hello'

    def test_html(self):
        c = Cell('val', style={'font-weight': 'bold'})
        h = c.html()
        assert '<td' in h
        assert 'val' in h

    def test_read(self):
        assert Cell.read('123') == 123
        assert Cell.read('12.5') == 12.5
        assert Cell.read('text') == 'text'


class TestRow:
    def test___init__(self):
        r = Row([1, 2, 3], tag='th')
        assert len(r.data) == 3
        assert r.data[0].tag == 'th'

    def test___repr__(self):
        r = Row([1, 2])
        assert repr(r) is not None

    def test_html(self):
        r = Row(['a', 'b'])
        h = r.html()
        assert '<tr' in h
        assert '<td' in h

