'''
more math than :mod:`math` standard library, without numpy
'''
__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2012, Philippe Guglielmetti"
__credits__ = [
    "https://pypi.python.org/pypi/primefac"
    "https://github.com/tokland/pyeuler/blob/master/pyeuler/toolset.py",
    "http://blog.dreamshire.com/common-functions-routines-project-euler/",
]
__license__ = "LGPL"

import logging

import math
import cmath
import operator
import itertools
import functools
import fractions
import numbers
import random
from typing import Generator, Iterable, Iterator
from bitarray import bitarray

from goulib import itertools2, decorators

inf = float('Inf')  # infinity
eps = 2.2204460492503131e-16  # numpy.finfo(np.float64).eps

try:
    nan = math.nan
except AttributeError:
    nan = float('nan')  # Not a Number


def longint(mantissa, exponent):
    ''' :return: int equivalent to int(mantissa*10^exponent) without rounding errors
    '''
    s = str(mantissa)
    if 'E' in s:
        raise ValueError
    p = 0
    try:
        p = s.index('.')
        s = s.replace('.', '', 1)
        p = len(s)-p
    except ValueError:
        pass
    p = exponent - p
    if p < 0:
        raise ValueError
    if p > 0:
        s = s + '0' * p
    return int(s)


def cmp(x, y):
    '''Compare the two objects x and y and return an integer according to the outcome.
    The return value is negative if x < y, zero if x == y and strictly positive if x > y.
    '''
    return sign(x - y)


isclose = math.isclose  # for historic reasons : wasn't available before python 3.5


def allclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    ''':return: True if two arrays are element-wise equal within a tolerance.'''
    # https://docs.scipy.org/doc/numpy-1.14.0/reference/generated/numpy.allclose.html
    for x, y in itertools.zip_longest(a, b):
        if x is None or y is None:
            return False
        if not isclose(x, y, rel_tol=rel_tol, abs_tol=abs_tol):
            return False
    return True

# basic useful functions


def is_number(x):
    ''':return: True if x is a number of any type, including Complex'''
    # http://stackoverflow.com/questions/4187185/how-can-i-check-if-my-python-object-is-a-number
    return isinstance(x, numbers.Number)


def is_complex(x):
    return isinstance(x, complex)


def is_real(x):
    return is_number(x) and not is_complex(x)


def sign(number):
    ''':return: 1 if number is positive, -1 if negative, 0 if ==0'''
    if number < 0:
        return -1
    if number > 0:
        return 1
    return 0

# rounding


def rint(v):
    '''
    :return: int value nearest to float v
    '''
    return int(round(v))


def is_integer(x, rel_tol=0, abs_tol=0):
    '''
    :return: True if  float x is an integer within tolerances
    '''
    if isinstance(x, int):
        return True
    try:
        if rel_tol + abs_tol == 0:
            return x == rint(x)
        return isclose(x, round(x), rel_tol=rel_tol, abs_tol=abs_tol)
    except (TypeError, ValueError):  # for complex, NaN, inf etc.
        return False


def int_or_float(x, rel_tol=0, abs_tol=0):
    '''
    :param x: int or float
    :return: int if x is (almost) an integer, otherwise float
    '''
    return rint(x) if is_integer(x, rel_tol, abs_tol) else x


def format(x, decimals=3):
    ''' formats a float with given number of decimals, but not an int

    :return: string repr of x with decimals if not int
    '''
    if is_integer(x):
        decimals = 0
    return '{0:.{1}f}'.format(x, decimals)

# improved versions of math functions


def gcd(*args):
    '''greatest common divisor of an arbitrary number of args'''
    # http://code.activestate.com/recipes/577512-gcd-of-an-arbitrary-list/

    L = list(args)  # in case args are generated

    b = L[0]  # will be returned if only one arg

    while len(L) > 1:
        a = L[-2]
        b = L[-1]
        L = L[:-2]

        while a:
            a, b = b % a, a

        L.append(b)

    return abs(b)


def lcm(*args):
    '''least common multiple of any number of integers'''
    if len(args) <= 2:
        return mul(args) // gcd(*args)
    # TODO : better
    res = lcm(args[0], args[1])
    for n in args[2:]:
        res = lcm(res, n)
    return res


def xgcd(a, b):
    '''Extended GCD

    :return: (gcd, x, y) where gcd is the greatest common divisor of a and b
    with the sign of b if b is nonzero, and with the sign of a if b is 0.
    The numbers x,y are such that gcd = ax+by.'''
    # taken from http://anh.cs.luc.edu/331/code/xgcd.py
    prevx, x = 1, 0
    prevy, y = 0, 1
    while b:
        q, r = divmod(a, b)
        x, prevx = prevx - q * x, x
        y, prevy = prevy - q * y, y
        a, b = b, r
    return a, prevx, prevy


def coprime(*args):
    ''':return: True if args are coprime to each other'''
    return gcd(*args) == 1


def coprimes_gen(limit):
    '''generates coprime pairs
    using Farey sequence
    '''
    # https://www.quora.com/What-are-the-fastest-algorithms-for-generating-coprime-pairs

    pend = []
    n, d = 0, 1  # n, d is the start fraction n/d (0,1) initially
    N = D = 1  # N, D is the stop fraction N/D (1,1) initially
    while True:
        mediant_d = d + D
        if mediant_d <= limit:
            mediant_n = n + N
            pend.append((mediant_n, mediant_d, N, D))
            N = mediant_n
            D = mediant_d
        else:
            yield n, d  # numerator / denominator
            if pend:
                n, d, N, D = pend.pop()
            else:
                break


def carmichael(n):
    '''
    Carmichael function
    :return : int smallest positive integer m such that a^m mod n = 1 for every integer a between 1 and n that is coprime to n.
    :param n: int
    :see: https://en.wikipedia.org/wiki/Carmichael_function
    :see: https://oeis.org/A002322

    also known as the reduced totient function or the least universal exponent function.
    '''
    coprimes = [x for x in range(1, n) if gcd(x, n) == 1]
    k = 1
    while not all(pow(x, k, n) == 1 for x in coprimes):
        k += 1
    return k

# https://en.wikipedia.org/wiki/Primitive_root_modulo_n
# code decomposed from http://stackoverflow.com/questions/40190849/efficient-finding-primitive-roots-modulo-n-using-python


def is_primitive_root(x, m, s={}):
    '''returns True if x is a primitive root of m

    :param s: set of coprimes to m, if already known
    '''
    if not s:
        s = {n for n in range(1, m) if coprime(n, m)}
    return {pow(x, p, m) for p in range(1, m)} == s


def primitive_root_gen(m):
    '''generate primitive roots modulo m'''
    required_set = {num for num in range(1, m) if coprime(num, m)}
    for n in range(1, m):
        if is_primitive_root(n, m, required_set):
            yield n


def primitive_roots(modulo):
    return list(primitive_root_gen(modulo))


def quad(a, b, c, allow_complex=False):
    ''' solves quadratic equations aX^2+bX+c=0

    :param a,b,c: floats
    :param allow_complex: function returns complex roots if True
    :return: x1,x2 real or complex solutions
    '''
    discriminant = b * b - 4 * a * c
    if allow_complex:
        d = cmath.sqrt(discriminant)
    else:
        d = math.sqrt(discriminant)
    return (-b + d) / (2 * a), (-b - d) / (2 * a)


