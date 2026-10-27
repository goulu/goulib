from goulib.tests import *
from goulib.stats import *

from random import random

import os
path = os.path.dirname(os.path.abspath(__file__))

# data from https://www.hackerrank.com/challenges/stat-warmup
h = [64630, 11735, 14216, 99233, 14470, 4978, 73429, 38120, 51135, 67060]
hmean = 43900.6
hvar = 1031372102  # variance of h computed in Matlab

n = 10000

f = [float(_)/n for _ in range(n+1)]
fvar = 1./12  # variance of f, theoretical


class TestMean:
    def test_mean(self):
        assert avg(f) == pytest.approx(1/2)
        assert mean(h) == pytest.approx(hmean)


class TestVariance:
    def test_variance(self):
        assert var(f) == pytest.approx(1./12,rel=0.01)
        assert variance(h) == pytest.approx(hvar)


class TestStats:
    @classmethod
    def setup_class(self):
        self.f = Stats(f)
        self.h = Stats(h)

    def test___init__(self):
        pass  # tested above

    def test_append(self):
        pass  # tested above

    def test_extend(self):
        pass  # tested above

    def test_remove(self):
        s = Stats([1, 2, 3, 4, 5])
        s.remove(5)
        assert s.n == 4

    def test_mean(self):
        assert self.f.mean == pytest.approx(0.5)
        assert self.h.avg == pytest.approx(hmean)

    def test_variance(self):
        assert self.f.variance == pytest.approx(fvar,0.01)
        assert math2.rint(self.h.var) == pytest.approx(hvar)

    def test_stddev(self):
        assert self.f.stddev == pytest.approx(math.sqrt(self.f.var))

    def test_stats(self):
        res = stats([1, 2, 3, 4, 5])
        assert len(res) == 6

    def test___add__(self):
        s = self.f + self.h
        assert isinstance(s, Stats)

    def test___mul__(self):
        s = self.f * 2
        assert isinstance(s, Stats)
        s2 = self.f * self.h
        assert isinstance(s2, Stats)

    def test___neg__(self):
        s = -self.f
        assert isinstance(s, Stats)

    def test___pow__(self):
        s = self.f ** 2
        assert isinstance(s, Stats)

    def test___repr__(self):
        assert 'Stats' in repr(self.f)

    def test___sub__(self):
        s = self.f - self.h
        assert isinstance(s, Stats)

    def test_covariance(self):
        assert self.f.covariance(self.h) is not None

    def test_sum(self):
        assert self.f.sum > 0

    def test_sum2(self):
        assert self.f.sum2 > 0


class TestStddev:
    def test_stddev(self):
        assert stddev(h) == pytest.approx(math.sqrt(hvar))


class TestConfidenceInterval:
    def test_confidence_interval(self):
        assert confidence_interval(h) == pytest.approx((23996, 63806),abs=0.5)


class TestMedian:
    def test_median(self):
        assert median(h) == pytest.approx(44627.5)


class TestMode:
    def test_mode(self):
        assert mode(h) == 4978
        assert mode([1, 1, 1, 2, 2, 3]) == 1  # test when mode is first
        assert mode([1, 2, 2, 3, 3, 3]) == 3  # test when mode is last
        assert mode([1, 2, 2, 3, 3, 4]) == 2  # test equality

class TestLinearRegression:
    def test_linear_regression(self):
        try:
            import scipy
        except:
            logging.warning('scipy required')
            return
        # first test a perfect fit
        a, b, c = linear_regression([1, 2, 3], [-1, -3, -5])
        assert (a, b, c) == pytest.approx((-2, 1, 0))
        a, b, c, ai, bi, ci = linear_regression([1, 2, 3], [-1, -3, -5], .95)
        assert ai == pytest.approx((-2, -2))
        assert bi == pytest.approx((1, 1))
        assert ci == pytest.approx((0, 0))


