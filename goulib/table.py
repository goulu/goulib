"""
"mini pandas.DataFrame"
Table class with Excel + CSV I/O, easy access to columns, HTML output, and much more.
"""
__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2013, Philippe Guglielmetti"
__credits__ = []
__license__ = "LGPL"


import csv
import itertools
import json
from typing import OrderedDict

from datetime import datetime, date, time, timedelta

from . import itertools2, markup, datetime2

from lxml import etree as ElementTree
defaultparser = ElementTree.HTMLParser
Element = ElementTree._Element


def attr(args):
    res = ''
    for key, val in args.items():
        k = "class" if key == "_class" else key
        res += ' %s="%s"' % (k, val)
    return res


class Cell(object):
    """Table cell with HTML attributes"""

    def __init__(self, data=None, align=None, fmt=None, tag=None, style={}):
        """
        :param data: cell value(s) of any type
        :param align: string for HTML align attribute
        :param fmt: format string applied applied to data
        :param tag: called to build each cell. defaults to 'td'
        :param style: dict or string for HTML style attribute
        """

        if isinstance(data, Element):
            tag = data.tag
            assert (tag in ('td', 'th'))

            def _recurse(data):
                "grab all possible text from the cell content"
                if data is None:
                    return ''
                s = ''.join(_recurse(x) for x in data.getchildren())
                if data.text:
                    s = data.text+s
                if data.tail:
                    s = s+data.tail
                return s

            data = Cell.read(_recurse(data))

        if isinstance(data, str):
            data = data.lstrip().rstrip()  # remove spaces, but also trailing \r\n

        self.data = data
        self.align = align
        self.fmt = fmt
        self.tag = tag if tag else 'td'
        if not isinstance(style, dict):
            style = markup.style_str2dict(style)
        self.style = style

    def __str__(self):
        return str(self.data)

    def _repr_html_(self):
        return self.html()

    @staticmethod
    def read(x):
        """interprets x as int, float, string or None"""
        try:
            x = float(x)  # works for x in unicode
            xi = int(x)  # does not work if x is floating point in unicode (?)
            if xi == x:
                x = xi
        except:
            if x == '':
                x = None
        return x

    def html(self, **kwargs):
        """:return: string HTML formatted cell:

        * if data is int, default align="right"
        * if data is float, default align="right" and fmt='%0.2f'
        * if data is :class:`~datetime.timedelta`, align = "right" and formatting is done by :func:`datetime2.strftimedelta`

        """
        args = {}
        args.update(kwargs)  # copy needed to avoid side effects

        v = self.data
        f = self.fmt

        style = args.get('style', {})
        if isinstance(style, str):
            style = markup.style_str2dict(style)

        # create style dict by merging default Cell style + parameters
        # http://stackoverflow.com/questions/9819602/union-of-dict-objects-in-python
        style = dict(self.style, **style)

        if hasattr(v, '_repr_html_'):
            try:
                v = v._repr_html_()
            except Exception as e:
                v = 'ERROR : %s _repr_html_ failed : %s' % (v, e)

        elif 'text-align' not in style:  # HTML 4 and before
            a = args.pop('align', self.align)
            if isinstance(v, int):
                if not a:
                    a = "right"
            elif isinstance(v, float):
                if not a:
                    a = "right"
                if not f:
                    f = '%0.2f'
                v = f % v
                f = None  # don't reformat below
            elif isinstance(v, date):
                if not a:
                    a = "right"
                if not f:
                    f = '%Y-%m-%d'
                v = v.strftime(f)
                f = None  # don't reformat below
            elif isinstance(v, timedelta):
                if not a:
                    a = "right"
                if not f:
                    f = '%H:%M:%S'
                v = datetime2.strftimedelta(v, f)
                f = None  # don't reformat below

            if a:
                style['text-align'] = a

        if v is None or v == '':
            v = "&nbsp;"  # for IE8
        else:
            v = f % v if f else str(v)

        if v[0] == '$' and v[-1] == '$':  # LaTeX formula : avoid line wrap
            v = '$'+v+'$'

        if style:
            args['style'] = style

        return markup.tag(self.tag, v, **args)