def ceildiv(a, b):
    return -(-a // b)  # simple and clever


def ipow(x, y, z=0):
    '''
    :param x: number (int or float)
    :param y: int power
    :param z: int optional modulus
    :return: (x**y) % z as integer if possible
    '''

    if y < 0:
        if z:
            raise NotImplementedError('no modulus allowed for negative power')
        else:
            return 1 / ipow(x, -y)

    a, b = 1, x
    while y > 0:
        if y % 2 == 1:
            a = (a * b) % z if z else a * b
        b = (b * b) % z if z else b * b
        y = y // 2
    return a


def pow(x, y, z=0):
    '''
    :return: (x**y) % z as integer
    '''
    if not isinstance(y, int):
        if z == 0:
            return pow(x, y)  # switches to floats in Py3...
        else:
            return pow(x, y, z)  # switches to floats in Py3...
    else:
        return ipow(x, y, z)


def sqrt(n):
    '''square root
    :return: int, float or complex depending on n
    '''
    if type(n) is int:
        s = isqrt(n)
        if s * s == n:
            return s
    if n < 0:
        return cmath.sqrt(n)
    return math.sqrt(n)


def isqrt(n):
    '''integer square root

    :return: largest int x for which x * x <= n
    '''
    # http://stackoverflow.com/questions/15390807/integer-square-root-in-python
    # https://projecteuler.net/thread=549#235536
    n = int(n)
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def icbrt(n):
    '''integer cubic root

    :return: largest int x for which x * x * x <= n
    '''
    # https://projecteuler.net/thread=549#235536
    if n <= 0:
        return 0
    x = int(n ** (1. / 3.) * (1 + 1e-12))
    while True:
        y = (2 * x + n // (x * x)) // 3
        if y >= x:
            return x
        x = y


def is_square(n):
    s = isqrt(n)
    return s * s == n


def introot(n, r=2):
    ''' integer r-th root

    :return: int, greatest integer less than or equal to the r-th root of n.

    For negative n, returns the least integer greater than or equal to the r-th root of n, or None if r is even.
    '''
    # copied from https://pypi.python.org/pypi/primefac
    if n < 0:
        return None if r % 2 == 0 else -introot(-n, r)
    if n < 2:
        return n
    if r == 2:
        return isqrt(n)
    lower, upper = 0, n
    while lower != upper - 1:
        mid = (lower + upper) // 2
        m = mid ** r
        if m == n:
            return mid
        elif m < n:
            lower = mid
        elif m > n:
            upper = mid
    return lower


def is_power(n):
    '''
    :return: integer that, when squared/cubed/etc, yields n,
    or 0 if no such integer exists.
    Note that the power to which this number is raised will be prime.'''
    # copied from https://pypi.python.org/pypi/primefac
    for p in primes_gen():
        r = introot(n, p)
        if r is None:
            continue
        if r ** p == n:
            return r
        if r == 1:
            return 0


def multiply(x, y):
    '''
    Karatsuba fast multiplication algorithm

    https://en.wikipedia.org/wiki/Karatsuba_algorithm

    Copyright (c) 2014 Project Nayuki
    http://www.nayuki.io/page/karatsuba-multiplication
    '''
    _CUTOFF = 1536  # _CUTOFF >= 64, or else there will be infinite recursion.
    if x.bit_length() <= _CUTOFF or y.bit_length() <= _CUTOFF:  # Base case
        return x * y

    else:
        n = max(x.bit_length(), y.bit_length())
        half = (n + 32) // 64 * 32
        mask = (1 << half) - 1
        xlow = x & mask
        ylow = y & mask
        xhigh = x >> half
        yhigh = y >> half

        a = multiply(xhigh, yhigh)
        b = multiply(xlow + xhigh, ylow + yhigh)
        c = multiply(xlow, ylow)
        d = b - a - c
        return (((a << half) + d) << half) + c

# vector operations


def accsum(it):
    '''Yield accumulated sums of iterable: accsum(count(1)) -> 1,3,6,10,...'''
    return itertools2.drop(1, itertools2.ireduce(operator.add, it, 0))


cumsum = accsum  # numpy alias


def mul(nums, init=1):
    '''
    :return: Product of nums
    '''
    return functools.reduce(operator.mul, nums, init)


def dot_vv(a, b, default=0):
    '''dot product for vectors

    :param a: vector (iterable)
    :param b: vector (iterable)
    :param default: default value of the multiplication operator
    '''
    return sum(map(operator.mul, a, b), default)


def dot_mv(a, b, default=0):
    '''dot product for vectors

    :param a: matrix (iterable or iterables)
    :param b: vector (iterable)
    :param default: default value of the multiplication operator
    '''
    return [dot_vv(line, b, default) for line in a]


def dot_mm(a, b, default=0):
    '''dot product for matrices

    :param a: matrix (iterable or iterables)
    :param b: matrix (iterable or iterables)
    :param default: default value of the multiplication operator
    '''
    return transpose([dot_mv(a, col) for col in zip(*b)])


def dot(a, b, default=0):
    '''dot product

    general but slow : use dot_vv, dot_mv or dot_mm if you know a and b's dimensions
    '''
    if itertools2.ndim(a) == 2:  # matrix
        if itertools2.ndim(b) == 2:  # matrix*matrix
            return dot_mm(a, b, default)
        else:  # matrix*vector
            return dot_mv(a, b, default)
    else:  # vector*vector
        return dot_vv(a, b, default)


# some basic matrix ops
def zeros(shape):
    '''
    :see: https://docs.scipy.org/doc/numpy/reference/generated/numpy.zeros.html
    '''
    return [[0] * shape[1]] * shape[0]


def diag(v):
    '''
    Create a two-dimensional array with the flattened input as a diagonal.

    :param v: If v is a 2-D array, return a copy of its diagonal.
        If v is a 1-D array, return a 2-D array with v on the diagonal
    :see: https://docs.scipy.org/doc/numpy/reference/generated/numpy.diag.html#numpy.diag
    '''
    s = len(v)
    if itertools2.ndim(v) == 2:
        return [v[i][i] for i in range(s)]
    res = []
    for i, x in enumerate(v):
        line = [x] + [0] * (s - 1)
        line = line[-i:] + line[:-i]
        res.append(line)
    return res


def identity(n):
    return diag([1] * n)


eye = identity  # alias for now


def transpose(m):
    '''
    :return: matrix m transposed
    '''
    # ensures the result is a list of lists
    return list(map(list, list(zip(*m))))


def maximum(m):
    '''
    Compare N arrays and returns a new array containing the element-wise maxima

    :param m: list of arrays (matrix)
    :return: list of maximal values found in each column of m
    :see: http://docs.scipy.org/doc/numpy/reference/generated/numpy.maximum.html
    '''
    return [max(c) for c in transpose(m)]


def minimum(m):
    '''
    Compare N arrays and returns a new array containing the element-wise minima

    :param m: list of arrays (matrix)
    :return: list of minimal values found in each column of m
    :see: http://docs.scipy.org/doc/numpy/reference/generated/numpy.minimum.html
    '''
    return [min(c) for c in transpose(m)]


def vecadd(a, b, fillvalue=0):
    '''addition of vectors of inequal lengths'''
    return [c[0] + c[1] for c in itertools.zip_longest(a, b, fillvalue=fillvalue)]


def vecsub(a, b, fillvalue=0):
    '''substraction of vectors of inequal lengths'''
    return [c[0] - c[1] for c in itertools.zip_longest(a, b, fillvalue=fillvalue)]


def vecneg(a):
    '''unary negation'''
    return list(map(operator.neg, a))


def vecmul(a, b):
    '''product of vectors of inequal lengths'''
    if isinstance(a, (int, float)):
        return [x * a for x in b]
    if isinstance(b, (int, float)):
        return [x * b for x in a]
    return [functools.reduce(operator.mul, c) for c in zip(a, b)]


def vecdiv(a, b):
    '''quotient of vectors of inequal lengths'''
    if isinstance(b, (int, float)):
        return [float(x) / b for x in a]
    return [functools.reduce(operator.truediv, c) for c in zip(a, b)]


def veccompare(a, b):
    '''compare values in 2 lists. returns triple number of pairs where [a<b, a==b, a>b]'''
    res = [0, 0, 0]
    for ai, bi in zip(a, b):
        if ai < bi:
            res[0] += 1
        elif ai == bi:
            res[1] += 1
        else:
            res[2] += 1
    return res


def sat(x, low=0, high=None):
    ''' saturates x between low and high '''
    if isinstance(x, (int, float)):
        if low is not None:
            x = max(x, low)
        if high is not None:
            x = min(x, high)
        return x
    return [sat(_, low, high) for _ in x]

# norms and distances


def norm_2(v):
    '''
    :return: "normal" euclidian norm of vector v
    '''
    return sqrt(sum(x * x for x in v))


def norm_1(v):
    '''
    :return: "manhattan" norm of vector v
    '''
    return sum(abs(x) for x in v)


def norm_inf(v):
    '''
    :return: infinite norm of vector v
    '''
    return max(abs(x) for x in v)


def norm(v, order=2):
    '''
    :see: http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.norm.html
    '''
    return sum(abs(x) ** order for x in v) ** (1. / order)


def dist(a, b, norm=norm_2):
    return norm(vecsub(a, b))


def vecunit(v, norm=norm_2):
    '''
    :return: vector normalized
    '''
    return vecdiv(v, norm(v))


def hamming(s1, s2):
    '''Calculate the Hamming distance between two iterables'''
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def sets_dist(a, b):
    '''
    :see: http://stackoverflow.com/questions/11316539/calculating-the-distance-between-two-unordered-sets
    '''
    c = a.intersection(b)
    return sqrt(len(a - c) * 2 + len(b - c) * 2)


def sets_levenshtein(a, b):
    '''levenshtein distance on sets

    :see: http://en.wikipedia.org/wiki/Levenshtein_distance
    '''
    c = a.intersection(b)
    return len(a - c) + len(b - c)


def levenshtein(seq1, seq2):
    '''levenshtein distance

    :return: distance between 2 iterables
    :see: http://en.wikipedia.org/wiki/Levenshtein_distance
    '''
    # http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
    oneago = None
    thisrow = list(range(1, len(seq2) + 1)) + [0]
    for x in range(len(seq1)):
        _, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in range(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
    return thisrow[len(seq2) - 1]

# stats

# moved to stats.py

# numbers functions
# originally from https://github.com/tokland/pyeuler/blob/master/pyeuler/toolset.py


def recurrence(factors, values, cst=0, max=None, mod=0):
    '''general generator for recurrences

    :param signature: factors defining the recurrence
    :param values: list of initial values
    '''
    if not isinstance(factors, list):
        signature = list(factors)  # to allow tuples or iterators
    if not isinstance(values, list):
        values = list(values)  # to allow tuples or iterators
    for n in values:
        if mod:
            n = n % mod
        yield n
    values = values[-len(factors):]
    while True:
        n = dot_vv(factors, values)
        if max and n > max:
            break
        n = n + cst
        if mod:
            n = n % mod
        yield n
        values.pop(0)
        values.append(n)


# https://en.wikipedia.org/wiki/Lucas_sequence
def lucasU(p, q):
    return recurrence([-q, p], [0, 1])


def lucasV(p, q):
    return recurrence([-q, p], [2, p])


def kfibonacci_gen(k, init=None, max=None, mod=0):
    '''Generate k-fibonacci serie'''
    init = init or [0] * (k - 1) + [1]
    return recurrence([1] * k, init, max=max, mod=mod)


def fibonacci_gen(max=None, mod=0):
    '''Generate fibonacci serie (k=2)'''
    return kfibonacci_gen(2, None, max, mod)


def kfibonacci(k, mod=0):
    ''' k-fibonacci series n-th element

    :param k: int number of consecutive terms to add
    :param mod: int optional modulo
    :return: function(n) returning the n-th element
    '''
    # http://stackoverflow.com/a/28549402/1395973
    # uses http://mathworld.wolfram.com/FibonacciQ-Matrix.html
    mat = identity(k - 1)
    for row in mat:
        row.append(0)
    mat.insert(0, [1] * k)
    return lambda n: mod_matpow(mat, n, mod)[0][k - 1]


def fibonacci(n, mod=0):
    ''' fibonacci series n-th element
    :param n: int can be extremely high, like 1e19 !
    :param mod: int optional modulo
    '''
    return kfibonacci(2, mod)(n)


def is_fibonacci(n):
    '''returns True if n is in Fibonacci series'''
    # http://www.geeksforgeeks.org/check-number-fibonacci-number/
    return is_square(5 * n * n + 4) or is_square(5 * n * n - 4)


def pisano_cycle(mod):
    if mod < 2:
        return [0]
    seq = [0, 1]
    k = len(seq)
    s = []
    for i, n in enumerate(fibonacci_gen(mod=mod)):
        s.append(n)
        if i > k and s[-k:] == seq:
            return s[:-k]


def pisano_period(mod):
    if mod < 2:
        return 1
    flag = False  # 0 was found
    for i, n in enumerate(fibonacci_gen(mod=mod)):
        if not flag:
            flag = n == 0
        elif i > 3:
            if n == 1:
                return i - 1
            flag = False


def collatz(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1


def collatz_gen(n=0):
    yield n
    while True:
        n = collatz(n)
        yield n


@decorators.memoize
def collatz_period(n):
    if n == 1:
        return 1
    return 1 + collatz_period(collatz(n))


def pascal_row_gen():
    '''Pascal's triangle read by rows: C(n,k) = binomial(n,k) = n!/(k!*(n-k)!), 0<=k<=n.'''
    for row in itertools.count():
        x = 1
        res = [x]
        for m in range(row):
            x = (x * (row - m)) // (m + 1)
            res.append(x)
        yield res

def pascal_gen():
    '''Generate row n of Pascal's triangle: C(n,k) = binomial(n,k) = n!/(k!*(n-k)!), 0<=k<=n.

    https://oeis.org/A007318
    '''
    return itertools2.flatten(pascal_row_gen())
    return


def catalan(n):
    '''Catalan numbers: C(n) = binomial(2n,n)/(n+1) = (2n)!/(n!(n+1)!).
    '''
    return binomial(2 * n, n) // (n + 1)  # result is always int


def catalan_gen():
    '''Generate Catalan numbers: C(n) = binomial(2n,n)/(n+1) = (2n)!/(n!(n+1)!).
    Also called Segner numbers.
    '''
    yield 1
    last = 1
    yield last
    for n in itertools.count(1):
        last = last * (4 * n + 2) // (n + 2)
        yield last


def is_pythagorean_triple(a, b, c):
    return a * a + b * b == c * c


def primitive_triples():
    ''' generates primitive Pythagorean triplets x<y<z

    sorted by hypotenuse z, then longest side y
    through Berggren's matrices and breadth first traversal of ternary tree
    :see: https://en.wikipedia.org/wiki/Tree_of_primitive_Pythagorean_triples
    '''

    def key(x):
        return (x[2], x[1])

    from sortedcontainers import SortedListWithKey
    triples = SortedListWithKey(key=key)
    triples.add([3, 4, 5])
    A = [[1, -2, 2], [2, -1, 2], [2, -2, 3]]
    B = [[1, 2, 2], [2, 1, 2], [2, 2, 3]]
    C = [[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]]

    while triples:
        (a, b, c) = triples.pop(0)
        yield (a, b, c)

        # expand this triple to 3 new triples using Berggren's matrices
        for X in [A, B, C]:
            triple = [sum(x * y for (x, y) in zip([a, b, c], X[i]))
                      for i in range(3)]
            if triple[0] > triple[1]:  # ensure x<y<z
                triple[0], triple[1] = triple[1], triple[0]
            triples.add(triple)


def triples():
    ''' generates all Pythagorean triplets triplets x<y<z
    sorted by hypotenuse z, then longest side y
    '''
    prim = []  # list of primitive triples up to now

    def key(x):
        return (x[2], x[1])

    from sortedcontainers import SortedListWithKey
    samez = SortedListWithKey(key=key)  # temp triplets with same z
    buffer = SortedListWithKey(key=key)  # temp for triplets with smaller z
    for pt in primitive_triples():
        z = pt[2]
        if samez and z != samez[0][2]:  # flush samez
            while samez:
                yield samez.pop(0)
        samez.add(pt)
        # build buffer of smaller multiples of the primitives already found
        for i, pm in enumerate(prim):
            p, m = pm[0:2]
            while True:
                mz = m * p[2]
                if mz < z:
                    buffer.add(tuple(m * x for x in p))
                elif mz == z:
                    # we need another buffer because next pt might have
                    # the same z as the previous one, but a smaller y than
                    # a multiple of a previous pt ...
                    samez.add(tuple(m * x for x in p))
                else:
                    break
                m += 1
            prim[i][1] = m  # update multiplier for next loops
        while buffer:  # flush buffer
            yield buffer.pop(0)
        prim.append([pt, 2])  # add primitive to the list


def divisors(n):
    '''
    :param n: int
    :return: all divisors of n: divisors(12) -> 1,2,3,4,6,12
    including 1 and n,
    except for 1 which returns a single 1 to avoid messing with sum of divisors...
    '''
    if n == 1:
        yield 1
    else:
        all_factors = [
            [f ** p for p in itertools2.irange(0, fp)] for (f, fp) in factorize(n)]
        # do not use itertools2.product here as long as the order of the result differs
        for ns in itertools.product(*all_factors):
            yield mul(ns)


def proper_divisors(n):
    ''':return: all divisors of n except n itself.'''
    return (divisor for divisor in divisors(n) if divisor != n)


def erathostene(n):
    return n * n, 2 * n


class Sieve:
    '''General sieve
    '''
    # should be derived from bitarray but ...
    # https://github.com/ilanschnell/bitarray/issues/69
    # TODO: simplify when solved (still a problem in 2025...)

    def __init__(self, init: Iterable, f=erathostene):
        self._ = bitarray(init)
        self.f = f

    def __len__(self):
        return len(self._)

    def __getitem__(self, index):
        return self._[index]

    def __call__(self, n):
        self.resize(n)
        for i in range(n):
            if self._[i]:
                yield i

    def resize(self, n):
        k = len(self) - 1
        if n <= k:
            return
        n = int(n)  # to tolerate n=1E9, which is float
        self._.extend([True] * (n - k))
        for i in self(n):
            if i == 2:
                i2, s = 4, 2
            else:
                i2, s = self.f(i)
            if i2 > n:
                break
            self._[i2::s] = False  # bitarray([False]*int((n-i2)/s+1))


# bitset indicating primality
_sieve = Sieve('001', erathostene)


def sieve(n, oneisprime=False):
    '''prime numbers from 2 to a prime < n
    '''
    res = _sieve(n)
    if oneisprime:
        res = itertools.chain([1], res)
    return list(res)


_primes = sieve(1000)  # primes up to 1000
_primes_set = set(_primes)  # to speed us primality tests below


def primes(n):
    '''memoized list of n first primes

    :warning: do not call with large n, use prime_gen instead
    '''
    m = n - len(_primes)
    if m > 0:
        more = list(itertools2.take(m, primes_gen(_primes[-1] + 1)))
        _primes.extend(more)
        _primes_set.union(set(more))

    return _primes[:n]


def is_prime_euler(n, eb=(2,)):
    '''Euler's primality test

    :param n: int number to test
    :param eb: test basis
    :return: False if not prime, True if prime, but also for many pseudoprimes...
    :see: https://en.wikipedia.org/wiki/Euler_pseudoprime
    '''
    # https://pypi.python.org/pypi/primefac
    for b in eb:
        if b >= n:
            continue
        if not pow(b, n - 1, n) == 1:
            return False
        r = n - 1
        while r % 2 == 0:
            r //= 2
        c = pow(b, r, n)
        if c == 1:
            continue
        while c != 1 and c != n - 1:
            c = pow(c, 2, n)
        if c == 1:
            return False
    return True  # according to Euler, but there are


def is_prime(n, oneisprime=False, tb=(3, 5, 7, 11), eb=(2,), mrb=None) -> bool:
    '''main primality test.

    :param n: int number to test
    :param oneisprime: bool True if 1 should be considered prime (it was, a long time ago)
    :param tb: trial division basis
    :param eb: Euler's test basis
    :param mrb: Miller-Rabin basis, automatic if None

    :see: https://en.wikipedia.org/wiki/Baillie%E2%80%93PSW_primality_test

    It’s an implementation of the BPSW test (Baillie-Pomerance-Selfridge-Wagstaff)
    with some prefiltes for speed and is deterministic for all numbers less than 2^64
    Iin fact, while infinitely many false positives are conjectured to exist,
    no false positives are currently known.
    The prefilters consist of trial division against 2 and the elements of the tuple tb,
    checking whether n is square, and Euler’s primality test to the bases in the tuple eb.
    If the number is less than 3825123056546413051, we use the Miller-Rabin test
    on a set of bases for which the test is known to be deterministic over this range.
    '''
    # https://pypi.python.org/pypi/primefac

    if n <= 0:
        return False

    if n == 1:
        return oneisprime

    if n < len(_sieve):
        return _sieve[n]

    if n in _primes_set:
        return True

    if any(n % p == 0 for p in tb):
        return False

    if is_square(n):
        return False  # it's quick ...

    if not is_prime_euler(n):
        return False  # Euler's test

    s, d = pfactor(n)
    if not sprp(n, 2, s, d):
        return False
    if n < 2047:
        return True

    # BPSW has two phases: SPRP with base 2 and SLPRP.
    # We just did the SPRP; now we do the SLPRP
    if n >= 3825123056546413051:
        d = 5
        while True:
            if gcd(d, n) > 1:
                p, q = 0, 0
                break
            if jacobi(d, n) == -1:
                p, q = 1, (1 - d) // 4
                break
            d = -d - 2 * d // abs(d)
        if p == 0:
            return n == d
        s, t = pfactor(n + 2)
        u, v, u2, v2, m = 1, p, 1, p, t // 2
        k = q
        while m > 0:
            u2, v2, q = (u2 * v2) % n, (v2 * v2 - 2 * q) % n, (q * q) % n
            if m % 2 == 1:
                u, v = u2 * v + u * v2, v2 * v + u2 * u * d
                if u % 2 == 1:
                    u += n
                if v % 2 == 1:
                    v += n
                u, v, k = (u // 2) % n, (v // 2) % n, (q * k) % n
            m //= 2
        if (u == 0) or (v == 0):
            return True
        for i in range(1, s):
            v, k = (v * v - 2 * k) % n, (k * k) % n
            if v == 0:
                return True
        return False

    # Miller-Rabin
    if not mrb:
        if n < 1373653:
            mrb = [3]
        elif n < 25326001:
            mrb = [3, 5]
        elif n < 3215031751:
            mrb = [3, 5, 7]
        elif n < 2152302898747:
            mrb = [3, 5, 7, 11]
        elif n < 3474749660383:
            mrb = [3, 5, 6, 11, 13]
        elif n < 341550071728321:
            # This number is also a false positive for primes(19+1).
            mrb = [3, 5, 7, 11, 13, 17]
        elif n < 3825123056546413051:
            # Also a false positive for primes(31+1).
            mrb = [3, 5, 7, 11, 13, 17, 19, 23]
    return all(sprp(n, b, s, d) for b in mrb)


def nextprime(n):
    '''Determines, with some semblance of efficiency, the least prime number strictly greater than n.'''
    # from https://pypi.python.org/pypi/primefac
    if n < 2:
        return 2
    if n == 2:
        return 3
    n = (n + 1) | 1  # first odd larger than n
    m = n % 6
    if m == 3:
        if is_prime(n + 2):
            return n + 2
        n += 4
    elif m == 5:
        if is_prime(n):
            return n
        n += 2
    for m in itertools.count(n, 6):
        if is_prime(m):
            return m
        if is_prime(m + 4):
            return m + 4


def prevprime(n):
    '''Determines, very inefficiently, the largest prime number strictly smaller than n.'''
    if n < 3:
        return None
    if n == 3:
        return 2
    n = n | 1  # n if it is odd, or n+1 if it is even
    while True:
        n -= 2
        if is_prime(n):
            return n


def primes_gen(start=2, stop=None) -> Iterator[int]:
    '''generate prime numbers from start'''
    if start == 1:
        yield 1  # if we asked for it explicitly
        start = 2
    if stop is None or stop > start:
        n = start - 1  # to include start if it is prime
        while True:
            n = nextprime(n)
            if (stop is None) or n <= stop:
                yield n
            else:
                break
    else:  # backwards
        n = start + 1
        while True:
            n = prevprime(n)
            if n and n >= stop:
                yield n
            else:
                break


def random_prime(bits):
    '''returns a random number of the specified bit length'''
    import random
    while True:
        n = random.getrandbits(bits - 1) + 2 ** (bits - 1)
        n = nextprime(n - 1)
        if n < 2 ** bits:
            return n


def euclid_gen():
    '''generates Euclid numbers: 1 + product of the first n primes'''
    n = 1
    for p in primes_gen():
        n = n * p
        yield n + 1


def prime_factors(num, start=2):
    '''generates all prime factors (ordered) of num'''
    for p in primes_gen(start):
        if num == 1:
            break
        if is_prime(num):  # because it's fast
            yield num
            break
        if p > num:
            break
        while num % p == 0:
            yield p
            num = num // p


def lpf(n):
    '''greatest prime factor'''
    if n < 4:
        return n
    return itertools2.first(prime_factors(n))


def gpf(n):
    '''greatest prime factor'''
    if n < 4:
        return n
    return itertools2.last(prime_factors(n))


def prime_divisors(num, start=2):
    '''generates unique prime divisors (ordered) of num'''
    return itertools2.unique(prime_factors(num, start))


def is_multiple(n, factors):
    '''return True if n has ONLY factors as prime factors'''
    return not set(prime_divisors(n)) - set(factors)


def factorize(n):
    '''find the prime factors of n along with their frequencies. Example:

    >>> factor(786456)
    [(2,3), (3,3), (11,1), (331,1)]
    '''

    if n == 1:  # allows to make many things quite simpler...
        return [(1, 1)]
    return itertools2.compress(prime_factors(n))


def factors(n):
    for (p, e) in factorize(n):
        yield p ** e


def sigma(n):
    return sum(divisors(n))


def number_of_divisors(n):
    # http://mathschallenge.net/index.php?section=faq&ref=number/number_of_divisors
    res = 1
    if n > 1:
        for (p, e) in factorize(n):
            res = res * (e + 1)
    return res


def omega(n):
    '''Number of distinct primes dividing n'''
    return itertools2.count_unique(prime_factors(n))


def bigomega(n):
    '''Number of prime divisors of n counted with multiplicity'''
    return itertools2.ilen(prime_factors(n))


def moebius(n):
    '''Möbius (or Moebius) function mu(n).
    mu(1) = 1;
    mu(n) = (-1)^k if n is the product of k different primes;
    otherwise mu(n) = 0.
    '''
    if n == 1:
        return 1
    res = 1
    for p, q in factorize(n):
        if q > 1:
            return 0
        res = -res
    return res


def euler_phi(n):
    '''Euler totient function

    :see: http://stackoverflow.com/questions/1019040/how-many-numbers-below-n-are-coprimes-to-n
    '''
    if n <= 1:
        return n
    return int(mul((1 - 1.0 / p for p, _ in factorize(n)), n))


totient = euler_phi  # alias. totient is available in sympy


def kempner(n):
    '''"Kempner function, also called Smarandache function

    :return: int smallest positive integer m such that n divides m!.

    :param n: int

    :see: https://en.wikipedia.org/wiki/Kempner_function
    :see: http://mathworld.wolfram.com/SmarandacheFunction.html
    '''
    if n == 1:
        return 1
    if is_prime(n):
        return n

    @decorators.memoize
    def _np(n, p):
        # n^p . use https://codereview.stackexchange.com/a/129868/37671
        k = 0
        while p > n:
            k += n
            p -= n + 1
            t = k
            while t % n != 0:
                t = t // n
                p -= 1
        p = max(0, p)

        return (k + p) * n

    return max(_np(f, p) for f, p in factorize(n))


def prime_ktuple(constellation):
    '''
    generates tuples of primes with specified differences

    :param constellation: iterable of int differences betwwen primes to return
    :note: negative int means the difference must NOT be prime
    :see: https://en.wikipedia.org/wiki/Prime_k-tuple
    (0, 2)    twin primes
    (0, 4)    cousin primes
    (0, 6)    sexy primes
    (0, 2, 6), (0, 4, 6)    prime triplets
    (0, 6, 12, -18)    sexy prime triplets
    (0, 2, 6, 8)    prime quadruplets
    (0, 6, 12, 18)    sexy prime quadruplets
    (0, 2, 6, 8, 12), (0, 4, 6, 10, 12)    quintuplet primes
    (0, 4, 6, 10, 12, 16)    sextuplet primes

    '''
    diffs = constellation[1:]
    for p in primes_gen():
        res = [p]
        for d in diffs:
            if is_prime(p + abs(d)) == (d < 0):
                break
            if d > 0:
                res.append(p + d)
        else:  # no break
            yield tuple(res)


def twin_primes():
    return prime_ktuple((0, 2))


def cousin_primes():
    return prime_ktuple((0, 4))


def sexy_primes():
    return prime_ktuple((0, 6))


def sexy_prime_triplets():
    return prime_ktuple((0, 6, 12, -18))  # exclude quatruplets


def sexy_prime_quadruplets():
    return prime_ktuple((0, 6, 12, 18))


def lucas_lehmer(p):
    '''Lucas Lehmer primality test for Mersenne exponent p

    :param p: int
    :return: True if 2^p-1 is prime
    '''
    # http://rosettacode.org/wiki/Lucas-Lehmer_test#Python
    if p == 2:
        return True
    elif not is_prime(p):
        return False
    else:
        m_p = (1 << p) - 1  # 2^p-1
    s = 4
    for i in range(3, p + 1):
        s = (s * s - 2) % m_p
    return s == 0

# digits manipulation


def digits_gen(num, base=10):
    '''generates int digits of num in base BACKWARDS'''
    if num == 0:
        yield 0
    while num:
        num, rem = divmod(num, base)
        yield rem


def digits(num, base=10, rev=False):
    '''
    :return: list of digits of num expressed in base, optionally reversed
    '''
    res = list(digits_gen(num, base))
    if not rev:
        res.reverse()
    return res


def digsum(num, f=None, base=10):
    '''sum of digits

    :param num: number
    :param f: int power or function applied to each digit
    :param base: optional base
    :return: sum of f(digits) of num

    digsum(num) -> sum of digits
    digsum(num,base=2) -> number of 1 bits in binary represenation of num
    digsum(num,2) -> sum of the squares of digits
    digsum(num,f=lambda x:x**x) -> sum of the digits elevaed to their own power
    '''
    d = digits_gen(num, base)
    if f is None:
        return sum(d)
    if is_number(f):
        p = f

        def f(x):
            return pow(x, p)

    try:
        return sum(map(f, d))
    except AttributeError:
        pass
    d = [f(x, i) for i, x in enumerate(d)]
    return sum(d)


def integer_exponent(a, b=10):
    '''
    :returns: int highest power of b that divides a.
    :see: https://reference.wolfram.com/language/ref/IntegerExponent.html
    '''
    res = 0
    for d in digits_gen(a, b):
        if d > 0:
            break
        res += 1
    return res


trailing_zeros = integer_exponent


def power_tower(v):
    '''
    :return: v[0]**v[1]**v[2] ...
    :see: http://ajcr.net#Python-power-tower/
    '''
    return functools.reduce(lambda x, y: y ** x, reversed(v))


def carries(a, b, base=10, pos=0):
    '''
    :return: int number of carries required to add a+b in base
    '''
    carry, answer = 0, 0  # we have no carry terms so far, and we haven't carried anything yet
    for one, two in itertools.zip_longest(digits_gen(a, base), digits_gen(b, base), fillvalue=0):
        carry = (one + two + carry) // base
        answer += carry > 0  # increment the number of carry terms, if we will carry again
    return answer


def powertrain(n):
    '''
    :return: v[0]**v[1]*v[2]**v[3] ...**(v[-1] or 0)
    :author: # Chai Wah Wu, Jun 16 2017
    :see: http://oeis.org/A133500
    '''
    s = str(n)
    k = len(s)
    m = int(s[-1]) if k % 2 else 1
    for i in range(0, k - 1, 2):
        m *= int(s[i]) ** int(s[i + 1])
    return m


def str_base(num, base=10, numerals='0123456789abcdefghijklmnopqrstuvwxyz'):
    '''
    :return: string representation of num in base
    :param num: int number (decimal)
    :param base: int base, 10 by default
    :param numerals: string with all chars representing numbers in base base. chars after the base-th are ignored
    '''
    if base < 2 or base > len(numerals):
        raise ValueError(
            "str_base: base must be between 2 and %d" % len(numerals))
    if base == 10 and numerals[:10] == '0123456789':
        return str(num)
    if base == 2 and numerals[:2] == '01':
        return "{0:b}".format(int(num))

    if num < 0:
        sign = '-'
        num = -num
    else:
        sign = ''

    result = ''
    for d in digits_gen(num, base):
        result = numerals[d] + result

    return sign + result


def int_base(num, base):
    '''
    :return: int representation of num in base
    :param num: int number (decimal)
    :param base: int base, <= 10
    '''
    return int(str_base(num, base))


def num_from_digits(digits, base=10):
    '''
    :param digits: string or list of digits representing a number in given base
    :param base: int base, 10 by default
    :return: int number
    '''

    if isinstance(digits, str):
        string = digits
    else:
        string = ''
        for x in digits:
            if x >= base:
                raise ValueError(
                    "num_from_digits: digit %d is greater than base %d" % (x, base))
            string += str_base(x, base)
    return int(string, base)


def reverse(i):
    return int(str(i)[::-1])


def is_palindromic(num, base=10):
    '''Check if 'num' in base 'base' is a palindrome, that's it, if it can be
    read equally from left to right and right to left.'''
    if base == 10:
        return num == reverse(num)
    digitslst = list(digits_gen(num, base))
    return digitslst == list(reversed(digitslst))


def is_anagram(num1, num2, base=10):
    '''Check if 'num1' and 'num2' have the same digits in base'''
    digits1 = sorted(str_base(num1, base))
    digits2 = sorted(str_base(num2, base))
    return digits1 == digits2


def is_pandigital(num, base=10):
    '''
    :return: True if num contains all digits in specified base
    '''
    n = str_base(num, base)
    return len(n) >= base and not '123456789abcdefghijklmnopqrstuvwxyz'[:base - 1].strip(n)
    # return set(sorted(digits_from_num(num,base))) == set(range(base)) #slow


def bouncy(n, up=False, down=False):
    '''
    :param n: int number to test
    :param up: bool
    :param down: bool

    bouncy(x) returns True for Bouncy numbers (digits form a strictly non-monotonic sequence) (A152054)
    bouncy(x,True,None) returns True for Numbers with digits in nondecreasing order (OEIS A009994)
    bouncy(x,None,True) returns True for Numbers with digits in nonincreasing order (OEIS A009996)
    '''
    s = str(n)
    s1 = ''.join(sorted(s))
    res = True
    if up is not None:
        res = res and up == (s == s1)
    if down is not None:
        res = res and down == (s == s1[::-1])
    return res


def repunit_gen(base=10, digit=1):
    '''generate repunits'''
    n = digit
    yield 0  # to be coherent with definition
    while True:
        yield n
        n = n * base + digit


def repunit(n, base=10, digit=1):
    '''
    :return: nth repunit
    '''
    if n == 0:
        return 0
    if digit == 1:
        return (base ** n - 1) // (base - 1)
    return int(str(digit) * n, base)

# repeating decimals https://en.wikipedia.org/wiki/Repeating_decimal
# https://stackoverflow.com/a/36531120/1395973


def rational_form(numerator, denominator):
    '''information about the decimal representation of a rational number.

    :return: 5 integer : integer, decimal, shift, repeat, cycle

    * shift is the len of decimal with leading zeroes if any
    * cycle is the len of repeat with leading zeroes if any
    '''

    def first_divisible_repunit(x):
        # finds the first number in the sequence (9, 99, 999, 9999, ...) that is divisible by x.
        assert x % 2 != 0 and x % 5 != 0
        for r in itertools2.drop(1, repunit_gen(digit=9)):
            if r % x == 0:
                return r

    shift, p = 0, 1
    for x in (10, 2, 5):
        while denominator % x == 0:
            denominator //= x
            numerator = 10 * numerator // x
            shift += 1
            p *= 10
    base, numerator = divmod(numerator, denominator)
    integer, decimal = divmod(base, p)
    repunit = first_divisible_repunit(denominator)
    repeat = numerator * (repunit // denominator)
    cycle = number_of_digits(repunit) if repeat else 0
    return integer, decimal, shift, repeat, cycle


def rational_str(n, d):
    integer, decimal, shift, repeat, cycle = rational_form(n, d)
    s = str(integer)
    if not (decimal or repeat):
        return s
    s = s + "."
    if decimal or shift:
        s = s + "{:0{}}".format(decimal, shift)
    if repeat:
        s = s + "({:0{}})".format(repeat, cycle)
    return s


def rational_cycle(num, den):
    '''periodic part of the decimal expansion of num/den. Any initial 0's are placed at end of cycle.

    :see: https://oeis.org/A036275
    '''
    _, _, _, digits, cycle = rational_form(num, den)
    lz = cycle - number_of_digits(digits)
    return digits * ipow(10, lz)

# polygonal numbers


def tetrahedral(n):
    '''
    :return: int n-th tetrahedral number
    :see: https://en.wikipedia.org/wiki/Tetrahedral_number
    '''
    return n * (n + 1) * (n + 2) // 6


def sum_of_squares(n):
    '''
    :return: 1^2 + 2^2 + 3^2 + ... + n^2
    :see: https://en.wikipedia.org/wiki/Square_pyramidal_number
    '''
    return n * (n + 1) * (2 * n + 1) // 6


pyramidal = sum_of_squares


def sum_of_cubes(n):
    '''
    :return: 1^3 + 2^3 + 3^3 + ... + n^3
    :see: https://en.wikipedia.org/wiki/Squared_triangular_number
    '''
    a = triangular(n)
    return a * a  # by Nicomachus's theorem


def bernouilli_gen(init=-1):
    '''generator of Bernouilli numbers

    :param init: int -1 or +1.
    * -1 for "first Bernoulli numbers" with B1=-1/2
    * +1 for "second Bernoulli numbers" with B1=+1/2
    https://en.wikipedia.org/wiki/Bernoulli_number
    https://rosettacode.org/wiki/Bernoulli_numbers#Python:_Optimised_task_algorithm
    '''
    B, m = [], 0
    while True:
        B.append(fractions.Fraction(1, m + 1))
        for j in range(m, 0, -1):
            B[j - 1] = j * (B[j - 1] - B[j])
        yield init * B[0] if m == 1 else B[0]  # (which is Bm)
        m += 1


def bernouilli(n, init=-1):
    return itertools2.takenth(n, bernouilli_gen(init))


def faulhaber(n, p):
    ''' sum of the p-th powers of the first n positive integers

    :return: 1^p + 2^p + 3^p + ... + n^p
    :see: https://en.wikipedia.org/wiki/Faulhaber%27s_formula
    '''
    s = 0
    for j, a in enumerate(bernouilli_gen(1)):
        if j > p:
            break
        s = s + binomial(p + 1, j) * a * n ** (p + 1 - j)
    return s // (p + 1)


def is_happy(n):
    # https://en.wikipedia.org/wiki/Happy_number
    while n > 1 and n != 89 and n != 4:
        n = digsum(n, 2)  # sum of squares of digits
    return n == 1


def lychrel_seq(n):
    while True:
        r = reverse(n)
        yield n, r
        if n == r:
            break
        n += r


def lychrel_count(n, limit=96):
    '''number of lychrel iterations before n becomes palindromic

    :param n: int number to test
    :param limit: int max number of loops.
        default 96 corresponds to the known most retarded non lychrel number
    :warning: there are palindrom lychrel numbers such as 4994
    '''
    for i in itertools.count():
        r = reverse(n)
        if r == n or i == limit:
            return i
        n = n + r


def is_lychrel(n, limit=96):
    '''
    :warning: there are palindrom lychrel numbers such as 4994
    '''
    r = lychrel_count(n, limit)
    if r >= limit:
        return True
    if r == 0:  # palindromic number...
        # ... can be lychrel !
        return lychrel_count(n + reverse(n), limit) + 1 >= limit
    return False


def polygonal(s, n):
    # https://en.wikipedia.org/wiki/Polygonal_number
    return ((s - 2) * n * n - (s - 4) * n) // 2


def triangle(n):
    '''
    :return: nth triangle number, defined as the sum of [1,n] values.
    :see: http://en.wikipedia.org/wiki/Triangular_number
    '''
    return polygonal(3, n)  # (n*(n+1))/2


triangular = triangle


def is_triangle(x):
    '''
    :return: True if x is a triangle number
    '''
    return is_square(1 + 8 * x)


is_triangular = is_triangle


def square(n):
    return polygonal(4, n)  # n*n


def pentagonal(n):
    '''
    :return: nth pentagonal number
    :see: https://en.wikipedia.org/wiki/Pentagonal_number
    '''
    return polygonal(5, n)  # n*(3*n - 1)/2


def is_pentagonal(n):
    '''
    :return: True if x is a pentagonal number
    '''
    if n < 1:
        return False
    n = 1 + 24 * n
    s = isqrt(n)
    if s * s != n:
        return False
    return is_integer((1 + s) / 6.0)


def hexagonal(n):
    '''
    :return: nth hexagonal number
    :see: https://en.wikipedia.org/wiki/Hexagonal_number
    '''
    return polygonal(6, n)  # n*(2*n - 1)


def is_hexagonal(n):
    return (1 + sqrt(1 + (8 * n))) % 4 == 0


def heptagonal(n):
    return polygonal(7, n)  # (n * (5 * n - 3)) / 2


def is_heptagonal(n):
    return (3 + sqrt(9 + (40 * n))) % 10 == 0


def octagonal(n):
    return polygonal(8, n)  # (n * (3 * n - 2))


def is_octagonal(n):
    return (2 + sqrt(4 + (12 * n))) % 6 == 0


@decorators.memoize
def partition(n):
    '''The partition function p(n)

    gives the number of partitions of a nonnegative integer n
    into positive integers.
    (There is one partition of zero into positive integers,
    i.e. the empty partition, since the empty sum is defined as 0.)

    :see: http://oeis.org/wiki/Partition_function https://oeis.org/A000041
    '''

    # TODO : http://code.activestate.com/recipes/218332-generator-for-integer-partitions/
    def non_zero_integers(n):
        for k in range(1, n):
            yield k
            yield -k

    if n == 0:
        return 1
    elif n < 0:
        return 0

    result = 0
    for k in non_zero_integers(n + 1):
        sign = 1 if (k - 1) % 2 == 0 else -1
        result += sign * partition(n - pentagonal(k))
    return result


@decorators.memoize
def partitionsQ(n, d=0):
    # http://mathworld.wolfram.com/PartitionFunctionQ.html
    # http://reference.wolfram.com/language/ref/PartitionsQ.html
    # https://oeis.org/A000009
    # https://codegolf.stackexchange.com/a/71945/17547

    if n == 0:
        return 1
    return sum(partitionsQ(n - k, n - 2 * k + 1) for k in range(1, n - d + 1))


numbers_en = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
    11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
    15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
    19: "nineteen", 20: "twenty", 30: "thirty", 40: "forty",
    50: "fifty", 60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety",
    100: "hundred",
    1000: "thousand",
    1000000: "million",
    1000000000: "billion",

}

numbers_fr = {
    0: "zero", 1: "un", 2: "deux", 3: "trois", 4: "quatre", 5: "cinq",
    6: "six", 7: "sept", 8: "huit", 9: "neuf", 10: "dix",
    11: "onze", 12: "douze", 13: "treize", 14: "quatorze",
    15: "quinze", 16: "seize", 17: "dix-sept", 18: "dix-huit",
    19: "dix-neuf", 20: "vingt", 30: "trente", 40: "quarante",
    50: "cinquante", 60: "soixante", 70: "soixante-dix", 80: "quatre-vingt", 90: "quatre-vingt-dix",
    100: "cent",
    1000: "mille",
    1000000: "million",
    1000000000: "milliard",
}

numbers_ch = numbers_fr
numbers_ch.update({70: "septante", 80: "huitante", 90: "nonante"})


def get_cardinal_name(num, numbers=numbers_en):
    '''Get cardinal name for number (0 to 1 million)'''

    if num in numbers:
        return numbers[num]

    def _get_tens(n):
        a, b = divmod(n, 10)
        return numbers[n] if (n in numbers) else "%s-%s" % (numbers[10 * a], numbers[b])

    def _get_hundreds(n):
        tens = n % 100
        hundreds = (n // 100) % 10
        return filter(bool, [
            hundreds > 0 and numbers[hundreds],
            hundreds > 0 and numbers[100],
            hundreds > 0 and tens and "and",
            (not hundreds or tens > 0) and _get_tens(tens),
        ])

    blocks = digits(num, 1000, rev=True)  # group by 1000
    res = ''
    for hdu, word in zip(blocks, ['', ' '+numbers[1000]+' ', ' '+numbers[1000000]+' ', ' ' + numbers[1000000000]+' ']):
        if hdu == 0:
            continue  # skip
        try:
            res = ' '.join(_get_hundreds(hdu)) + word + res
        except:
            pass
    return res


def abundance(n):
    return sigma(n) / n


def is_perfect(n):
    '''
    :return: -1 if n is deficient, 0 if perfect, 1 if abundant
    :see: https://en.wikipedia.org/wiki/Perfect_number,
    https://en.wikipedia.org/wiki/Abundant_number,
    https://en.wikipedia.org/wiki/Deficient_number
    '''
    # return sign(abundance(n)) #simple, but might be slow for large n
    for s in itertools2.accumulate(divisors(n)):
        if s > 2 * n:
            return 1
    return 0 if s == 2 * n else -1


def number_of_digits(num, base=10):
    '''Return number of digits of num (expressed in base 'base')'''
    # math.log(num,base) is imprecise, and len(str(num,base)) is slow and ugly
    num = abs(num)
    for i in itertools.count():
        if num < base:
            return i + 1
        num = num // base


def chakravala(n):
    '''solves x^2 - n*y^2 = 1 for x,y integers

    https://en.wikipedia.org/wiki/Pell%27s_equation
    https://en.wikipedia.org/wiki/Chakravala_method
    '''
    # https://github.com/timothy-reasa/Python-Project-Euler/blob/master/solutions/euler66.py

    m = 1
    k = 1
    a = 1
    b = 0

    while k != 1 or b == 0:
        m = k * (m // k + 1) - m
        m = m - int((m - sqrt(n)) // k) * k

        tempA = (a * m + n * b) // abs(k)
        b = (a + b * m) // abs(k)
        k = (m * m - n) // k

        a = tempA

    return a, b

# combinatorics


factorial = math.factorial  # didn't knew it was there...


def factorialk(n, k):
    '''Multifactorial of n of order k, n(!!...!).

    This is the multifactorial of n skipping k values.  For example,
      factorialk(17, 4) = 17!!!! = 17 * 13 * 9 * 5 * 1
    In particular, for any integer ``n``, we have
      factorialk(n, 1) = factorial(n)
      factorialk(n, 2) = factorial2(n)

    :param n: int Calculate multifactorial. If `n` < 0, the return value is 0.
    :param k : int Order of multifactorial.
    :return: int Multifactorial of `n`.
    '''
    # code from scipy, with extact=true
    if n < -1:
        return 0
    if n <= 0:
        return 1
    val = mul(range(n, 0, -k))
    return val


def factorial2(n):
    return factorialk(n, 2)


def factorial_gen(f=lambda x: x):
    '''Generator of factorial
    :param f: optional function to apply at each step
    '''
    last = 1
    yield last
    for n in itertools.count(1):
        last = f(last * n)
        yield last


def log_factorial(n):
    '''
    :return: float approximation of ln(n!) by Ramanujan formula
    '''
    return n * math.log(n) - n + (math.log(n * (1 + 4 * n * (1 + 2 * n)))) / 6 + math.log(math.pi) / 2


gamma = math.gamma  # didn't knew it was there...

# inverse gamma function from https://mathoverflow.net/a/98267/88768


def lambertW(z):
    """
    Lambert W function, principal branch.
    See http://en.wikipedia.org/wiki/Lambert_W_function
    Code taken from http://keithbriggs.info/software.html
    """
    eps = 4.0e-16
    em1 = 0.3678794411714423215955237701614608
    assert z >= -em1, 'lambertW: bad argument %g, exiting.' % z
    if 0.0 == z:
        return 0.0
    if z < -em1+1e-4:
        q = z+em1
        r = math.sqrt(q)
        q2 = q*q
        q3 = q2*q
        return\
            -1.0\
            + 2.331643981597124203363536062168*r\
            - 1.812187885639363490240191647568*q\
            + 1.936631114492359755363277457668*r*q\
            - 2.353551201881614516821543561516*q2\
            + 3.066858901050631912893148922704*r*q2\
            - 4.175335600258177138854984177460*q3\
            + 5.858023729874774148815053846119*r*q3\
            - 8.401032217523977370984161688514*q3*q
    if z < 1.0:
        p = math.sqrt(2.0*(2.7182818284590452353602874713526625*z+1.0))
        w = -1.0+p*(1.0+p*(-0.333333333333333333333
                           + p*0.152777777777777777777777))
    else:
        w = math.log(z)
    if z > 3.0:
        w -= math.log(w)
    for i in range(10):
        e = math.exp(w)
        t = w*e-z
        p = w+1.0
        t /= e*p-0.5*(p+1.0)*t/p
        w -= t
        if abs(t) < eps*(1.0+abs(w)):
            return w
    raise AssertionError('Unhandled value %1.2f' % z)


def gamma_inverse(x):
    """
    Inverse the gamma function.
    http://mathoverflow.net/questions/12828/inverse-gamma-function
    """
    k = 1.461632  # the positive zero of the digamma function, scipy.special.psi
    assert x >= k, 'gamma(x) is strictly increasing for x >= k, k=%1.2f, x=%1.2f' % (
        k, x)

    C = math.sqrt(2*math.pi)/math.e - gamma(k)  # approximately 0.036534
    L = math.log((x+C)/sqrt(2*math.pi))
    gamma_inv = 0.5+L/lambertW(L/math.e)
    return gamma_inv


def binomial(n, k):
    '''binomial coefficient "n choose k"
    :param: n, k int
    :return: int, number of ways to chose n items in k, unordered

    :see: https://en.wikipedia.org/wiki/binomial
    '''
    # return factorial(n) // (factorial(k) * factorial(n - k)) # is very slow
    # code from https://en.wikipedia.org/wiki/binomial#binomial_in_programming_languages
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)  # take advantage of symmetry
    if k > 1e8:
        raise OverflowError('k=%d too large' % k)
    c = 1
    for i in range(k):
        c = c * (n - i) // (i + 1)
    return int(c)


choose = binomial  # alias
ncombinations = binomial  # alias


def binomial_exponent(n, k, p):
    '''
    :return: int largest power of p that divides binomial(n,k)
    '''
    if is_prime(p):
        # https://en.wikipedia.org/wiki/Kummer%27s_theorem
        return carries(k, n - k, p)

    return min(binomial_exponent(n, k, a) // b for a, b in factorize(p))


def log_binomial(n, k):
    '''
    :return: float approximation of ln(binomial(n,k))
    '''
    return log_factorial(n) - log_factorial(k) - log_factorial(n - k)


def ilog(a, b, upper_bound=False):
    '''discrete logarithm x such that b^x=a

    :parameter a,b: integer
    :parameter upper_bound: bool. if True, returns smallest x such that b^x>=a
    :return: x integer such that b^x=a, or upper_bound, or None
    https://en.wikipedia.org/wiki/Discrete_logarithm
    '''
    # TODO: implement using baby_step_giant_step or http://anh.cs.luc.edu/331/code/PohligHellman.py or similar
    # for now it's brute force...
    i = 0
    while a >= b:
        a //= b
        i += 1
    return i

    p = 1
    for x in itertools.count():
        if p == a:
            return x
        if p > a:
            return x if upper_bound else None
        p = b * p

# from "the right way to calculate stuff" : http://www.plunk.org/~hatch/rightway.php


def angle(u, v, unit=True):
    '''
    :param u,v: iterable vectors
    :param unit: bool True if vectors are unit vectors. False increases computations
    :returns: float angle n radians between u and v unit vectors i
    '''
    if not unit:
        u = vecunit(u)
        v = vecunit(v)
    if dot_vv(u, v) >= 0:
        return 2. * math.asin(dist(v, u) / 2)
    else:
        return math.pi - 2. * math.asin(dist(vecneg(v), u) / 2)


def sin_over_x(x):
    '''numerically safe sin(x)/x'''
    if 1. + x * x == 1.:
        return 1.
    else:
        return math.sin(x) / x


def slerp(u, v, t):
    '''spherical linear interpolation

    :param u,v: 3D unit vectors
    :param t: float in [0,1] interval
    :return: vector interpolated between u and v
    '''
    a = angle(u, v)
    fu = (1 - t) * sin_over_x((1 - t) * a) / sin_over_x(a)
    fv = t * sin_over_x(t * a) / sin_over_x(a)
    return vecadd([fu * x for x in u], [fv * x for x in v])


# interpolations
def proportional(nseats, votes):
    '''assign n seats proportionaly to votes using the https://en.wikipedia.org/wiki/Hagenbach-Bischoff_quota method

    :param nseats: int number of seats to assign
    :param votes: iterable of int or float weighting each party
    :result: list of ints seats allocated to each party
    '''
    quota = sum(votes) / (1. + nseats)  # force float
    frac = [vote / quota for vote in votes]
    res = [int(f) for f in frac]
    n = nseats - sum(res)  # number of seats remaining to allocate
    if n == 0:
        return res  # done
    if n < 0:
        # to handle case where votes=[0,0,..,1,0,...,0]
        return [min(x, nseats) for x in res]
    # give the remaining seats to the n parties with the largest remainder
    remainders = vecsub(frac, res)
    limit = sorted(remainders, reverse=True)[n - 1]
    for i, r in enumerate(remainders):
        if r >= limit:
            res[i] += 1
            n -= 1  # attempt to handle perfect equality
            if n == 0:
                return res  # done


def triangular_repartition(x, n):
    ''' divide 1 into n fractions such that:

    - their sum is 1
    - they follow a triangular linear repartition (sorry, no better name for now) where x/1 is the maximum
    '''

    def _integral(x1, x2):
        '''return integral under triangle between x1 and x2'''
        if x2 <= x:
            return (x1 + x2) * float(x2 - x1) / x
        elif x1 >= x:
            return (2 - x1 - x2) * float(x1 - x2) / (x - 1)
        else:  # top of the triangle:
            return _integral(x1, x) + _integral(x, x2)

    w = 1. / n  # width of a slice
    return [_integral(i * w, (i + 1) * w) for i in range(n)]


def rectangular_repartition(x, n, h):
    ''' divide 1 into n fractions such that:

    - their sum is 1
    - they follow a repartition along a pulse of height h<1
    '''
    w = 1. / n  # width of a slice and of the pulse
    x = max(x, w / 2.)
    x = min(x, 1 - w / 2.)
    xa, xb = x - w / 2, x + w / 2.  # start,end of the pulse
    o = (1. - h) / (n - 1)  # base level

    def _integral(x1, x2):
        '''return integral between x1 and x2'''
        if x2 <= xa or x1 >= xb:
            return o
        elif x1 < xa:
            return float(o * (xa - x1) + h * (w - (xa - x1))) / w
        else:  # x1<=xb
            return float(h * (xb - x1) + o * (w - (xb - x1))) / w

    return [_integral(i * w, (i + 1) * w) for i in range(n)]


def de_bruijn(k, n):
    '''
    De Bruijn sequence for alphabet k and subsequences of length n.

    https://en.wikipedia.org/wiki/De_Bruijn_sequence
    '''
    try:
        # let's see if k can be cast to an integer;
        # if so, make our alphabet a list
        _ = int(k)
        alphabet = list(map(str, range(k)))

    except (ValueError, TypeError):
        alphabet = k
        k = len(k)

    a = [0] * k * n
    sequence = []

    def db(t, p):
        if t > n:
            if n % p == 0:
                sequence.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)

    db(1, 1)
    return "".join(alphabet[i] for i in sequence)


'''modular arithmetic
initial motivation: https://www.hackerrank.com/challenges/ncr

code translated from http://comeoncodeon.wordpress.com/2011/07/31/combination/
see also http://userpages.umbc.edu/~rcampbel/Computers/Python/lib/numbthy.py

mathematica code from http://thales.math.uqam.ca/~rowland/packages/BinomialCoefficients.m
'''

# see http://anh.cs.luc.edu/331/code/mod.py for a MOD class


def mod_inv(a, b):
    # http://rosettacode.org/wiki/Chinese_remainder_theorem#Python
    if is_prime(b):  # Use Euler's Theorem
        return ipow(a, b - 2, b)
    b0 = b
    x0, x1 = 0, 1
    if b == 1:
        return 1
    while a > 1:
        q = a // b
        a, b = b, a % b
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += b0
    return x1


def mod_div(a, b, m):
    '''
    :return: x such that (b*x) mod m = a mod m
    '''
    return a * mod_inv(b, m)


def mod_fact(n, m):
    '''
    :return: n! mod m
    '''
    res = 1
    while n > 0:
        for i in range(2, n % m + 1):
            res = (res * i) % m
        n = n // m
        if n % 2 > 0:
            res = m - res
    return res % m


def chinese_remainder(m, a):
    '''http://en.wikipedia.org/wiki/Chinese_remainder_theorem

    :param m: list of int moduli
    :param a: list of int remainders
    :return: smallest int x such that x mod ni=ai
    '''
    # http://rosettacode.org/wiki/Chinese_remainder_theorem#Python
    res = 0
    prod = mul(m)
    for m_i, a_i in zip(m, a):
        p = prod // m_i
        res += a_i * mod_inv(p, m_i) * p
    return res % prod


def _count(n, p):
    '''
    :return: power of p in n
    '''
    k = 0
    while n >= p:
        k += n // p
        n = n // p
    return k


def mod_binomial(n, k, m, q=None):
    '''calculates C(n,k) mod m for large n,k,m

    :param n: int total number of elements
    :param k: int number of elements to pick
    :param m: int modulo (or iterable of (m,p) tuples used internally)
    :param q: optional int power of m for prime m, used internally
    '''
    # the function implements 3 cases which are called recursively:
    # 1 : m is factorized in powers of primes pi^qi
    # 2 : Chinese remainder theorem is used to combine all C(n,k) mod pi^qi
    # 3 : Lucas or Andrew Granville's theorem is used to calculate  C(n,k) mod pi^qi

    if type(m) is int:
        if q is None:
            return mod_binomial(n, k, factorize(m))

        # 3
        elif q == 1:  # use http://en.wikipedia.org/wiki/Lucas'_theorem
            ni = digits_gen(n, m)
            ki = digits_gen(k, m)
            res = 1
            for a, b in zip(ni, ki):
                res *= binomial(a, b)
                if res == 0:
                    break
            return res
        # see http://codechef17.rssing.com/chan-12597213/all_p5.html
        '''
        elif q==3:
            return mod_binomial(n*m,k*m,m)
        '''
        # no choice for the moment....
        return binomial(n, k) % (m ** q)

    else:  # 2
        # use http://en.wikipedia.org/wiki/Chinese_remainder_theorem
        r, f = [], []
        for p, q in m:
            r.append(mod_binomial(n, k, p, q))
            f.append(p ** q)
        return chinese_remainder(f, r)


def baby_step_giant_step(y, a, n):
    ''' solves Discrete Logarithm Problem (DLP) y = a**x mod n
    '''
    # http://l34rn-p14y.blogspot.it/2013/11/baby-step-giant-step-algorithm-python.html
    s = int(math.ceil(math.sqrt(n)))
    A = [y * pow(a, r, n) % n for r in range(s)]
    for t in range(1, s + 1):
        value = pow(a, t * s, n)
        if value in A:
            return (t * s - A.index(value)) % n

# inspired from http://stackoverflow.com/questions/28548457/nth-fibonacci-number-for-n-as-big-as-1019


def mod_matmul(A, B, mod=0):
    if not mod:
        return dot_mm(A, B)
    return [[sum(a * b for a, b in zip(A_row, B_col)) % mod for B_col in zip(*B)] for A_row in A]


def mod_matpow(M, power, mod=0):
    if power < 0:
        raise NotImplementedError
    result = identity(2)
    for power in digits(power, 2, True):
        if power:
            result = mod_matmul(result, M, mod)
        M = mod_matmul(M, M, mod)
    return result

# in fact numpy.linalg.matrix_power has a bug for large powers
# https://github.com/numpy/numpy/issues/5166
# so our function here above is better :-)


matrix_power = mod_matpow


def mod_sqrt(n, p):
    '''modular sqrt(n) mod p
    '''
    assert is_prime(p), 'p must be prime'
    a = n % p
    if p % 4 == 3:
        return pow(a, (p + 1) >> 2, p)
    elif p % 8 == 5:
        v = pow(a << 1, (p - 5) >> 3, p)
        i = ((a * v * v << 1) % p) - 1
        return (a * v * i) % p
    elif p % 8 == 1:  # Shank's method
        q, e = p - 1, 0
        while q & 1 == 0:
            e += 1
            q >>= 1
        n = 2
        while legendre(n, p) != -1:
            n += 1
        w, x, y, r = pow(a, q, p), pow(a, (q + 1) >> 1, p), pow(n, q, p), e
        while True:
            if w == 1:
                return x
            v, k = w, 0
            while v != 1 and k + 1 < r:
                v = (v * v) % p
                k += 1
            if k == 0:
                return x
            d = pow(y, 1 << (r - k - 1), p)
            x, y = (x * d) % p, (d * d) % p
            w, r = (w * y) % p, k
    else:
        return a  # p == 2


def mod_fac(n, mod, mod_is_prime=False):
    '''modular factorial
    : return n! % modulo
    if module is prime, use Wilson's theorem
    https://en.wikipedia.org/wiki/Wilson%27s_theorem
    '''
    if n >= mod:  # then mod is a factor of n!
        return 0

    if n < 20:  # for small n the naive algorithm can be faster
        return factorial(n) % mod

    # use Wilson's Theorem : (n-1)! == -1 (mod modulo)
    if mod_is_prime or is_prime(mod):
        # avoid negative numbers:  -1 == modulo - 1 (mod modulo)
        result = mod - 1
        for i in range(mod - 1, n, -1):
            result *= mod_inv(i, mod)
            result %= mod
        return result
    else:
        return itertools2.nth(n, factorial_gen(lambda x: x % mod))


def pi_digits_gen():
    ''' generates pi digits as a sequence of INTEGERS !
    using Jeremy Gibbons spigot generator

    :see :http://www.cs.ox.ac.uk/people/jeremy.gibbons/publications/spigot.pdf
    '''
    # code from http://davidbau.com/archives/2010/03/14/python_pipy_spigot.html
    q, r, t, j = 1, 180, 60, 2
    while True:
        u, y = 3 * (3 * j + 1) * (3 * j + 2), \
            (q * (27 * j - 12) + 5 * r) // (5 * t)
        yield y
        q, r, t, j = 10 * q * j * (2 * j - 1), \
            10 * u * (q * (5 * j - 2) + r - y * t), \
            t * u, \
            j + 1


def lucky_gen():
    '''
    generates lucky numbers
    :see: https://en.wikipedia.org/wiki/Lucky_number
    :see: https://oeis.org/A000959
    '''

    # https://stackoverflow.com/a/22281524/1395973

    def _idx_after_removal(removed_indices, value):
        for removed in removed_indices:
            value -= value // removed
        return value

    def _should_be_excluded(removed_indices, value):
        for j in range(len(removed_indices) - 1):
            value_idx = _idx_after_removal(removed_indices[:j + 1], value)
            if value_idx % removed_indices[j + 1] == 0:
                return True
        return False

    yield 1
    removed_indices = [2]
    for i in itertools.count(3, 2):
        if not _should_be_excluded(removed_indices, i):
            yield i
            removed_indices.append(i)
            # removed_indices = list(set(removed_indices))
            # removed_indices.sort()
# ------------------------------------------------------------------------------
# factorization code taken from https://pypi.python.org/pypi/primefac
#
# http://programmingpraxis.com/2010/04/23/modern-elliptic-curve-factorization-part-1/
# http://programmingpraxis.com/2010/04/27/modern-elliptic-curve-factorization-part-2/
# ------------------------------------------------------------------------------


def pfactor(n):
    '''Helper function for sprp.

    Returns the tuple (x,y) where n - 1 == (2 ** x) * y and y is odd.
    We have this bit separated out so that we don’t waste time
    recomputing s and d for each base when we want to check n against multiple bases.
    '''
    # https://pypi.python.org/pypi/primefac
    s, d, q = 0, n - 1, 2
    while not d & q - 1:
        s, q = s + 1, q * 2
    return s, d // (q // 2)


def sprp(n, a, s=None, d=None):
    '''Checks n for primality using the Strong Probable Primality Test to base a.
    If present, s and d should be the first and second items, respectively,
    of the tuple returned by the function pfactor(n)'''
    # https://pypi.python.org/pypi/primefac
    if n % 2 == 0:
        return False
    if (s is None) or (d is None):
        s, d = pfactor(n)
    x = pow(a, d, n)
    if x == 1:
        return True
    for i in range(s):
        if x == n - 1:
            return True
        x = pow(x, 2, n)
    return False


def jacobi(a, p):
    '''Computes the Jacobi symbol (a|p), where p is a positive odd number.
    :see: https://en.wikipedia.org/wiki/Jacobi_symbol
    '''
    # https://pypi.python.org/pypi/primefac
    if (p % 2 == 0) or (p < 0):
        return None  # p must be a positive odd number
    if (a == 0) or (a == 1):
        return a
    a, t = a % p, 1
    while a != 0:
        while not a & 1:
            a //= 2
            if p & 7 in (3, 5):
                t *= -1
        a, p = p, a
        if (a & 3 == 3) and (p & 3) == 3:
            t *= -1
        a %= p
    return t if p == 1 else 0


def pollardRho_brent(n):
    '''Brent’s improvement on Pollard’s rho algorithm.

    :return: int n if n is prime
    otherwise, we keep chugging until we find a factor of n strictly between 1 and n.
    :see: https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm
    '''

    if is_prime(n):
        return n
    g = n
    while g == n:
        y, c, m, g, r, q = random.randrange(1, n), random.randrange(
            1, n), random.randrange(1, n), 1, 1, 1
        while g == 1:
            x, k = y, 0
            for i in range(r):
                y = (y ** 2 + c) % n
            while k < r and g == 1:
                ys = y
                for i in range(min(m, r - k)):
                    y = (y ** 2 + c) % n
                    q = q * abs(x - y) % n
                g, k = gcd(q, n), k + m
            r *= 2
        if g == n:
            while True:
                ys = (ys ** 2 + c) % n
                g = gcd(abs(x - ys), n)
                if g > 1:
                    break
    return g


# TODO: What are the best default bounds and way to increment them?
def pollard_pm1(n, B1=100, B2=1000):
    '''Pollard’s p+1 algorithm, two-phase version.

    :return: n if n is prime; otherwise, we keep chugging until we find a factor of n strictly between 1 and n.
    '''
    if is_prime(n):
        return n
    m = is_power(n)
    if m:
        return m
    while True:
        pg = primes_gen()
        q = 2  # TODO: what about other initial values of q?
        p = pg.next()
        while p <= B1:
            q, p = pow(q, p ** ilog(B1, p), n), pg.next()
        g = gcd(q - 1, n)
        if 1 < g < n:
            return g
        while p <= B2:
            q, p = pow(q, p, n), pg.next()
        g = gcd(q - 1, n)
        if 1 < g < n:
            return g
        # These bounds failed.  Increase and try again.
        B1 *= 10
        B2 *= 10


def mlucas(v, a, n):
    ''' Helper function for williams_pp1().
    Multiplies along a Lucas sequence modulo n.
    '''
    v1, v2 = v, (v ** 2 - 2) % n
    for bit in bin(a)[3:]:
        if bit == "0":
            v1, v2 = ((v1 ** 2 - 2) % n, (v1 * v2 - v) % n)
        else:
            v1, v2 = ((v1 * v2 - v) % n, (v2 ** 2 - 2) % n)
    return v1


def williams_pp1(n):
    '''Williams’ p+1 algorithm.
    :return: n if n is prime
    otherwise, we keep chugging until we find a factor of n strictly between 1 and n.
    '''
    if is_prime(n):
        return n
    m = is_power(n)
    if m:
        return m
    for v in itertools.count(1):
        for p in primes_gen():
            e = ilog(isqrt(n), p)
            if e == 0:
                break
            for _ in range(e):
                v = mlucas(v, p, n)
            g = gcd(v - 2, n)
            if 1 < g < n:
                return g
            if g == n:
                break


def ecadd(p1, p2, p0, n):
    # Add two points p1 and p2 given point P0 = P1-P2 modulo n
    x1, z1 = p1
    x2, z2 = p2
    x0, z0 = p0
    t1, t2 = (x1 - z1) * (x2 + z2), (x1 + z1) * (x2 - z2)
    return (z0 * pow(t1 + t2, 2, n) % n, x0 * pow(t1 - t2, 2, n) % n)


def ecdub(p, A, n):
    # double point p on A modulo n
    x, z = p
    An, Ad = A
    t1, t2 = pow(x + z, 2, n), pow(x - z, 2, n)
    t = t1 - t2
    return (t1 * t2 * 4 * Ad % n, (4 * Ad * t2 + t * An) * t % n)


def ecmul(m, p, A, n):
    # multiply point p by m on curve A modulo n
    if m == 0:
        return (0, 0)
    elif m == 1:
        return p
    else:
        q = ecdub(p, A, n)
        if m == 2:
            return q
        b = 1
        while b < m:
            b *= 2
        b //= 4
        r = p
        while b:
            if m & b:
                q, r = ecdub(q, A, n), ecadd(q, r, p, n)
            else:
                q, r = ecadd(r, q, p, n), ecdub(r, A, n)
            b //= 2
        return r


def factor_ecm(n, B1=10, B2=20):
    ''' Factors n using the elliptic curve method,
    using Montgomery curves and an algorithm analogous
    to the two-phase variant of Pollard’s p-1 method.
    :return: n if n is prime
    otherwise, we keep chugging until we find a factor of n strictly between 1 and n

    '''
    # TODO: Determine the best defaults for B1 and B2 and the best way to increment them and iters
    # TODO: We currently compute the prime lists from the sieve as we need them, but this means that we recompute them at every
    #       iteration.  While it would not be particularly efficient memory-wise, we might be able to increase time-efficiency
    #       by computing the primes we need ahead of time (say once at the beginning and then once each time we increase the
    #       bounds) and saving them in lists, and then iterate the inner while loops over those lists.
    if is_prime(n):
        return n
    m = is_power(n)
    if m:
        return m
    iters = 1
    while True:
        for _ in range(iters):  # TODO: multiprocessing?
            # TODO: Do we really want to call the randomizer?  Why not have seed be a function of B1, B2, and iters?
            # TODO: Are some seeds better than others?
            seed = random.randrange(6, n)
            u, v = (seed ** 2 - 5) % n, 4 * seed % n
            p = pow(u, 3, n)
            Q, C = (pow(v - u, 3, n) * (3 * u + v) %
                    n, 4 * p * v % n), (p, pow(v, 3, n))
            pg = primes_gen()
            p = next(pg)
            while p <= B1:
                Q, p = ecmul(p ** ilog(B1, p), Q, C, n), next(pg)
            g = gcd(Q[1], n)
            if 1 < g < n:
                return g
            while p <= B2:
                # "There is a simple coding trick that can speed up the second stage. Instead of multiplying each prime times Q,
                # we iterate over i from B1 + 1 to B2, adding 2Q at each step; when i is prime, the current Q can be accumulated
                # into the running solution. Again, we defer the calculation of the greatest common divisor until the end of the
                # iteration.
                # TODO: Implement this trick and compare performance.
                Q = ecmul(p, Q, C, n)
                g *= Q[1]
                g %= n
                p = next(pg)
            g = gcd(g, n)
            if 1 < g < n:
                return g
            # This seed failed.  Try again with a new one.
        # These bounds failed.  Increase and try again.
        B1 *= 3
        B2 *= 3
        iters *= 2


# legendre symbol (a|m)
# TODO: which is faster?
def legendre(a, p):
    '''Functions to comptue the Legendre symbol (a|p).
    The return value isn’t meaningful if p is composite
    :see: https://en.wikipedia.org/wiki/Legendre_symbol
    '''
    return ((pow(a, (p - 1) >> 1, p) + 1) % p) - 1


def legendre2(a, p):  # TODO: pretty sure this computes the Jacobi symbol
    '''Functions to comptue the Legendre symbol (a|p).
    The return value isn’t meaningful if p is composite
    :see: https://en.wikipedia.org/wiki/Legendre_symbol
    '''
    if a == 0:
        return 0
    x, y, L = a, p, 1
    while 1:
        if x > (y >> 1):
            x = y - x
            if y & 3 == 3:
                L = -L
        while x & 3 == 0:
            x >>= 2
        if x & 1 == 0:
            x >>= 1
            if y & 7 == 3 or y & 7 == 5:
                L = -L
        if x == 1:
            return ((L + 1) % p) - 1
        if x & 3 == 3 and y & 3 == 3:
            L = -L
        x, y = y % x, x