class TestNormal:
    @classmethod
    def setup_class(self):
        self.gauss = Normal(mean=1)
        self.two = Normal(mean=2, var=0)
        self.h = Normal(h)

    def test___init__(self):
        pass  # tested above

    def test_append(self):
        pass  # tested above

    def test_extend(self):
        pass  # tested above

    def test___str__(self):
        assert str(self.gauss) == 'Normal(mean=1, var=1)'

    def test_mean(self):
        assert self.h.avg == hmean

    def test_variance(self):
        assert self.gauss.var == pytest.approx(1)
        assert self.two.var ==pytest.approx(0)
        assert self.h.var == pytest.approx(hvar)

    def test_stddev(self):
        assert self.h.stddev == pytest.approx(math.sqrt(hvar))

    def test_linear(self):
        pass  # tested below

    def test___add__(self):
        twogauss = self.gauss+self.gauss
        assert twogauss.var == pytest.approx(2)
        assert twogauss.avg == pytest.approx(2)

        n = self.gauss+1
        assert n.var == pytest.approx(1)
        assert n.avg == pytest.approx(2)

    def test___radd__(self):
        n = 1+self.gauss
        assert n.avg == pytest.approx(2)
        assert n.var == pytest.approx(1)

    def test___sub__(self):
        zero = self.gauss-self.gauss
        assert zero.avg == pytest.approx(0)
        assert zero.var == pytest.approx(2)

    def test___mul__(self):
        twogauss = self.gauss*2
        assert twogauss.avg == pytest.approx(2)
        assert twogauss.var == pytest.approx(2)

    def test___div__(self):
        halfgauss = self.gauss/2
        assert halfgauss.avg == pytest.approx(1/2)
        assert halfgauss.var == pytest.approx(1/2)

    def test___call__(self):
        assert self.gauss(1) > 0
        assert list(self.gauss([0, 1]))[1] > 0

    def test___neg__(self):
        assert (-self.gauss).mean == pytest.approx(-self.gauss.mean)

    def test___rsub__(self):
        diff = 5 - self.gauss
        assert diff.mean == pytest.approx(5 - self.gauss.mean)

    def test_covariance(self):
        n1 = Normal([1, 2, 3])
        n2 = Normal([2, 4, 6])
        cov = n1.covariance(n2)
        assert cov is not None

    def test_pdf(self):
        assert self.gauss.pdf(1) > 0

    def test_pearson(self):
        n1 = Normal([1, 2, 3], mean=2, var=1)
        n2 = Normal([2, 4, 6], mean=4, var=4)
        assert n1.pearson(n2) is not None

    def test_plot(self):
        fig, ax = plt.subplots()
        self.gauss._plot(ax)
        plt.close(fig)

    def test_pop(self):
        pass  # pop is not implemented on Normal, remove is used

    def test_remove(self):
        n = Normal([1, 2, 3])
        n.remove(2)
        assert n.n == 2

    def test_save(self):
        n1 = Normal()
        n2 = Normal([], 2, 2)
        n3 = Normal([2])
        plot.save([n1, n2, n1+n2], path+'/results/stats.gauss.png')

    def test_latex(self):
        lat = self.gauss.latex()
        assert r"\mathcal{N}" in lat


class TestMeanVar:
    def test_mean_var(self):
        m, v = mean_var([1, 2, 3, 4, 5])
        assert m == pytest.approx(3.0)
        assert v == pytest.approx(2.5)
        m0, v0 = mean_var([1])
        assert m0 == 1
        assert math.isnan(v0)


class TestKurtosis:
    def test_kurtosis(self):
        k = kurtosis([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        assert isinstance(k, float)


class TestCovariance:
    def test_covariance(self):
        cov = covariance([1, 2, 3, 4], [2, 4, 6, 8])
        assert cov > 0


class TestNormalPdf:
    def test_normal_pdf(self):
        p = normal_pdf(0, 0, 1)
        assert p == pytest.approx(1 / math.sqrt(2 * math.pi))


class TestDiscrete:
    def test___call__(self):
        d = Discrete([1, 2, 3, 4])
        assert d(2) == pytest.approx(0.25)
        assert d(5) == 0
        assert list(d([1, 2])) == pytest.approx([0.25, 0.25])
        d2 = Discrete({1: 0.25, 2: 0.5, 3: 0.25})
        assert d2(2) == pytest.approx(0.5)

    def test___init__(self):
        d = Discrete({1: 0.2, 2: 0.8})
        assert d(1) == pytest.approx(0.2)
        assert d(2) == pytest.approx(0.8)


class TestPDF:
    def test___call__(self):
        p = PDF(lambda x: x * 2)
        assert p(3) == 6
        assert list(p([1, 2, 3])) == [2, 4, 6]

    def test___init__(self):
        p = PDF(lambda x: normal_pdf(x, 0, 1))
        assert p(0) == pytest.approx(normal_pdf(0, 0, 1))

