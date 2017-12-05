#!/usr/bin/env python
# coding: utf8
"""
simple symbolic math expressions
"""

__author__ = "Philippe Guglielmetti, J.F. Sebastian, Geoff Reedy"
__copyright__ = "Copyright 2013, Philippe Guglielmetti"
__credits__ = [
    'http://stackoverflow.com/questions/2371436/evaluating-a-mathematical-expression-in-a-string',
    'http://stackoverflow.com/questions/3867028/converting-a-python-numeric-expression-to-latex',
    ]
__license__ = "LGPL"

import six, logging, copy, collections, inspect, re

from . import plot #sets matplotlib backend

from . import itertools2, math2

# http://stackoverflow.com/questions/2371436/evaluating-a-mathematical-expression-in-a-string

import ast
import operator as op

# supported operators with precedence and text + LaTeX repr
# precedence as in https://docs.python.org/reference/expressions.html#operator-precedence
#
operators = {
    ast.Or: (op.or_,300,' or ',' or ',' \\vee '),
    ast.And: (op.and_,400,' and ',' and ',' \\wedge '),
    ast.Not: (op.not_,500,'not ','not ','\\neg'),
    ast.Eq: (op.eq,600,'=',' == ',' = '),
    ast.Gt: (op.gt,600,' > ',' > ',' \\gtr '),
    ast.GtE:(op.ge,600,' >= ',' >= ',' \\gec '),
    ast.Lt: (op.lt,600,' < ',' < ',' \\ltr '),
    ast.LtE: (op.le,600,' <= ',' <= ',' \\leq '),
    ast.BitXor: (op.xor,800,' xor ',' xor ',' xor '),
    ast.LShift: (op.lshift, 1000,' << ',' << ',' \\ll '),
    ast.RShift: (op.rshift, 1000,' >> ',' >> ',' \\gg '),
    ast.Add: (op.add, 1100,'+','+','+'),
    ast.Sub: (op.sub, 1100,'-','-','-'),
    ast.Mult: (op.mul, 1200,'','*',' \\cdot '),
    ast.Div: (op.truediv, 1200,'/','/','/'),
    ast.Mod: (op.mod, 1200,' mod ','%','\\bmod'),
    ast.Invert: (op.not_,1300,'~','~','\\sim'),
    ast.UAdd: (op.pos,1300,'+','+','+'),
    ast.USub: (op.neg,1300,'-','-','-'),
    ast.Pow: (op.pow,1400,'^','**','^'),

    # precedence of other types below
    ast.Name:(None,9999),
    ast.Num:(None,9999),
    ast.Call:(None,9999),
}

#indexes in operators to use for corresponding symbols
_dialect_str = 2
_dialect_python = 3
_dialect_latex = 4

import math
functions=math.__dict__ #allowed functions

def eval(node,ctx={}):
    """safe eval of ast node : only functions and operators listed above can be used
    
    :param node: ast.AST to evaluate
    :param ctx: dict of varname : value to substitute in node
    :return: number or expression string
    """
    if isinstance(node, ast.Num): # <number>
        return node.n
    elif isinstance(node, ast.Name):
        return ctx.get(node.id,node.id) #return value or var
    elif isinstance(node, ast.Attribute):
        return getattr(ctx[node.value.id],node.attr)
    elif isinstance(node,ast.Tuple):
        return tuple(eval(e,ctx) for e in node.elts)
    elif isinstance(node, ast.Call):
        params=[eval(arg,ctx) for arg in node.args]
        if not node.func.id in functions:
            raise NameError('%s function not allowed'%node.func.id)
        f=functions[node.func.id]
        return f(*params)
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        op=operators[type(node.op)]
        left=eval(node.left,ctx)
        right=eval(node.right,ctx)
        if math2.is_number(left) and math2.is_number(right):
            return op[0](left, right)
        else:
            return "%s%s%s"%(left,op[_dialect_python],right)
    elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
        right=eval(node.operand,ctx)
        return operators[type(node.op)][0](right)
    elif isinstance(node, ast.Compare):
        left=eval(node.left,ctx)
        for op,right in zip(node.ops,node.comparators):
            #TODO: find what to do when multiple items in list
            return operators[type(op)][0](left, eval(right,ctx))
    elif six.PY3 and isinstance(node, ast.NameConstant):
        return node.value
    else:
        logging.warning(ast.dump(node,False,False))
        return eval(node.body,ctx) #last chance

