"""
simple manipulation of polynomials (without SimPy)
see http://docs.sympy.org/dev/modules/polys/reference.html if you need more ...
"""

__author__ = "Rick Muller + Philippe Guglielmetti"
__copyright__ = "Copyright 2013, Philippe Guglielmetti"
__credits__ = [
    "http://code.activestate.com/recipes/362193-manipulate-simple-polynomials-in-python/"]
__license__ = "LGPL"

import re

from . import expr


class Polynomial(expr.Expr):
    def __init__(self, val):
        """
        :param val: can be:

            - an iterable of the factors in ascending powers order : Polynomial([1,2,3]) holds 3*x^2+2*x+1
            - a string of the form "ax^n + b*x^m + ... + c x + d" where a,b,c,d, are floats and n,m ... are integers 
              the 'x' variable name is fixed, and the spaces and '*' chars are optional.
              terms can be in any order, and even "overlap" : Polynomial('3x+x^2-x') holds x^2+2*x
        """
        self.plist = tuple(plist(val))  # a polynomial is immutable
        s = tostring(self.plist, pow='**', mul='*')
        super(Polynomial, self).__init__(s)

    """
    def __str__(self):
        ''':return: the best string we can for text output'''
        return tostring(self.plist)
    
    def __repr__(self):
        ''':return: a string we can cut/paste in a calculator'''
        return tostring(self.plist,mul='*')
    """

    def _latex(self, **kwargs):
        return tostring(self.plist, **kwargs)

    def __lt__(self, other):
        try:
            other = other.plist
        except:
            other = Polynomial(other).plist
        if len(other) < len(self.plist):
            return False
        if len(other) > len(self.plist):
            return True
        # compare the coefficients by decreasing degree
        for i in range(len(self.plist) - 1, -1, -1):
            if self.plist[i] < other[i]:
                return True
            elif self.plist[i] > other[i]:
                return False
        return False  # equality

    def __eq__(self, other):
        try:
            return self.plist == other.plist
        except:
            return self.plist == Polynomial(other).plist

    def __add__(self, other):
        return Polynomial(add(self.plist, plist(other)))

    def __radd__(self, other):
        return Polynomial(add(self.plist, plist(other)))

    def __sub__(self, other):
        return Polynomial(sub(self.plist, plist(other)))

    def __rsub__(self, other):
        return -Polynomial(sub(self.plist, plist(other)))

    def __mul__(self, other):
        return Polynomial(multiply(self.plist, plist(other)))

    def __rmul__(self, other):
        return Polynomial(multiply(self.plist, plist(other)))

    def __neg__(self):
        return -1 * self

    def __pow__(self, e):
        return Polynomial(power(self.plist, e))

    def integral(self):
        return Polynomial(integral(self.plist))

    def derivative(self):
        return Polynomial(derivative(self.plist))


# Define some simple utility functions. These manipulate "plists", polynomials
#  that are stored as python lists. Thus, 3x^2 + 2x + 1 would be stored
#  as [1,2,3] (lowest to highest power of x, even though polynomials
#  are typically written from highest to lowest power).

def plist(term):
    "Force term to have the form of a polynomial list"

    try:  # already a Polynomial ?
        return term.plist
    except:
        pass

    try:  # a string ?
        return parse_string(term)
    except:
        pass

    try:  # a list of coeffcients ?
        term[0]
        return term
    except:
        pass
    return [term]  # then it's a constant


def peval(plist, x, x2=None):
    """\
    Eval the plist at value x. If two values are given, the
    difference between the second and the first is returned. This
    latter feature is included for the purpose of evaluating
    definite integrals.
    """
    val = 0
    if x2:
        for i in range(len(plist)):
            val += plist[i] * (pow(x2, i) - pow(x, i))
    else:
        for i in range(len(plist)):
            val += plist[i] * pow(x, i)
    return val


def integral(plist):
    """
    Return a new plist corresponding to the integral of the input plist.
    This function uses zero as the constant term, which is okay when
    evaluating a definite integral, for example, but is otherwise
    ambiguous.
    """
    if not plist:
        return []
    new = [0]
    for i in range(len(plist)):
        c = plist[i] / (i + 1.)
        if c == int(c):
            c = int(c)  # attempt to cast back to int
        new.append(c)
    return new


