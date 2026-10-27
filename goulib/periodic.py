'''
periodic functions

! work in progress, not tested yet !
'''

__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2025, Philippe Guglielmetti"
__license__ = "LGPL"

import math
from . import math2
from .expr import Expr

Period = tuple[float,float]
class Periodic(Expr):
    '''
    periodic function defined by an Expr and a period
    '''
    _period:Period
    _expr:Expr
    def __init__(self, f:Expr, period:Period):
        '''constructor
        :param f: Expr
        :param period: Period (start, end) for periodicity'''
        self._expr = f
        if math2.is_number(period):
            period = (0, period)
        self._period = period

        # to initialize context and such stuff
        super(Periodic, self).__init__(0)
        self.body =None  # should not be used

    def period(self)->float:
        if math.isinf(self._period[1]):
            return 0
        return self._period[1] - self._period[0]

    def _str_period(self):
        p = self.period()
        return ", period=%s" % p if p else ""
    
    def __str__(self):
        return str(self._expr) + self._str_period()

    def __repr__(self):
        return repr(self._expr) + self._str_period()

    def __call__(self, x):
        x = (x - self._period[0]) % (self._period[1] - self._period[0]) + self._period[0]
        return self._expr(x)
    
    def apply(self, f, right=None)->'Periodic':
        '''function composition self o f = f(self(x))
        overrides Expr.apply
        :param f: function to apply
        :param right: optional second argument for f
        :return: a new Periodic object'''
        return Periodic(self._expr.apply(right), self._period)

    def applx(self, f, var='x') -> 'Periodic':
        '''function composition f o self = self(f(x))
        overrides Expr.apply
        :param f: function to apply
        :param var: string variable name
        :return: a new Periodic object'''
        return Periodic(self._expr.applx(f,var), self._period)
