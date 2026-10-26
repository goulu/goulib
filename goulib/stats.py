"""
very basic statistics functions
"""

__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2012, Philippe Guglielmetti"
__credits__ = []
__license__ = "LGPL"

import math
import logging
import matplotlib

from goulib import plot  # sets matplotlib backend
import matplotlib.pyplot as plt  # after import .plot

from goulib import itertools2, math2, expr


def mean_var(data):
    """mean and variance by stable algorithm
    :param
    :return: float (mean, variance) of data
    uses a stable algo by Knuth
    """
    # https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Online_algorithm
    n = 0
    mean = 0
    M2 = 0

    for x in data:
        n += 1
        delta = x - mean
        mean += delta / n
        M2 += delta * (x - mean)

    if n < 2:
        return mean, float('nan')
    else:
        return mean, M2 / (n - 1)


def mean(data):
    """:return: mean of data"""
    return mean_var(data)[0]


avg = mean  # alias


def variance(data):
    """:return: variance of data, faster (?) if mean is already available"""
    return mean_var(data)[1]


var = variance  # alias


def stddev(data):
    """:return: standard deviation of data"""
    return math.sqrt(variance(data))


def confidence_interval(data, conf=0.95):
    """:return: (low,high) bounds of 95% confidence interval of data"""
    m, v = mean_var(data)
    e = 1.96 * math.sqrt(v) / math.sqrt(len(data))
    return m - e, m + e


def median(data, is_sorted=False):
    """:return: median of data"""
    x = data if is_sorted else sorted(data)
    n = len(data)
    i = n // 2
    if n % 2:
        return x[i]
    else:
        return avg(x[i - 1:i + 1])


def mode(data, is_sorted=False):
    """:return: mode (most frequent value) of data"""
    # we could use a collection.Counter, but we're only looking for the largest value
    x = data if is_sorted else sorted(data)
    res, count = None, 0
    prev, c = None, 0
    x.append(None)  # to force the last loop
    for v in x:
        if v == prev:
            c += 1
        else:
            if c > count:  # best so far
                res, count = prev, c
            c = 1
        prev = v
    x.pop()  # no side effect please
    return res


def kurtosis(data):
    # https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
    n = 0
    mean = 0
    M2 = 0
    M3 = 0
    M4 = 0

    for x in data:
        n1 = n
        n = n + 1
        delta = x - mean
        delta_n = delta / n
        delta_n2 = delta_n * delta_n
        term1 = delta * delta_n * n1
        mean = mean + delta_n
        M4 = M4 + term1 * delta_n2 * \
            (n * n - 3 * n + 3) + 6 * delta_n2 * M2 - 4 * delta_n * M3
        M3 = M3 + term1 * delta_n * (n - 2) - 3 * delta_n * M2
        M2 = M2 + term1

    kurtosis = (n * M4) / (M2 * M2) - 3
    return kurtosis


def covariance(data1, data2):
    # https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Covariance
    mean1 = mean2 = 0
    M12 = 0
    n = len(data1)
    for i in range(n):
        delta1 = (data1[i] - mean1) / (i + 1)
        mean1 += delta1
        delta2 = (data2[i] - mean2) / (i + 1)
        mean2 += delta2
        M12 += i * delta1 * delta2 - M12 / (i + 1)
    return n / (n - 1.) * M12


def stats(l):
    """:return: min,max,sum,sum2,avg,var of a list"""
    s = Stats(l)
    return s.lo, s.hi, s.sum1, s.sum2, s.avg, s.var