class Row(object):
    """Table row with HTML attributes"""

    def __init__(self, data, align=None, fmt=None, tag=None, style={}):
        """
        :param data: (list of) cell value(s) of any type
        :param align: (list of) string for HTML align attribute
        :param fmt: (list of) format string applied applied to data
        :param tag: (list of) tags called to build each cell. defaults to 'td'
        :param style: (list of) dict or string for HTML style attribute
        """

        if not itertools2.isiterable(data):
            data = [data]
        data = list(data)  # to make it mutable

        # ensure params have the same length as data

        if not isinstance(style, list):
            style = [style]
        style = style+[None]*(len(data)-len(style))

        if not isinstance(align, list):
            align = [align]
        align = align+[None]*(len(data)-len(align))

        if not isinstance(fmt, list):
            fmt = [fmt]
        fmt = fmt+[None]*(len(data)-len(fmt))

        if not tag:
            tag = 'td'
        if not isinstance(tag, list):
            tag = [tag]*(len(data))  # make a full row, in case it's a 'th'
        # fill the row with None, which will be 'td's
        tag = tag+[None]*(len(data)-len(fmt))

        for i, cell in enumerate(data):
            if not isinstance(cell, Cell):
                cell = Cell(cell, align[i], fmt[i], tag[i], style[i])
            else:
                pass  # ignore attribs for now
            data[i] = cell

        self.data = data

    def __str__(self):
        return str(self.data)

    def _repr_html_(self):
        return self.html()

    def html(self, cell_args={}, **kwargs):
        """return in HTML format"""
        res = ''
        for cell in self.data:
            res += cell.html(**cell_args)
        return markup.tag('tr', res, **kwargs)


