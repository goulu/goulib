__author__ = "Marc Nicole"
__copyright__ = "Copyright 2015, Marc Nicole"
__credits__ = [""]
__license__ = "LGPL"

from pint import UnitRegistry  # https://pypi.python.org/pypi/Pint/
from inspect import isfunction, getsource

# defines V as a way to express any physical value (and Currency)
ureg = UnitRegistry()
V = ureg.Quantity


def magnitudeIn(self, unit):
    return self.to(unit).magnitude


V.__call__ = magnitudeIn


class Row():
    """
    a Raw is internally a dict of {'colname1':value,'colname2',value...}

    """

    def __init__(self, row):  # row has the same format as internal
        self.row = row

    def __getitem__(self, col):
        try:
            v = self.row[col]
            if isfunction(v):  # in that case, one must resolve the calculation
                v = v()
            return v
        except KeyError:
            return None

    def __setitem__(self, col, value):
        self.row[col] = value

    def isfunc(self, col):
        try:
            return isfunction(self.row[col])
        except KeyError:
            return False

    def _repr_html_(self, col, convertToUnits='', withoutUnits=False):
        if self.isfunc(col):
            c = self.row[col]
            background = 'background-color: #f1f1c1;'
            title = 'title="'+getsource(c)+'"'
        else:
            background = ''
            title = ''

        try:
            disp = self[col] if convertToUnits == '' else self[col].to(
                convertToUnits)
            if withoutUnits:
                return '<td colspan=2 style="text-align:right;'+background+'" '+title+'>%f</td>' % disp.magnitude
            else:
                return '<td style="text-align:right;'+background+'" '+title+'>%f</td><td>%s</td>' % (disp.magnitude, disp.units)
        except Exception as e:
            return '<td colspan=2 style="background-color:#ffe5e5;" title="'+str(e)+'">'+str(self[col])+'</td>'


class Table():
    """To create a table, use the following syntax::

        t = Table('myTable', ['col1', 'col2', 'col3'],
                  ['distance', V(20, 'm'), V(30, 'm'), V(40, 'm'),
                   ('speed', 'm/s'), V(2, 'm/min'), V(5, 'm/s'), V(10, 'inch/s')
                  ])

    The row label can be a tuple of ('label', 'unit'). In that case, all the values of the row will be converted to 'unit' (if possible) and the cells won't display the units saving space.
    In the future, the label could be replaced by a dictionary having more properties like:
    ``{'label': <label>, 'comment': <comment>...}``

    Internally, the rows are represented as::

        {'<the label>': {'col1': <value>, 'col2': <value>...},
         '<the next label>'...}
    """

    def __init__(self, name, cols, cells):
        if isinstance(name, tuple):
            self.name = name[0]
            self.defaultUnits = name[1]
        else:
            self.name = name
            self.defaultUnits = ''
        self.cols = []
        self.colUnits = {}
        self.rows = {}
        self.rowUnits = {}
        self.rowLabels = []  # in order to keep the natural order of the table
        self.format = format

        for c in cols:
            if isinstance(c, tuple):
                unit = c[1]
                c = c[0]
                self.colUnits[c] = unit
            self.cols.append(c)

        i = iter(cells)
        tableOk = False  # just here to check consistency of rows
        try:
            while True:
                tableOk = True
                label = next(i)
                if isinstance(label, tuple):
                    unit = label[1]
                    label = label[0]
                    self.rowUnits[label] = unit
                self.rowLabels.append(label)
                row = {}
                tableOk = False
                for col in cols:
                    row[col] = next(i)
                self.rows[label] = Row(row)
                tableOk = True
        except StopIteration:
            if not tableOk:
                raise Exception(
                    'the cells array has inconsistent number of cells regarding the number of columns passed in cols')

    def setCell(self, row, col, value):
        if isinstance(row, tuple):
            self.rowUnits[row[0]] = row[1]
            row = row[0]
        if isinstance(col, tuple):
            self.colUnits[col[0]] = col[1]
            col = col[0]

        if row not in self.rowLabels:
            self.rowLabels.append(row)
            self.rows[row] = Row({})
        if col not in self.cols:
            self.cols.append(col)
        self.rows[row][col] = value

    def __getitem__(self, key):
        return self.rows[key]

    def _repr_html_(self):
        html = '<table border="1"><caption> '+self.name + \
            ' '+self.defaultUnits+'</caption><tr><th></th>'
        for col in self.cols:
            unit = ' ['+self.colUnits[col]+']' if col in self.colUnits else ''
            html += '<th colspan="2">'+col+unit+'</th>'
        html += '</tr><tr>'
        for label in self.rowLabels:
            if label in self.rowUnits:
                units = self.rowUnits[label]
                html += '<td>'+label+'['+units+']</td>'
            else:
                units = self.defaultUnits
                html += '<td>'+label+'</td>'
            r = self.rows[label]
            for col in self.cols:
                noUnits = False
                if label in self.rowUnits:
                    units = self.rowUnits[label]
                    noUnits = True
                if col in self.colUnits:
                    units = self.colUnits[col]
                    noUnits = True
                html += r._repr_html_(col, convertToUnits=units,
                                      withoutUnits=noUnits)
            html += '</tr>'
        html += '</table>'
        return html

    def appendCol(self, colname, values):
        """ appends a column at the right of the table
            :parameter values: is a dict of {<row>:V(...),...}
        """
        self.cols.append(colname)
        for rowname in values:
            self.rows[rowname][colname] = values[rowname]

    def appendRow(self, label, values, unit=None,):
        """ appends a new row of data
        :params label: the label of the row
        :params values: an array of values. must be the same size as ne number of columns of the table
        :params unit: if specified, the unit that will be used to display the row
        """
        assert len(values) == len(self.cols), "the values array has {} elements and the table has {} columns".format(
            len(values), len(self.cols))
        self.rowLabels.append(label)
        r = {self.cols[i]: values[i] for i in range(len(values))}
        self.rows[label] = Row(r)
        if unit:
            self.rowUnits[label] = unit

    def appendColFromObj(self, colname, obj, default=None):
        """ add a new column by searching in obj all properties that have the same name as the row names
            if a row is not found, then the default is used"""
        values = {}
        for label in self.rowLabels:
            v = getattr(obj, label, default)
            values[label] = v
        self.appendCol(colname, values)


class View():
    def __init__(self, table, rows=[], cols=[], rowUnits={}, name=''):
        self.table = table
        self.rows = rows if rows != [] else table.rowLabels
        self.name = name if name != '' else table.name

        if cols == []:
            self.cols = table.cols
        else:
            self.cols = cols
        self.rowUnits = rowUnits

    def _repr_html_(self):
        html = '<table border="1"><caption> '+self.name+'</caption><tr><th></th>'
        for col in self.cols:
            html += '<th colspan="2">'+col+'</th>'
        html += '</tr><tr>'
        for row in self.rows:
            if row in self.rowUnits:
                units = self.rowUnits[row]
                html += '<td>'+row+'['+units+']</td>'
            else:
                units = ''
                html += '<td>'+row+'</td>'
            r = self.table.rows[row]
            for col in self.cols:
                html += r._repr_html_(col, convertToUnits=units,
                                      withoutUnits=row in self.rowUnits)
            html += '</tr>'
        html += '</table>'
        return html