class Stats(object):
    """an object that computes mean, variance and modes of data that is appended to it
    as in a list (but actual values are not stored)
    """

    def __init__(self, data=[], mean=None, var=None):
        self.lo = float("inf")
        self.hi = float("-inf")
        self.n = 0
        self._offset = 0
        self._dsum1 = 0
        self._dsum2 = 0
        if not data:
            s2 = math.sqrt(var / 2)
            data = [mean - s2, mean + s2]
        self.extend(data)

    def __repr__(self):
        return "{}(mean={:.12g}, var={:.12g})".format(self.__class__.__name__, self.mu, self.var)

    def append(self, x):
        """add data x to Stats"""
        if (self.n == 0):
            self._offset = x
        self.n += 1
        delta = x - self._offset
        self._dsum1 += delta
        self._dsum2 += delta * delta

        if x < self.lo:
            self.lo = x
        if x > self.hi:
            self.hi = x

    def extend(self, data):
        for x in data:
            self.append(x)

    def remove(self, data):
        """remove data from Stats
        :param data: value or iterable of values
        """
        if not hasattr(data, '__iter__'):
            data = [data]
        for x in data:
            self.n -= 1
            delta = x - self._offset
            self._dsum1 -= delta
            self._dsum2 -= delta * delta

            if x <= self.lo:
                logging.warning('lo value possibly invalid')
            if x >= self.hi:
                logging.warning('hi value possibly invalid')

    @property
    def sum(self):
        return self._offset * self.n + self._dsum1

    sum1 = sum  # alias

    @property
    def sum2(self):
        return self._dsum2 + self._offset * (2 * self.sum - self.n * self._offset)

    @property
    def mean(self):
        return self._offset + self._dsum1 / self.n

    avg = mean  # alias
    average = mean  # alias
    mu = mean  # alias

    @property
    def variance(self):
        if self.n < 2:  # variance of a single data...
            return 0
        return (self._dsum2 - (self._dsum1 * self._dsum1) / self.n) / (self.n - 1)

    var = variance  # alias

    @property
    def stddev(self):
        return math.sqrt(self.variance)

    sigma = stddev

    def __add__(self, other):
        if math2.is_number(other):
            other = Stats([other])
        # https://fr.wikipedia.org/wiki/Variance_(statistiques_et_probabilit%C3%A9s)#Produit
        try:
            cov = covariance(self, other)
        except:
            cov = 0
        mean = (self.mean + other.mean) / 2  # TODO : improve
        var = self.variance + other.variance + 2 * cov
        return Stats(mean=mean, var=var)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if math2.is_number(other):
            mean = self.mean
            var = other * self.variance
        else:  # it's a Stat
            mean = self.mean * other.mean
            # https://fr.wikipedia.org/wiki/Variance_(statistiques_et_probabilit%C3%A9s)#Produit
            var = self.variance * other.variance + \
                self.variance * other.mean ** 2 + other.variance * self.mean ** 2
        return Stats(mean=mean, var=var)

    def __neg__(self):
        return self * (-1)

    def __pow__(self, n):
        from copy import copy
        res = copy(self)
        while n > 1:
            res = res * self
            n -= 1
        return res

    def covariance(self, other):
        xy = (self - self.mean) * (other - other.mean)
        return xy.mean


class Discrete(Stats):
    """discrete probability density function"""

    def __init__(self, data):
        """
        :param data: can be:

            * list of equiprobable values (uniform distribution)
            * dict of x:p values:probability pairs
        """
        n = len(data)
        if not isinstance(data, dict):  # uniform distribution
            data = list(data)
            data = {i: 1 / n for i in data}
        Stats.__init__(self, [x * data[x] * n for x in data])
        self.pdf = data

    def __call__(self, x):
        if itertools2.isiterable(x):
            return (self(x) for x in x)
        if x in self.pdf:
            return self.pdf[x]
        else:
            return 0


class PDF(expr.Expr, Stats):
    """probability density function"""

    def __init__(self, pdf, data=[]):
        Stats.__init__(self, data)
        self.pdf = pdf
        expr.Expr.__init__(self, pdf)

    def __call__(self, x=None, **kwargs):
        if itertools2.isiterable(x):
            return (self(x) for x in x)
        return self.pdf(x)


def normal_pdf(x, mu, sigma):
    """Return the probability density function at x"""
    try:
        return 1. / (math.sqrt(2 * math.pi) * sigma) * math.exp(-0.5 * (1. / sigma * (x - mu)) ** 2)
    except ZeroDivisionError:
        return 1 if math2.isclose(x, mean) else 0