def get_function_source(f):
    """returns cleaned code of a function or lambda
    currently only supports:
    - lambda x:formula_of_(x)
    - def anything(x): return formula_of_(x)
    """
    f=inspect.getsource(f).rstrip('\n') #TODO: merge lines more subtly
    g=re.search(r'lambda(.*):(.*)(\)|#)',f)
    if g:
        res=g.group(2).strip() #remove leading+trailing spaces
        bra,ket=res.count('('),res.count(')')
        if bra==ket:
            return res
        else: #closing parenthesis ?
            return res[:-(ket-bra)]
    else:
        g=re.search(r'def \w*\((.*)\):\s*return (.*)',f)
        if g is None:
            logging.error('not a valid function code %s'%f)
        res=g.group(2)
    return res


class Expr(plot.Plot):
    """
    Math expressions that can be evaluated like standard functions
    combined using standard operators
    and plotted in IPython/Jupyter notebooks
    """
    def __init__(self,f):
        """
        :param f: function or operator, Expr to copy construct, or formula string
        """

        if isinstance(f,Expr): #copy constructor
            self.body=f.body
            return
        elif isinstance(f,ast.AST):
            self.body=f
            return
        elif inspect.isfunction(f):
            f=get_function_source(f)
        elif isinstance(f, collections.Callable): # builtin function
            f='%s(x)'%f.__name__
        elif f in ('True','False'):
            f=bool(f)
        if type(f) is bool: 
            self.body=ast.Num(f)
            return
        if type(f) is float: #try to beautify it
            if math2.is_integer(f):
                f=math2.rint(f)
            elif f!=0 and math2.is_integer(1/f):
                f='1/%d'%math2.rint(1/f)
            elif math2.is_integer(f*f):
                f='sqrt(%d)'%math2.rint(f*f)
                
        f=str(f).replace('^','**') #accept ^ as power operator rather than xor ...

        self.body=compile(f,'Expr','eval',ast.PyCF_ONLY_AST).body
        
    @property
    def isNum(self):
        return isinstance(self.body,ast.Num)
    
    @property
    def isconstant(self):
        """:return: True if Expr evaluates to a constant number of bool"""
        res=self()
        return not isinstance(res,six.string_types)

    def __call__(self,x=None,**kwargs):
        """evaluate the Expr at x OR compose self(x())"""
        if isinstance(x,Expr): #composition
            return self.applx(x)
        if itertools2.isiterable(x):
            return (self(x) for x in x)
        if x is not None:
            kwargs['x']=x
        kwargs['self']=self #allows to call methods such as in Stats
        try:
            e=eval(self.body,kwargs)
        except TypeError: # some params remain symbolic
            return self
        except Exception as error:# ZeroDivisionError, OverflowError
            return None
        if math2.is_number(e):
            return e
        return Expr(e)
    
    def __float__(self):
        return float(self())

    def __repr__(self):
        return TextVisitor(_dialect_python).visit(self.body)
        return ast.dump(self.body,False,False)

    def __str__(self):
        return TextVisitor(_dialect_str).visit(self.body)
    
    def _repr_html_(self):
        """default rich format is LaTeX"""
        return self._repr_latex_()

    def latex(self):
        """:return: string LaTex formula"""
        return LatexVisitor().visit(self.body)

    def _repr_latex_(self):
        return r'$%s$'%self.latex()

    def _plot(self, ax, x=None, y=None, **kwargs):
        if x is None:
            x=itertools2.arange(-1,1,.1)
        x=list(x)
        if y is None:
            y=self(x)

        offset=kwargs.pop('offset',0) #slightly shift the points to make superimposed curves more visible
        
        points=list(zip(x,y)) # might contain (x,None) for undefined points
        for xy in itertools2.isplit(points,lambda _:_[1] is None): # curves between defined points
            xy=list(xy)
            x=[v[0]+offset for v in xy]
            y=[v[1]+offset for v in xy]
            ax.plot(x,y, **kwargs)
        return ax

    def apply(self,f,right=None):
        """function composition self o f = f(self(x))"""

        if right is None:
            if isinstance(f, ast.unaryop):
                node=ast.UnaryOp(f,self.body)
            else:
                #if not isinstance(f,Expr): f=Expr(f) #not useful as applx does the reverse
                return f.applx(self)
        else:
            if not isinstance(right,Expr):
                right=Expr(right)
            node = ast.BinOp(self.body,f,right.body)
        return Expr(node)

    def applx(self,f,var='x'):
        """function composition f o self = self(f(x))"""
        if isinstance(f,Expr):
            f=f.body

        class Subst(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id==var:
                    return f
                else:
                    return node

        node=copy.deepcopy(self.body)
        return Expr(Subst().visit(node))

    def __eq__(self,other):
        if math2.is_number(other):
            try:
                return self()==other
            except:
                return False
        if not isinstance(other,Expr):
            other=Expr(other)
        return str(self())==str(other())
    
    def __ne__(self, other):
        return not self==other

    def __lt__(self,other):
        if math2.is_number(other):
            try:
                return self()<other
            except:
                return False
        if not isinstance(other,Expr):
            other=Expr(other)
        return float(self())<float(other())
        
    def __le__(self, other):
        return self<other or self==other
    
    def __ge__(self, other):
        return not self<other
    
    def __gt__(self,other):
        return self>=other and not self==other

    def __add__(self,right):
        return self.apply(ast.Add(),right)

    def __sub__(self,right):
        return self.apply(ast.Sub(),right)

    def __neg__(self):
        return self.apply(ast.USub())

    def __mul__(self,right):
        return self.apply(ast.Mult(),right)

    def __rmul__(self,right):
        return Expr(right)*self

    def __truediv__(self,right):
        return self.apply(ast.Div(),right)
    
    def __pow__(self,right):
        return self.apply(ast.Pow(),right)


    __div__=__truediv__

    def __invert__(self):
        return self.apply(ast.Invert())

    def __and__(self,right):
        return self.apply(ast.And(),right)

    def __or__(self,right):
        return self.apply(ast.Or(),right)

    def __xor__(self,right):
        return self.apply(ast.BitXor(),right)

    def __lshift__(self,dx):
        return self.applx(ast.BinOp(ast.Name('x',None),ast.Add(),ast.Num(dx)))

    def __rshift__(self,dx):
        return self.applx(ast.BinOp(ast.Name('x',None),ast.Sub(),ast.Num(dx)))
    
    def complexity(self):
        """ measures the complexity of Expr
        :return: int, sum of the precedence of used ops
        """
        def _node_complexity(node):
            res=0
            try:
                res=operators[type(node.op)][1]
            except:
                pass
            try:
                res+=_node_complexity(node.left)
            except:
                pass
            try:
                res+=_node_complexity(node.right)
            except:
                pass
            return res
        return _node_complexity(self.body)


#http://stackoverflow.com/questions/3867028/converting-a-python-numeric-expression-to-latex

class TextVisitor(ast.NodeVisitor):
    
    def __init__(self,dialect):
        ''':param dialect: int index in operators of symbols to use
        '''
        self.dialect=dialect

    def prec(self, n):
        try:
            return operators[type(n)][1]
        except KeyError:
            return operators[type(n.op)][1]

    def prec_UnaryOp(self, n):
        return self.prec(n.op)

    def prec_BinOp(self, n):
        return self.prec(n.op)
    
    @staticmethod
    def _par(content):
        return r'(%s)'%content

    def visit_Call(self, n):
        func = self.visit(n.func)
        args = r', '.join(map(self.visit, n.args))
        return str(func)+self._par(args)

    def visit_Name(self, n):
        return n.id
    
    def visit_NameConstant(self, node):
        return str(node.value)

    def visit_UnaryOp(self, n):
        symbol=operators[type(n.op)][self.dialect]
        left=self.visit(n.operand)
        if self.prec(n.op) > self.prec(n.operand):
            left=self._par(left)
        return symbol+left

    def _Bin(self, left,op,right):
        
        # commute x*3 in 3*x
        if isinstance(op, ast.Mult) and \
            isinstance(right, ast.Num) and \
            not isinstance(left, ast.Num): 
            return self._Bin(right,op,left)
        
        l,r = self.visit(left),self.visit(right)
        #handle precedence (parenthesis) if needed
            
        if isinstance(op, ast.Sub): # forces (a-b)-(c+d) and a-(-b) 
            if self.prec(op) >= self.prec(left):
                l = self._par(l)
            if self.prec(op) >= self.prec(right) or isinstance(right, ast.UnaryOp):
                r = self._par(r)
        else:
            if self.prec(op) > self.prec(left):
                l = self._par(l)
            if self.prec(op) > self.prec(right) or (
                isinstance(right, ast.UnaryOp) and isinstance(op, ast.Add)
            ):
                r = self._par(r)
            
            
        symbol=operators[type(op)][self.dialect]

        # check if we should have a '*' nevertheless
        if not symbol and isinstance(op, ast.Mult) and l[-1].isdigit() and r[0].isdigit():
            symbol='*'
        return l+symbol+r

    def visit_BinOp(self, n):
        return self._Bin(n.left,n.op,n.right)

    def visit_Compare(self,n):
        #TODO: what to do with multiple ops/comparators ?
        return self._Bin(n.left,n.ops[0],n.comparators[0])

    def visit_Num(self, n):
        return str(math2.int_or_float(n.n))

    def generic_visit(self, n):
        try:
            l=list(map(self.visit, n))
            return ''.join(l)
        except TypeError:
            pass

        if isinstance(n, ast.AST):
            l=map(self.visit, [getattr(n, f) for f in n._fields])
            return ''.join(l)
        else:
            return str(n)


class LatexVisitor(TextVisitor):
    def __init__(self):
        super(LatexVisitor,self).__init__(_dialect_latex)

    def visit_Call(self, n):
        func = self.visit(n.func)
        args = ', '.join(map(self.visit, n.args))
        if func in ['sqrt']:
            return r'\%s {%s}' % (func, args)
        if func in ['factorial']:
            return r'%s!' % args
            
        return r'\%s \left(%s\right)' % (func, args)

    def visit_UnaryOp(self, n):
        if self.prec(n.op) >= self.prec(n.operand):
            return r'%s\left(%s\right)' % (operators[type(n.op)][_dialect_latex], self.visit(n.operand))
        else:
            try:
                return r'%s %s' % (operators[type(n.op)][_dialect_latex], self.visit(n.operand))
            except Exception as e:
                pass

    def _Bin(self, left,op,right):
        # commute x*2 as 2*X for clarity
        if isinstance(op, ast.Mult):
            if isinstance(right, ast.Num) and not isinstance(left, ast.Num):
                return self._Bin(right,op,left)

        l,r = self.visit(left),self.visit(right)

        #handle divisions and power first as precedence doesn't matter
        if isinstance(op, ast.Div):
            return r'\frac{%s}{%s}' % (l, r)
        if isinstance(op, ast.FloorDiv):
            return r'\left\lfloor\frac{%s}{%s}\right\rfloor' % (l,r)
        if isinstance(op, ast.Pow):
            if isinstance(right,ast.BinOp):
                return r'%s^{%s}' % (l,r)
            else:
                return r'%s^%s' % (l,r)
        #handle precedence (parenthesis) if needed
        if self.prec(op) > self.prec(left):
            l = r'\left(%s\right)' % l
        if self.prec(op) > self.prec(right):
            r = r'\left(%s\right)' % r

        if isinstance(op, ast.Mult):
            if isinstance(left, ast.Num) and not isinstance(right, ast.Num):
                return l+r

        return l+operators[type(op)][_dialect_latex]+r