def derivative(plist):
    """
    Return a new plist corresponding to the derivative of the input plist.
    """
    new = []
    for i in range(1, len(plist)):
        new.append(i * plist[i])
    if not new:
        new = [0]
    return new


def add(p1, p2):
    "Return a new plist corresponding to the sum of the two input plists."
    if len(p1) > len(p2):
        new = [i for i in p1]
        for i in range(len(p2)):
            new[i] += p2[i]
    else:
        new = [i for i in p2]
        for i in range(len(p1)):
            new[i] += p1[i]
    return new


def sub(p1, p2):
    return add(p1, mult_const(p2, -1))


def mult_const(p, c):
    "Return a new plist corresponding to the input plist multplied by a const"
    return [c * pi for pi in p]


def multiply(p1, p2):
    "Return a new plist corresponding to the product of the two input plists"
    if len(p1) > len(p2):
        short, f = p2, p1
    else:
        short, f = p1, p2
    new = []
    for i in range(len(short)):
        new = add(new, mult_one(f, short[i], i))
    return new


def mult_one(p, c, i):
    """\
    Return a new plist corresponding to the product of the input plist p
    with the single term c*x^i
    """
    new = [0] * i  # increment the list with i zeros
    for pi in p:
        new.append(pi * c)
    return new


def power(p, e):
    "Return a new plist corresponding to the e-th power of the input plist p"
    assert int(e) == e, "Can only take integral power of a plist"
    new = [1]
    for i in range(e):
        new = multiply(new, p)
    return new


def parse_string(s):
    """\
    Do very, very primitive parsing of a string into a plist.
    'x' is the only term considered for the polynomial, and this
    routine can only handle terms of the form:
    7x^2 + 6x - 5
    and will choke on seemingly simple forms such as
    x^2*7 - 1
    or
    x**2 - 1
    """
    s = s.replace('$', '').replace(
        '*', '')  # remove LateX marks and optional * mul symbols
    termpat = re.compile(r'([-+]?\s*\d*\.?\d*)(x?\^?\d?)')
    # print "Parsing string: ",str
    # print termpat.findall(str)
    res_dict = {}
    for n, p in termpat.findall(s):
        n, p = n.strip(), p.strip()
        if not n and not p:
            continue
        n, p = _parse_n(n), _parse_p(p)
        if p in res_dict:
            res_dict[p] += n
        else:
            res_dict[p] = n
    highest_order = max(res_dict.keys())
    res = [0] * (highest_order + 1)
    for key, value in list(res_dict.items()):
        res[key] = value
    return res


def _parse_n(str):
    "Parse the number part of a polynomial string term"
    if not str:
        return 1
    elif str == '-':
        return -1
    elif str == '+':
        return 1
    return eval(str)


def _parse_p(str):
    "Parse the power part of a polynomial string term"
    pat = re.compile(r'x\^?(\d)?')
    if not str:
        return 0
    res = pat.findall(str)[0]
    if not res:
        return 1
    return int(res)


def _strip_leading_zeros(p):
    "Remove the leading (in terms of high orders of x) zeros in the polynomial"
    # compute the highest nonzero element of the list
    for i in range(len(p) - 1, -1, -1):
        if p[i]:
            break
    return p[:i + 1]


def tostring(p, **kwargs):
    """\
    Convert a plist into a string. This looks overly complex at first,
    but most of the complexity is caused by special cases.
    """
    p = _strip_leading_zeros(p)
    str = []
    for i in range(len(p) - 1, -1, -1):
        if p[i]:
            if i < len(p) - 1:
                if p[i] >= 0:
                    str.append(kwargs.get('plus', '+'))
                else:
                    str.append(kwargs.get('minus', '-'))
                str.append(_tostring_term(abs(p[i]), i, **kwargs))
            else:
                str.append(_tostring_term(p[i], i, **kwargs))
    if not str:
        str = '0'
    return ' '.join(str)


def _tostring_term(c, i, **kwargs):
    "Convert a single coefficient c and power e to a string cx^i"
    if i == 0:
        return str(c)
    res = kwargs.get('x', 'x')
    if c == -1:
        res = kwargs.get('minus', '-') + res
    elif c != 1:
        # by default there is no multiplication sign
        res = str(c) + kwargs.get('mul', '') + res
    if i != 1:
        res = res + kwargs.get('pow', '^') + str(i)
    return res