expr.default_context.add_function(normal_pdf)  # add to allowed functions


class Normal(PDF):
    """represents a normal distributed variable
    the base class (list) optionally contains data
    """

    def __init__(self, data=[], mean=0, var=1):
        """if data is specified, it it used to fit a normal law"""
        sigma = math.sqrt(var)
        s2 = math.sqrt(var / 2)
        # this way we preserve mean and variance
        data = data or [mean - s2, mean + s2]
        super(Normal, self).__init__(
            lambda x: normal_pdf(x, mean, sigma), data)

    def __str__(self):
        return Stats.__repr__(self)

    def latex(self):
        mean = expr.Expr(self.mean).latex()
        sigma = expr.Expr(self.sigma).latex()
        return r"\mathcal{N}(\mu=%s, \sigma=%s)" % (mean, sigma)

    def _plot(self, ax, x=None, **kwargs):
        if x is None:
            x = itertools2.linspace(
                self.mu - 3 * self.sigma, self.mu + 3 * self.sigma, 101)
        x = list(x)
        y = list(self(x))
        return expr.Expr._plot(self, ax, x, y, **kwargs)

    def linear(self, a, b=0):
        """
        :return: a*self+b
        """
        return Normal(mean=self.mean * a + b, var=abs(self.var * a))

    def __mul__(self, a):
        return self.linear(a, 0)

    def __div__(self, a):
        return self.linear(1. / a, 0)

    __truediv__ = __div__

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return self.linear(1, other)
        # else: assume other is a Normal variable
        mean = self.mean + other.mean
        var = self.var + other.var + 2 * self.cov(other)
        return Normal(mean=mean, var=var)

    def __radd__(self, other):
        return self + other

    def __neg__(self):
        return self * (-1)

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return -(self - other)

    def covariance(self, other):
        try:
            return mean(
                math2.vecmul(
                    math2.vecsub(self, [], self.mean),
                    math2.vecsub(other, [], other.mean)
                )
            )
        except:
            return 0  # consider decorrelated

    cov = covariance  # alias

    def pearson(self, other):
        return self.cov(other) / (self.stddev * other.stddev)

    correlation = pearson  # alias
    corr = pearson  # alias


def linear_regression(x, y, conf=None):
    """
    :param x,y: iterable data
    :param conf: float confidence level [0..1]. If None, confidence intervals are not returned
    :return: b0,b1,b2, (b0

    Return the linear regression parameters and their <prob> confidence intervals.

    ex:
    >>> linear_regression([.1,.2,.3],[10,11,11.5],0.95)
    """
    # https://gist.github.com/riccardoscalco/5356167
    try:
        import scipy.stats
        import numpy  # TODO remove these requirements
    except:
        logging.error('scipy needed')
        return None

    x = numpy.array(x)
    y = numpy.array(y)
    n = len(x)
    xy = x * y
    xx = x * x

    # estimates

    b1 = (xy.mean() - x.mean() * y.mean()) / (xx.mean() - x.mean() ** 2)
    b0 = y.mean() - b1 * x.mean()
    s2 = 1. / n * sum([(y[i] - b0 - b1 * x[i]) ** 2 for i in range(n)])

    if not conf:
        return b1, b0, s2

    # confidence intervals

    alpha = 1 - conf
    c1 = scipy.stats.chi2.ppf(alpha / 2., n - 2)
    c2 = scipy.stats.chi2.ppf(1 - alpha / 2., n - 2)

    c = -1 * scipy.stats.t.ppf(alpha / 2., n - 2)
    bb1 = c * (s2 / ((n - 2) * (xx.mean() - (x.mean()) ** 2))) ** .5

    bb0 = c * ((s2 / (n - 2)) * (1 + (x.mean()) ** 2 /
                                 (xx.mean() - (x.mean()) ** 2))) ** .5

    return b1, b0, s2, (b1 - bb1, b1 + bb1), (b0 - bb0, b0 + bb0), (n * s2 / c2, n * s2 / c1)