class Table(list):
    """Table class with CSV I/O, easy access to columns, HTML output"""

    def __init__(self, data=[], **kwargs):
        """inits a table, optionally by reading a Excel, csv or html file
        :param data: list of list of cells, or string as filename
        :param titles: optional list of strings used as column id
        :param footer: optional list of functions used as column reducers
        """
        try:
            self.titles = data.titles
        except AttributeError:
            self.titles = kwargs.pop('titles', [])
        try:
            self.footer = data.footer
        except AttributeError:
            self.footer = kwargs.pop('footer', [])

        filename = None
        if isinstance(data, str):
            filename = data
            data = []
        else:  # ensure data is 2D and mutable
            if isinstance(data, dict):
                data = data.values()
            for row in data:
                if not itertools2.isiterable(row):  # build a column
                    row = [row]
                self.append(row)

        if filename:
            self.load(filename, **kwargs)

    def __repr__(self):
        """:return: repr string of titles+5 first lines"""
        return '%s(len=%d,titles=%s,data=%s)' % (self.__class__, len(self), self.titles, self[:5])

    def __str__(self):
        """:return: string of full tables with linefeeds"""
        res = ''
        if self.titles:
            res += str(self.titles)+'\n'
        for line in self:
            res += str(line)+'\n'
        return res

    def _repr_html_(self):
        return self.html()

    def html(self, head=None, foot=None, **kwargs):
        """HTML representation of table

        :param head: optional column headers, .titles by default
        :param foot: optional column footers, .footer by default
        :param style: style for the table
        :param colstyle: list of dict of style attributes for each column
        :param kwargs: optional parameters passed along to tag('table'...
            except:
            * start=optional start row
            * stop=optional end row
            used to display a subset of lines. in this case rows with '...' cells
            are displayed before and/or after the lines
        :return: string HTML representation of table
        """

        def TR(data, align=None, fmt=None, tag=None, style={}):
            res = ''
            row = Row(data=data, align=align, fmt=fmt, tag=tag, style=style)
            res += row.html()+'\n'
            return res

        def THEAD(data, fmt=None, style={}):
            res = "<thead>\n"
            res += TR(data=data, fmt=fmt, tag='th', style=style)
            res += "</thead>\n"
            return res

        def TFOOT(data, fmt=None, style={}):
            res = "<tfoot>\n"
            res += TR(data=data, fmt=fmt, tag='th', style=style)
            res += "</tfoot>\n"
            return res

        res = ''

        colstyle = kwargs.pop('colstyle', None)

        if head is None:
            head = self.titles
        if head:
            res += THEAD(head)
        start = kwargs.pop('start', 0)
        stop = kwargs.pop('stop', len(self))
        if start != 0:
            res += TR(['...']*self.ncols(), style=colstyle)
        for row in self[start:stop]:
            res += TR(row, style=colstyle)
        if stop != -1 and stop < len(self):
            res += TR(['...']*self.ncols(), style=colstyle)
        if foot is None:
            foot = self.footer
        if foot:
            res += TFOOT(foot)

        # kwargs['style'] = kwargs.pop('style', {'table-layout': 'fixed'})  # to prevent wrapping

        return markup.tag('table', res, **kwargs)+'\n'

    def load(self, filename, **kwargs):
        if self.titles:  # explicitly set
            l = kwargs.setdefault('titles_line', 0)
            kwargs.setdefault('data_line', l+1)
        else:  # read titles from the file
            l = kwargs.setdefault('titles_line', 1)
            kwargs.setdefault('data_line', l+1)
        ext = filename.split('.')[-1].lower()
        if ext in ('xls', 'xlsx'):
            self.read_xls(filename, **kwargs)
        elif ext in ('htm', 'html'):
            self.read_html(filename, **kwargs)
        elif ext in ('json'):
            self.read_json(filename, **kwargs)
        else:  # try ...
            self.read_csv(filename, **kwargs)
        return self  # to allow chaining

    def read_element(self, element, **kwargs):
        """read table from a DOM element.
        :Warning: drops all formatting
        """
        titles_line = kwargs.pop('titles_line', 1)-1
        data_line = kwargs.pop('data_line', 2)-1
        line = 0
        head = element.find('thead')
        if head is not None:
            for row in head.findall('tr'):
                if line == titles_line:
                    self.titles = [cell.data for cell in Row(row).data]
                line = line+1
        body = element.find('tbody')
        if body is None:
            body = element
        for row in body.findall('tr'):
            data = [cell.data for cell in Row(row).data]
            if not data:
                continue  # skip empty lines
            if not self.titles and line == titles_line:
                self.titles = data
            elif line >= data_line:
                self.append(data)
            line = line+1
        return self

    def read_html(self, filename, **kwargs):
        """read first table in HTML file
        """
        parser = kwargs.get('parser', defaultparser)
        element = ElementTree.parse(filename, parser()).getroot()
        try:
            if element.tag != 'table':  # file contains table as topmost tag
                element = element.find('.//table')  # find first table
        except AttributeError:
            pass

        if element is None:
            raise LookupError('no table found in file')

        self.read_element(element, **kwargs)
        return self

    def read_json(self, filename, **kwargs):
        """appends a json file made of lines dictionaries"""
        with open(filename, 'r') as file:
            for row in json.load(file):
                self.append(row)
        return self

    def read_xls(self, filename, **kwargs):
        """appends an Excel table"""
        titles_line = kwargs.pop('titles_line', 1)-1
        data_line = kwargs.pop('data_line', 2)-1

        import xlrd
        wb = xlrd.open_workbook(filename)
        sheet = kwargs.get('sheet', 0)
        if isinstance(sheet, str):
            s = wb.sheet_by_name(sheet)
        else:
            s = wb.sheet_by_index(sheet)

        for i in range(s.nrows):
            line = [Cell.read(s.cell(i, j).value) for j in range(s.ncols)]
            if i == titles_line:
                self.titles = line
            elif i >= data_line:
                self.append(line)
        return self

    def read_csv(self, filename, **kwargs):
        """appends a .csv or similar file to the table"""
        titles_line = kwargs.pop('titles_line', 1)-1
        data_line = kwargs.pop('data_line', 2)-1

        dialect = kwargs.setdefault('dialect', csv.excel)
        delimiter = kwargs.setdefault('delimiter', ';')
        # must be iso-8859-15 in some cases
        encoding = kwargs.pop('encoding', 'utf-8')
        errors = kwargs.pop('errors', 'strict')

        def reader():  # version for Python 3
            with open(filename, 'rt', errors=errors, encoding=encoding) as f:
                csv_reader = csv.reader(f, **kwargs)
                for row in csv_reader:
                    yield row

        for i, row in enumerate(reader()):
            if i == titles_line:  # titles can have no left/right spaces
                self.titles = [Cell.read(x) for x in row]
            elif i >= data_line:
                line = [Cell.read(x) for x in row]
                if line != [None]:  # strange last line sometimes ...
                    self.append(line)
        return self

    def save(self, filename, **kwargs):
        ext = filename.split('.')[-1].lower()
        if ext in ('xls', 'xlsx'):
            self.write_xlsx(filename, **kwargs)
        elif ext in ('htm', 'html'):
            with open(filename, 'w') as file:
                file.write(self.html(**kwargs))
        elif ext in ('json'):
            with open(filename, 'w') as file:
                file.write(self.json(**kwargs))
        else:  # try ...
            self.write_csv(filename, **kwargs)
        return self  # to allow chaining

    def write_xlsx(self, filename, **kwargs):
        import xlsxwriter

        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        df = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        tf = workbook.add_format({'num_format': 'hh:mm:ss'})
        dtf = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm:ss'})

        def writerow(i, line):
            for j, s in enumerate(line):
                if isinstance(s, datetime):
                    worksheet.write_datetime(i, j, s, dtf)
                elif isinstance(s, date):
                    worksheet.write_datetime(i, j, s, df)
                elif isinstance(s, (time, timedelta)):
                    worksheet.write_datetime(i, j, s, tf)
                else:
                    worksheet.write(i, j, s)

        writerow(0, self.titles)
        for i, row in enumerate(self):
            writerow(i+1, row)

        workbook.close()
        return self

    def json(self, **kwargs):
        """
        :return: string JSON representation of table
        """
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            try:
                return str(obj)
            except Exception:
                pass
            raise TypeError("Type %s not serializable" % (type(obj)))
        array = [self.rowasdict(i) for i in range(len(self))]
        kwargs.setdefault('default', json_serial)
        return json.dumps(array, **kwargs)

    def write_csv(self, filename, **kwargs):
        """ write the table in Excel csv format, optionally transposed"""

        dialect = kwargs.get('dialect', 'excel')
        delimiter = kwargs.get('delimiter', ';')
        encoding = kwargs.pop('encoding', 'utf-8')  # was iso-8859-15 earlier
        empty = ''.encode(encoding)

        f = open(filename, 'w', newline='', encoding=encoding)

        def _encode(line):
            res = []
            for s in line:
                res.append(s)
            return res

        writer = csv.writer(f, dialect=dialect, delimiter=delimiter)
        if self.titles:
            s = _encode(self.titles)
            writer.writerow(s)
        for line in self:
            s = _encode(line)
            writer.writerow(s)
        f.close()
        return self

    def __eq__(self, other):
        """compare 2 Tables contents, mainly for tests"""
        if self.titles != other.titles:
            return False
        if len(self) != len(other):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True

    def ncols(self):
        """
        :return: number of columns, ignoring title
        """

        return max(map(len, self))

    def find_col(self, title):
        """finds a column from a part of the title"""
        title = title.lower()
        for i, c in enumerate(self.titles):
            if c.lower().find(title) >= 0:
                return i
        return None

    def _i(self, column):
        '''column index'''
        if isinstance(column, int):
            return column
        try:
            return self.titles.index(column)
        except ValueError:
            return None

    def icol(self, column):
        """iterates a column"""
        i = self._i(column)
        for row in self:
            try:
                yield row[i]
            except Exception:
                yield None

    def col(self, column, title=False):
        i = self._i(column)
        res = [x for x in self.icol(i)]
        if title:
            res = [self.titles[i]]+res
        return res

    def cols(self, title=False):
        """iterator through columns"""
        for i in range(self.ncols()):
            yield self.col(i, title)

    def transpose(self, titles_column=0):
        """transpose table
        :param: titles_column
        :return: Table where rows are made from self's columns and vice-versa
        """
        res = Table()
        for i, row in enumerate(self.cols(self.titles)):
            if i == titles_column:
                res.titles = row
            else:
                res.append(row)
        return res

    def index(self, value, column=0):
        """
        :return: int row number of first line where column contains value
        """
        for i, v in enumerate(self.icol(column)):
            if v == value:
                return i
        return None

    def __getitem__(self, n):
        try:
            c = self._i(n[1])
        except TypeError:
            return super(Table, self).__getitem__(n)
        else:
            rows = super(Table, self).__getitem__(n[0])
            if not isinstance(n[0], slice):
                return rows[c]
            return [row[c] for row in rows]

    def get(self, row, col):
        return self[row, col]

    def set(self, row, col, value):
        col = self._i(col)
        if row >= len(self):
            self.extend([list()]*(1+row-len(self)))
        if col >= len(self[row]):
            self[row].extend([None]*(1+col-len(self[row])))
        self[row][col] = value

    def setcol(self, col, value, i=0):
        """set column values
        :param col: int or string column index
        :param value: single value assigned to whole column or iterable assigned to each cell
        :param i: optional int : index of first row to assign
        """
        j = self._i(col)
        if itertools2.isiterable(value):
            for v in value:
                self.set(i, j, v)
                i += 1
        else:
            for i in range(i, len(self)):
                self.set(i, j, value)

    def append(self, line):
        ''' appends a line to table
        :param line: can be either:
        * a list
        * a dict or column names:values
        '''
        if isinstance(line, dict):
            r = len(self)  # row number
            for k, v in line.items():
                i = self._i(k)
                if i is None:  # column doesn't exist:
                    i = len(self.titles)
                    self.titles.append(k)
                self.set(r, i, v)
        else:
            list.append(self, list(line))
        return self

    def addcol(self, title, val=None, i=0):
        '''add column to the right'''
        col = len(self.titles)
        self.titles.append(title)
        if not itertools2.isiterable(val):
            val = [val]*(len(self)-i)
        for v in val:
            self.set(i, col, v)
            i += 1
        return self

    def sort(self, by, reverse=False):
        '''sort by column'''
        i = self._i(by)
        if isinstance(i, int):
            list.sort(self, key=lambda x: x[i], reverse=reverse)
        else:
            list.sort(i, reverse=reverse)

    def rowasdict(self, i):
        ''' returns a line as a dict '''
        return OrderedDict(zip(self.titles, self[i]))

    def asdict(self):
        for i in range(len(self)):
            yield self.rowasdict(i)

    def groupby_gen(self, by, sort=True, removecol=True):
        """generates subtables
        """
        i = self._i(by)
        t = self.titles
        if removecol:
            t = t[:i]+t[i+1:]
        if sort:
            self.sort(i)
        else:
            pass  # groupby will group CONSECUTIVE lines with same i, so entries at bottom of table will replace the earlier entries in dict
        for k, g in itertools.groupby(self, key=lambda x: x[i]):
            if removecol:
                r = Table(titles=t, data=[a[:i]+a[i+1:] for a in g])
            else:
                r = Table(titles=t, data=list(g))
            yield k, r

    def groupby(self, by, sort=True, removecol=True):
        """ ordered dictionary of subtables
        """
        return OrderedDict(
            (k, t) for (k, t) in self.groupby_gen(by, sort, removecol)
        )

    def hierarchy(self, by='Level',
                  # creates an object from a line
                  factory=lambda row: (row, []),
                  # creates a parend/child relation between x and y. raw is also available (for qty)
                  linkfct=lambda x, y, row: x[1].append(y)
                  ):
        '''builds a structure from a table containing a "level" column'''
        res = []
        i = self._i(by)
        stack = []
        for row in self:
            obj = factory(row)
            level = row[i]
            if level == 1:
                res.append(obj)
            while level <= len(stack):
                stack.pop()
            if stack:
                linkfct(stack[-1], obj, row)
            stack.append(obj)
        return res

    def applyf(self, by, f, skiperrors=False):
        """ apply a function to a column
        :param by: column name of number
        :param f: function of the form lambda cell:content
        :param skiperrors: bool. if True, errors while running f are ignored
        :return: bool True if ok, False if skiperrors==True and conversion failed
        """
        res = True
        i = self._i(by)
        for row in self:
            try:
                x = row[i]
                row[i] = f(x)
            except Exception as e:
                if not skiperrors:
                    # TODO: change message to ('could not applyf to %s'%x) for Py2+3
                    raise
                res = False
        return res

    def _datetimeformat(self, by, fmt, function, skiperrors):
        """convert a column to a date, time or datetime
        :param by: column name of number
        :param fmt: string defining format, or list of formats to try one by one
        :param function: function to call
        :param skiperrors: bool. if True, conversion errors are ignored
        :return: bool True if ok, False if skiperrors==True and conversion failed
        """
        if isinstance(fmt, list):
            for f in fmt:
                res = self._datetimeformat(
                    by, f, function, True if f != fmt[-1] else skiperrors)
            return res
        return self.applyf(by, lambda x: function(x, fmt=fmt), skiperrors)

    def to_datetime(self, by, fmt='%Y-%m-%d %H:%M:%S', skiperrors=False):
        """convert a column to datetime
        """
        return self._datetimeformat(by, fmt, datetime2.datetimef, skiperrors)

    def to_date(self, by, fmt='%Y-%m-%d', skiperrors=False):
        """convert a column to date
        """
        return self._datetimeformat(by, fmt, datetime2.datef, skiperrors)

    def to_time(self, by, fmt='%H:%M:%S', skiperrors=False):
        """convert a column to time
        """
        return self._datetimeformat(by, fmt, datetime2.timef, skiperrors)

    def to_timedelta(self, by, fmt=None, skiperrors=False):
        """convert a column to time
        """
        return self._datetimeformat(by, fmt, datetime2.timedeltaf, skiperrors)

    def total(self, funcs):
        """build a footer row by appling funcs to all columns
        """
        funcs = funcs+[None]*(len(self.titles)-len(funcs))
        self.footer = []
        for i, f in enumerate(funcs):
            try:
                self.footer.append(f(self.col(i)))
            except:
                self.footer.append(f)
        return self.footer

    def remove_lines_where(self, f, value=(None, 0, '')):
        """
        :param f: function of the form lambda line:bool returning True if line should be removed
        :return: int number of lines removed
        """
        i = self._i(f)
        if i is not None:
            f = (lambda x: x[i] in value)
        return len(itertools2.removef(self, f))


if __name__ == "__main__":
    t = Table([[1, 2], [3, 'a 4']], style='width:100%;')
    print(t.html())
