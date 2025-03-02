#!/usr/bin/env python
# coding: utf8

from goulib.math2 import *
from goulib.tests import *


class TestLongint:
    def test_longint(self):
        assert longint(1, 3) == 1000
        assert longint(10, 2) == 1000
        assert longint(0.1, 4) == 1000
        assert longint(0.123, 4) == 1230


class TestSign:
    def test_sign(self):
        assert sign(0.0001) == 1
        assert sign(-0.0001) == -1
        assert sign(-0.0000) == 0


class TestCmp:
    def test_cmp(self):
        assert cmp(0.0002, 0.0001) == 1
        assert cmp(0.0001, 0.0002) == -1
        assert cmp(0.0000, 0.0000) == 0


class TestMul(TestCase):
    def test_mul(self):
        assert mul(range(1, 10)) == 362880


class TestRint(TestCase):
    def test_rint(self):
        # https://docs.python.org/3.4/library/functions.html#round
        assert rint(0.5) == 0
        assert rint(-0.5) == -0

        assert rint(0.50001) == 1
        assert rint(-0.50001) == -1


class TestQuad:
    def test_quad(self):
        assert quad(1, 3, 2) == (-1, -2)
        with pytest.raises(ValueError) as excinfo:
            quad(1, 2, 3)  # complex results
        # complex results
        assert sum(quad(1, 2, 3, allow_complex=True)) == -2


class TestEqual:
    def test_isclose(self):
        a = 1E6
        d = 0.99e-3
        assert isclose(a, a+d)
        assert not isclose(a, a+2*d)

    def test_allclose(self):
        a = 1E6
        d = 0.99e-3
        assert allclose([a, a-d], [a+d, a])
        assert not allclose([a, a+2*d], [a, a])
        assert not allclose([a, a+2*d], [a, nan])
        assert not allclose([a], [a, nan])


class TestLcm:
    def test_lcm(self):
        assert lcm(101, -3) == -303
        assert lcm(4, 6) == 12
        assert lcm(3, 4, 6) == 12


class TestGcd:
    def test_gcd(self):
        assert gcd(54, 24) == 6
        assert gcd(24, 54) == 6
        assert gcd(68, 14, 9, 36, 126) == 1
        assert gcd(7, 14, 35, 7000) == 7
        assert gcd(1548) == 1548


class TestCoprime:
    def test_coprime(self):
        assert coprime(68, 14, 9, 36, 126)
        assert not coprime(7, 14, 35, 7000)


class TestAccsum:
    def test_accsum(self):
        s = list(accsum(range(10)))
        assert s[-1] == 45


class TestTranspose:
    def test_transpose(self):
        v1 = list(range(3))
        v2 = list(accsum(v1))
        m1 = [v1, v2, vecsub(v2, v1)]
        assert transpose(m1) == [[0, 0, 0], [1, 1, 0], [2, 3, 1]]


class TestMaximum:
    def test_maximum(self):
        m = [(1, 2, 3), (1, -2, 0), (4, 0, 0)]
        assert maximum(m) == [4, 2, 3]


class TestMinimum:
    def test_minimum(self):
        m = [(1, 2, 3), (1, -2, 0), (4, 0, 0)]
        assert minimum(m) == [1, -2, 0]


class TestDotVv:
    def test_dot_vv(self):
        v1 = list(range(3))
        v2 = list(accsum(v1))
        assert dot_vv(v1, v2) == 7


class TestDotMv:
    def test_dot_mv(self):
        v1 = list(range(3))
        v2 = list(accsum(v1))
        m1 = [v1, v2, vecsub(v2, v1)]
        assert dot_mv(m1, v1) == [5, 7, 2]


class TestDotMm:
    def test_dot_mm(self):
        v1 = list(range(3))
        v2 = list(accsum(v1))
        m1 = [v1, v2, vecsub(v2, v1)]
        m2 = transpose(m1)
        assert dot_mm(m1, m2) == [[5, 7, 2], [7, 10, 3], [2, 3, 1]]


class TestDot:
    def test_dot(self):
        v1 = list(range(3))
        v2 = list(accsum(v1))
        assert dot(v1, v2) == 7
        m1 = [v1, v2, vecsub(v2, v1)]
        assert dot(m1, v1) == [5, 7, 2]
        m2 = transpose(m1)
        assert dot(m1, m2) == [[5, 7, 2], [7, 10, 3], [2, 3, 1]]
        v1 = [715827883, 715827882]
        # fails with numpy.dot !
        assert dot(v1, v1) == 1024819114728867613


class TestVecadd:
    def test_vecadd(self):
        v1 = list(range(4))
        v2 = list(accsum(v1))
        assert vecadd(v1, v2) == [0, 2, 5, 9]
        v1 = v1[1:]
        assert vecadd(v1, v2) == [1, 3, 6, 6]
        assert vecadd(v1, v2, -1) == [1, 3, 6, 5]


class TestVecsub:
    def test_vecsub(self):
        v1 = list(range(4))
        v2 = tuple(accsum(v1))
        assert vecsub(v1, v2) == [0, 0, -1, -3]
        v1 = v1[1:]
        assert vecsub(v1, v2) == [1, 1, 0, -6]
        assert vecsub(v1, v2, -1) == [1, 1, 0, -7]


class TestVecmul:
    def test_vecmul(self):
        v1 = list(range(4))
        v2 = list(accsum(v1))
        assert vecmul(v1, v2) == [0, 1, 6, 18]
        assert vecmul(v1, 2) == [0, 2, 4, 6]
        assert vecmul(2, v1) == [0, 2, 4, 6]


class TestVecdiv:
    def test_vecdiv(self):
        v1 = list(range(5))[1:]
        v2 = list(accsum(v1))
        assert vecdiv(v1, v2) == [1, 2./3, 1./2, 2./5]
        assert vecdiv(v1, 2) == [1./2, 2./2, 3./2, 4./2]


class TestVeccompare:
    def test_veccompare(self):
        v1 = list(range(5))
        v2 = list(accsum(v1))
        v2[-1] = 2  # force to test ai>bi
        assert veccompare(v1, v2) == [2, 2, 1]


class TestFibonacciGen:
    def test_fibonacci_gen(self):
        # also tested in test_oeis

        # https://projecteuler.net/problem=2
        from itertools import takewhile

        def problem2(n):
            """Find the sum of all the even-valued terms in the Fibonacci < 4 million."""
            even_fibonacci = (x for x in fibonacci_gen() if x % 2 == 0)
            l = list(takewhile(lambda x: x < n, even_fibonacci))
            return sum(l)

        assert problem2(10) == 10
        assert problem2(100) == 44
        assert problem2(4E6) == 4613732


class TestFibonacci:
    def test_fibonacci(self):
        # checks that fibonacci and fibonacci_gen give the same results
        f = [fibonacci(i) for i in range(10)]
        assert f == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        assert f == list(itertools2.take(10, fibonacci_gen()))

        # http://controlfd.com/2016/07/05/using-floats-in-python.html
        assert fibonacci(78) == 8944394323791464

        f50 = fibonacci(50)
        f51 = fibonacci(51)
        phi = (1+sqrt(5))/2
        assert f51/f50 == pytest.approx(phi)

        # mod 1000000007 has the effect of using int32 only
        assert fibonacci(int(1E19), 1000000007) == 647754067
        assert fibonacci(int(1E19), 10) == 5


class TestIsFibonacci:
    def test_is_fibonacci(self):
        assert is_fibonacci(0)
        assert is_fibonacci(1)
        assert is_fibonacci(2)
        assert is_fibonacci(3)
        assert not is_fibonacci(4)
        assert is_fibonacci(8944394323791464)
        assert not is_fibonacci(8944394323791464+1)


class TestPisanoPeriod:
    def test_pisano_period(self):
        assert pisano_period(3) == 8
        assert pisano_period(10) == 60


class TestPisanoCycle:
    def test_pisano_cycle(self):
        assert pisano_cycle(3) == [0, 1, 1, 2, 0, 2, 2, 1]  # A082115


class TestIsInteger:
    def test_is_integer(self):
        assert is_integer(1+1e-6, 1e-6)
        assert not is_integer(1+2e-6, 1e-6)


class TestIntOrFloat:
    def test_int_or_float(self):
        # comparing values would always pass, so we must compare types
        assert type(int_or_float(1.0)) == int
        assert type(int_or_float(1.0+eps)) == float
        assert type(int_or_float(1+1e-6, 1e-6)) == int
        assert type(int_or_float(1+2e-6, 1e-6)) == float


class TestSieve:
    def test_sieve(self):
        assert sieve(50)[-1]== 47 
        assert sieve(10000)[-1]== 9973  # more than _sieve for coverage
        assert sieve(50)[-1]== 47 # test smaller afterwards for side effect


class TestPrimes:
    def test_primes(self):
        last = primes(1001)[999]  # more than _primes for coverage
        assert last == 7919


class TestNextprime:
    def test_nextprime(self):
        assert nextprime(0) == 2
        assert nextprime(1) == 2
        assert nextprime(2) == 3
        assert nextprime(1548) == 1549


class TestPrevprime:
    def test_prevprime(self):
        assert prevprime(1) == None
        assert prevprime(2) == None
        assert prevprime(3) == 2
        assert prevprime(1548) == 1543


class TestPrimesGen:
    def test_primes_gen(self):
        from itertools import islice
        a = list(islice(primes_gen(), 10))
        assert a == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        a = list(islice(primes_gen(29), 10))
        assert a == [29, 31, 37, 41, 43, 47, 53, 59, 61, 67]
        a = list(islice(primes_gen(67, 29), 10))
        assert a == list(reversed([29, 31, 37, 41, 43, 47, 53, 59, 61, 67]))
        a = list(primes_gen(901, 1000))
        assert a == [907, 911, 919, 929, 937, 941, 947,
                     953, 967, 971, 977, 983, 991, 997]


class TestStrBase:
    def test_str_base(self):
        assert str_base(2014) == "2014"
        assert str_base(-2014) == "-2014"
        assert str_base(-0) == "0"
        assert str_base(2014, 2) == "11111011110"
        assert str_base(65535, 16) == "ffff"

        with pytest.raises(ValueError):
            str_base(0, 1)

        # http://www.drgoulu.com/2011/09/25/comment-comptent-les-extraterrestres
        shadok = ['GA', 'BU', 'ZO', 'MEU']
        with pytest.raises(ValueError):
            str_base(0, 10, shadok)

        assert str_base(41, 4, shadok) == "ZOZOBU"
        assert str_base(1681, 4, shadok) == "BUZOZOBUGABU"


class TestDigitsGen:
    def test_digits_gen(self):
        pass  # used below


class TestDigits:
    def test_digits(self):
        assert digits(1234) == [1, 2, 3, 4]
        assert digits(1234, rev=True) == [4, 3, 2, 1]
        assert digits(2014, 2) == [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0]


class TestDigsum:
    def test_digsum(self):
        assert digsum(1234567890) == 45
        assert digsum(255, base=2) == 8  # sum of ones in binary rep
        assert digsum(255, base=16) == 30  # $FF in hex
        assert digsum(1234567890, 2) == sum_of_squares(9)
        assert digsum(548834, 6) == 548834  # narcissic number
        assert digsum(3435, lambda x: x**x) == 3435  # Munchausen number


class TestIntegerExponent:
    def test_integer_exponent(self):
        assert integer_exponent(1000) == 3
        assert integer_exponent(1024, 2) == 10
        # http://thales.math.uqam.ca/~rowland/packages/BinomialCoefficients/HTMLLinks/index_3.html
        assert integer_exponent(binomial(1000, 373), 2) == 6


class TestPowerTower:
    def test_power_tower(self):
        assert power_tower([3, 2, 2, 2]) == 43046721


class TestCarries:
    def test_carries(self):
        assert carries(127, 123) == 1
        assert carries(127, 173) == 2
        assert carries(1, 999) == 3
        assert carries(999, 1) == 3
        assert carries(127, 127, 2) == 7


class TestNumFromDigits:
    def test_num_from_digits(self):
        assert num_from_digits('1234') == 1234
        assert num_from_digits('11111011110', 2) == 2014
        assert num_from_digits([1, 2, 3, 4]) == 1234
        assert num_from_digits([1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0], 2) == 2014
        assert num_from_digits('ABCD', 16) == 43981
        assert num_from_digits([10,11,12,13], 16) == 43981
        with pytest.raises(ValueError):
            num_from_digits([10,11,12,13], 10)
        with pytest.raises(ValueError):
            num_from_digits('G', 16)



class TestNumberOfDigits:
    def test_number_of_digits(self):
        assert number_of_digits(0) == 1
        assert number_of_digits(-1) == 1
        assert number_of_digits(999) == 3
        assert number_of_digits(1000) == 4
        assert number_of_digits(1234) == 4
        assert number_of_digits(9999) == 4
        assert number_of_digits(2014, 2) == 11
        assert number_of_digits(65535, 16) == 4


class TestIsPalindromic:
    def test_is_palindromic(self):
        assert is_palindromic(4352534)
        assert is_palindromic(17, 2)
        assert sum(filter(is_palindromic, range(
            34*303, 100000, 303))) == 394203


class TestIsLychrel:
    def test_is_lychrel(self):
        assert is_lychrel(196)
        assert is_lychrel(4994)


class TestIsPrime:
    def test_is_prime(self):
        assert not is_prime(0)
        assert not is_prime(1)
        assert is_prime(2)

        # https://oeis.org/A014233
        pseudoprimes = [2047, 1373653, 25326001, 3215031751, 2152302898747, 3474749660383,
                        341550071728321, 3825123056546413051, 318665857834031151167461, 3317044064679887385961981]
        for pp in pseudoprimes:
            assert not is_prime(pp)

        assert is_prime(201420142013)
        assert is_prime(
            4547337172376300111955330758342147474062293202868155909489)
        assert not is_prime(
            4547337172376300111955330758342147474062293202868155909393)
        assert [x for x in range(901, 1000) if is_prime(x)] == [
            907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]
        assert is_prime(643808006803554439230129854961492699151386107534013432918073439524138264842370630061369715394739134090922937332590384720397133335969549256322620979036686633213903952966175107096769180017646161851573147596390153)
        assert not is_prime(743808006803554439230129854961492699151386107534013432918073439524138264842370630061369715394739134090922937332590384720397133335969549256322620979036686633213903952966175107096769180017646161851573147596390153)


class TestFactorEcm:
    def test_factor_ecm(self):
        for _ in range(10):
            size = 32
            a = random_prime(size)
            b = random_prime(size)
            c = factor_ecm(a*b)
            assert c in (a, b)


class TestPrimeFactors:
    def test_prime_factors(self):
        assert list(prime_factors(2014)) == [2, 19, 53]
        assert list(prime_factors(2048)) == [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]


class TestFactorize:
    def test_factorize(self):
        assert list(factorize(1)) == [(1, 1)]
        assert list(factorize(2014)) == [(2, 1), (19, 1), (53, 1)]
        assert list(factorize(2048)) == [(2, 11)]


class TestDivisors:
    def test_divisors(self):
        d = list(divisors(1))
        assert d == [1]
        d = list(divisors(2014))
        assert d == [1, 53, 19, 1007, 2, 106, 38, 2014]
        d = list(divisors(2**3*3**2))
        assert sorted(d) == sorted(
            [1, 2, 4, 8, 3, 9, 6, 12, 24, 18, 36, 72])


class TestProperDivisors:
    def test_proper_divisors(self):
        d = list(proper_divisors(2014))
        assert d == [1, 53, 19, 1007, 2, 106, 38]


class TestTriangle:
    def test_triangle(self):
        assert triangle(10) == 55


class TestIsTriangle:
    def test_is_triangle(self):
        assert is_triangle(55)
        assert not is_triangle(54)


class TestPentagonal:
    def test_pentagonal(self):
        assert pentagonal(10) == 145


class TestIsPentagonal:
    def test_is_pentagonal(self):
        assert is_pentagonal(145)
        assert not is_pentagonal(146)


class TestHexagonal:
    def test_hexagonal(self):
        assert hexagonal(10) == 190


class TestGetCardinalName:
    def test_get_cardinal_name(self):
        assert (get_cardinal_name(123456) ==
                'one hundred and twenty-three thousand four hundred and fifty-six')
        assert (get_cardinal_name(1234567890) ==
                'one billion two hundred and thirty-four million five hundred and sixty-seven thousand eight hundred and ninety')


class TestIsPerfect:
    def test_is_perfect(self):
        assert is_perfect(496) == 0  # perfect
        assert is_perfect(54) == 1  # abundant
        assert is_perfect(2) == -1  # deficient

        # Millenium 4, page 326
        assert is_perfect(2305843008139952128) == 0
        assert is_perfect(2658455991569831744654692615953842176) == 0


class TestIsPandigital:
    def test_is_pandigital(self):
        # https://en.wikipedia.org/wiki/Pandigital_number
        assert is_pandigital(9786530421)
        assert is_pandigital(1223334444555567890)
        assert is_pandigital(10, 2)
        assert is_pandigital(0x1023456789ABCDEF, 16)


class TestSetsDist:
    def test_sets_dist(self):
        a = set(list('hello'))
        b = set(list('world'))
        assert sets_dist(a, b) == 3.1622776601683795


class TestHamming:
    def test_hamming(self):
        a = "10011100"
        b = "00011010"
        assert hamming(a, b) == 3


class TestSetsLevenshtein:
    def test_sets_levenshtein(self):
        a = set(list('hello'))
        b = set(list('world'))
        assert sets_levenshtein(a, b) == 5


class TestLevenshtein:
    def test_levenshtein(self):
        assert levenshtein('hello', 'world') == 4


class TestBinomial:
    def test_binomial(self):
        # https://www.hackerrank.com/challenges/ncr
        assert binomial(1, 2) == 0
        assert binomial(2, 1) == 2
        assert binomial(4, 0) == 1
        assert binomial(5, 2) == 10
        assert binomial(10, 3) == 120
        assert binomial(87, 28) % 142857 == 141525
        assert binomial(100000, 4000) == binomial(100000, 96000)

    def test_binomial_overflow(self):
        with pytest.raises(OverflowError):
            assert binomial(961173600, 386223045) % 142857 == 0


class TestFaulhaber:
    def test_faulhaber(self):
        def sumpow(n, p):
            return sum((x**p for x in range(n+1)))
        assert faulhaber(100, 0) == 100
        assert faulhaber(100, 1) == triangular(100)
        assert faulhaber(100, 2) == sum_of_squares(100)
        assert faulhaber(100, 3) == sum_of_cubes(100)
        assert faulhaber(100, 4) == sumpow(100, 4)


class TestBinomialExponent:
    def test_binomial_exponent(self):
        # https://www.math.upenn.edu/~wilf/website/dm36.pdf
        assert binomial_exponent(88, 50, 3) == 3

        # http://thales.math.uqam.ca/~rowland/packages/BinomialCoefficients/HTMLLinks/index_3.html
        assert binomial_exponent(1000, 373, 2) == 6
        for b in range(2, 11):
            for n in range(1, 20):
                for k in range(1, n):
                    assert (binomial_exponent(n, k, b) ==
                            integer_exponent(binomial(n, k), b))


class TestProportional:
    def test_proportional(self):
        assert proportional(12, [0, 0, 1, 0]) == [0, 0, 12, 0]
        votes = [10, 20, 30, 40]
        assert proportional(100, votes) == votes
        assert proportional(10, votes) == [1, 2, 3, 4]
        assert sum(proportional(37, votes)) == 37
        assert proportional(37, votes) == [4, 7, 11, 15]


class TestTriangularRepartition:
    def test_triangular_repartition(self):

        ref = [0.01, 0.03, 0.05, 0.07, 0.09, 0.11, 0.13, 0.15, 0.17, 0.19]
        res = triangular_repartition(1, 10)
        assert sum(res) == pytest.approx(1)
        assert dist(res, ref) < 1E-6
        ref.reverse()
        res = triangular_repartition(0, 10)
        assert sum(res) == pytest.approx(1)
        assert dist(res, ref) < 1E-6

        ref = [0.02, 0.06, 0.1, 0.14, 0.18, 0.18, 0.14, 0.1, 0.06, 0.02]
        res = triangular_repartition(.5, 10)
        assert sum(res) == pytest.approx(1)
        assert dist(res, ref) < 1E-6

        ref = [0.08, 0.24, 0.36, 0.24, 0.08]
        res = triangular_repartition(.5, 5)  # center value is top of triangle
        assert sum(res) == pytest.approx(1)
        assert dist(res, ref) < 1E-6


class TestRectangularRepartition:
    def test_rectangular_repartition(self):
        ref = [.5, .125, .125, .125, .125]
        res = rectangular_repartition(0, 5, .5)
        assert pytest.approx(sum(res)) == 1
        assert dist(res, ref) < 1E-6

        ref = [0.3125, 0.3125, .125, .125, .125]
        res = rectangular_repartition(.2, 5, .5)
        assert pytest.approx(sum(res)) == 1
        assert dist(res, ref) < 1E-6
        ref.reverse()
        res = rectangular_repartition(.8, 5, .5)
        assert pytest.approx(sum(res)) == 1
        assert dist(res, ref) < 1E-6

        ref = [0.1, 0.1675, 0.3325, .1, .1, .1, .1]
        res = rectangular_repartition(.325, 7, .4)
        assert pytest.approx(sum(res)) == 1


class TestNorm2:
    def test_norm_2(self):
        assert norm_2([-3, 4]) == 5


class TestNorm1:
    def test_norm_1(self):
        assert norm_1([-3, 4]) == 7


class TestNormInf:
    def test_norm_inf(self):
        assert norm_inf([-3, 4]) == 4


class TestNorm:
    def test_norm(self):
        assert norm([-3, 4], 2) == 5
        assert norm([-3, 4], 1) == 7


class TestDist:
    def test_dist(self):
        pass  # tested somewhere else


class TestSat:
    def test_sat(self):
        assert sat(3) == 3
        assert sat(-2) == 0
        assert sat(-3, -3) == -3
        assert sat(3, 1, 2) == 2
        assert sat([-2, -1, 0, 1, 2, 3], -1, 2) == [-1, -1, 0, 1, 2, 2]


class TestVecneg:
    def test_vecneg(self):
        assert vecneg([-2, -1, 0, 1, 2, 3]) == [2, 1, 0, -1, -2, -3]


class TestAngle:
    def test_angle(self):
        assert angle((1, 0), (0, 1)) == pytest.approx(math.pi/2)
        assert angle((1, 0), (-1, 0)) == pytest.approx(math.pi)
        assert angle((1, 1), (0, 1), unit=False) == pytest.approx(math.pi/4)
        assert angle(vecunit((2, 1)), vecunit(
            (1, -2))) == pytest.approx(math.pi/2)


class TestVecunit:
    def test_vecunit(self):
        v = vecunit((-3, 4, 5))
        assert norm(v) == 1


class TestSinOverX:
    def test_sin_over_x(self):
        assert sin_over_x(1) == math.sin(1)
        assert sin_over_x(0) == 1
        assert sin_over_x(1e-9) == 1


class TestSlerp:
    def test_slerp(self):
        u = vecunit((1, 1, 1))
        v = vecunit((1, 1, -1))
        assert slerp(u, v, 0) == u
        assert slerp(u, v, 1) == v
        s = slerp(u, v, 0.5)
        assert pytest.approx(s) == vecunit((1, 1, 0))


class TestLogFactorial:
    def test_log_factorial(self):
        assert pytest.approx(log_factorial(100)) == 363.73937555556349014408


class TestLogBinomialCoefficient:
    def test_log_binomial(self):
        assert pytest.approx(log_binomial(87, 28)) == math.log(
            49848969000742658237160)


class Moebius:
    def test_moebius(self):
        assert moebius(3) == -1


class Omega:
    def test_omega(self):
        assert omega(3) == 0
        assert omega(4) == 1
        assert omega(6) == 2


class TestEulerPhi:
    def test_euler_phi(self):
        assert euler_phi(8849513) == 8843520


class TestKempner:
    def test_kempner(self):
        # from https://projecteuler.net/problem=549
        assert kempner(1) == 1
        assert kempner(8) == 4
        assert kempner(10) == 5
        assert kempner(25) == 10
        # assert_equal(kempner(128),8) #TODO: find why it fails ...
        assert sum(kempner(x) for x in range(2, 100+1)) == 2012


class TestRecurrence:

    def test_recurrence(self):
        # assert (expected, recurrence(factors, values, max))
        pytest.skip("not yet implemented")  # TODO: implement


class TestLucasLehmer:
    def test_lucas_lehmer(self):
        assert not lucas_lehmer(1548)  # trivial case
        assert lucas_lehmer(11213)  # found on Illiac 2, 1963)
        assert not lucas_lehmer(239)


class TestReverse:
    def test_reverse(self):
        # assert_equal(expected, reverse(i))
        pytest.skip("not yet implemented")  # TODO: implement


class TestLychrelSeq:
    def test_lychrel_seq(self):
        # assert_equal(expected, lychrel_seq(n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestLychrelCount:
    def test_lychrel_count(self):
        # assert_equal(expected, lychrel_count(n, limit))
        pytest.skip("not yet implemented")  # TODO: implement


class TestPow:
    def test_pow(self):
        from goulib.math2 import pow  # make sure we don't use builtins
        assert pow(10, 100) == pytest.approx(1E100)
        assert pow(10, -100) != 0

        assert pow(2, 10, 100) == 24
        # https://fr.wikipedia.org/wiki/Exponentiation_modulaire
        assert pow(4, 13, 497) == 445
        # http://www.math.utah.edu/~carlson/hsp2004/PythonShortCourse.pdf
        assert pow(2, 13739062, 13739063) == 2933187


class TestIsqrt:
    def test_isqrt(self):
        assert isqrt(256) == 16
        assert isqrt(257) == 16
        assert isqrt(255) == 15


class TestAbundance:
    def test_abundance(self):
        # assert_equal(expected, abundance(n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestFactorial:
    def test_factorial(self):
        assert factorial(0) == 1
        assert factorial2(0) == 1
        assert [factorial2(x) for x in [7, 8, 9]] == [105, 384, 945]
        assert factorialk(5, 1) == 120
        assert factorialk(5, 3) == 10


class TestCeildiv:
    def test_ceildiv(self):
        assert ceildiv(1, 3) == 1
        assert ceildiv(5, 3) == 2
        assert ceildiv(-1, 3) == 0
        assert ceildiv(1, -3) == 0


class TestCatalanGen:
    def test_catalan_gen(self):
        assert (itertools2.nth(20, catalan_gen()) ==
                6564120420)  # https://oeis.org/A000108


class TestCatalan:
    def test_catalan(self):
        assert catalan(20) == 6564120420  # https://oeis.org/A000108


class TestPrimitiveTriples:
    def test_primitive_triples(self):
        def key(x): return (x[2], x[1])
        for t in itertools2.take(10000, itertools2.ensure_sorted(primitive_triples(), key)):
            assert is_pythagorean_triple(*t)


class TestTriples:
    def test_triples(self):
        def key(x): return (x[2], x[1])
        for t in itertools2.take(10000, itertools2.ensure_sorted(triples(), key)):
            assert is_pythagorean_triple(*t)


class TestPolygonal:
    def test_polygonal(self):
        pass  # tested in test_oeis


class TestSquare:
    def test_square(self):
        pass  # tested in test_oeis


class TestIsSquare:
    def test_is_square(self):
        pass  # tested in test_oeis


class TestIsHexagonal:
    def test_is_hexagonal(self):
        pass  # tested in test_oeis


class TestHeptagonal:
    def test_heptagonal(self):
        pass  # tested in test_oeis


class TestIsHeptagonal:
    def test_is_heptagonal(self):
        pass  # tested in test_oeis


class TestOctagonal:
    def test_octagonal(self):
        pass  # tested in test_oeis


class TestIsOctagonal:
    def test_is_octagonal(self):
        pass  # tested in test_oeis


class TestPartition:
    def test_partition(self):
        pass  # tested in test_oeis


class TestChakravala:
    def test_chakravala(self):
        x, y = chakravala(61)
        assert x == 1766319049 and y == 226153980
        # https://en.wikipedia.org/wiki/Chakravala_method


class TestBouncy:
    def test_bouncy(self):
        # assert_equal(expected, bouncy(n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestIsHappy:
    def test_is_happy(self):
        # assert_equal(expected, is_happy(n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestNumberOfDivisors:
    def test_number_of_divisors(self):
        # assert_equal(expected, number_of_divisors(n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestFactorialGen:
    def test_factorial_gen(self):
        # assert_equal(expected, factorial_gen())
        pytest.skip("not yet implemented")  # TODO: implement


class TestEuclidGen:
    def test_euclid_gen(self):
        # assert_equal(expected, euclid_gen())
        pytest.skip("not yet implemented")  # TODO: implement


class TestEgcd:
    def test_egcd(self):
        pass  # tested below


class TestModInv:
    def test_mod_inv(self):
        assert mod_inv(3, 11) == 4


class TestModDiv:
    def test_mod_div(self):
        assert mod_div(3, 16, 53) == 30
        assert mod_div(3, 16, 53) == 30
        assert mod_div(5, 5, 12) == 25


class TestModFact:
    def test_mod_fact(self):
        assert mod_fact(10, 71) == 61
        assert mod_fact(11, 71) == 32


class TestChineseRemainder:
    def test_chinese_remainder(self):
        assert chinese_remainder([3, 5, 7], [2, 3, 2]) == 23
        # http://en.wikipedia.org/wiki/Chinese_remainder_theorem
        assert chinese_remainder([3, 4, 5], [2, 3, 1]) == 11


class TestModBinomial:
    def test_mod_binomial(self):
        # http://math.stackexchange.com/questions/95491/n-choose-k-bmod-m-using-chinese-remainder-theorem
        assert mod_binomial(456, 51, 30) == 28

        # http://thales.math.uqam.ca/~rowland/packages/BinomialCoefficients/HTMLLinks/index_4.html
        assert mod_binomial(1000, 729, 19) == 13

        res = binomial(16, 5) % 9
        # http://math.stackexchange.com/questions/222637/binomial-coefficient-modulo-prime-power
        assert mod_binomial(16, 5, 9) == res

        m = 142857

        assert mod_binomial(5, 2, m) == binomial(5, 2)
        assert mod_binomial(10, 3, m) == binomial(10, 3)

        assert mod_binomial(27, 3, 27) == binomial(27, 3) % 27  # ==9
        assert mod_binomial(27, 3, m) == binomial(27, 3) % m  # == 2925

        return  # tests below are too large for now

        assert mod_binomial(961173600, 386223045, m) == 0
        assert mod_binomial(938977945, 153121024, m) == 47619
        assert mod_binomial(906601285, 527203335, m) == 0
        assert mod_binomial(993051461, 841624879, m) == 104247


class TestDeBrujin:
    def test_de_brujin(self):
        assert de_bruijn(
            '1234', 3) == '1112113114122123124132133134142143144222322423323424324433343444'


class TestXgcd:
    def test_xgcd(self):
        # assert_equal(expected, xgcd(a, b))
        pytest.skip("not yet implemented")  # TODO: implement


class TestIsclose:
    def test_isclose(self):
        # assert_equal(expected, isclose(a, b, rel_tol, abs_tol))
        pytest.skip("not yet implemented")  # TODO: implement


class TestOmega:
    def test_omega(self):
        # assert_equal(expected, omega(n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestBigomega:
    def test_bigomega(self):
        # assert_equal(expected, bigomega(n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestMoebius:
    def test_moebius(self):
        # assert_equal(expected, moebius(n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestPrimeKtuple:
    def test_prime_ktuple(self):
        # assert_equal(expected, prime_ktuple(constellation))
        pytest.skip("not yet implemented")  # TODO: implement


class TestTwinPrimes:
    def test_twin_primes(self):
        # assert_equal(expected, twin_primes())
        pytest.skip("not yet implemented")  # TODO: implement


class TestCousinPrimes:
    def test_cousin_primes(self):
        # assert_equal(expected, cousin_primes())
        pytest.skip("not yet implemented")  # TODO: implement


class TestSexyPrimes:
    def test_sexy_primes(self):
        # assert_equal(expected, sexy_primes())
        pytest.skip("not yet implemented")  # TODO: implement


class TestSexyPrimeTriplets:
    def test_sexy_prime_triplets(self):
        # assert_equal(expected, sexy_prime_triplets())
        pytest.skip("not yet implemented")  # TODO: implement


class TestSexyPrimeQuadruplets:
    def test_sexy_prime_quadruplets(self):
        # assert_equal(expected, sexy_prime_quadruplets())
        pytest.skip("not yet implemented")  # TODO: implement


class TestLogBinomial:
    def test_log_binomial(self):
        # assert_equal(expected, log_binomial(n, k))
        pytest.skip("not yet implemented")  # TODO: implement


class TestIlog:
    def test_ilog(self):
        assert ilog(ipow(2, 5), 2) == 5
        assert ilog(ipow(10, 5), 10) == 5
        assert ilog(ipow(7, 13), 7) == 13


class TestBabyStepGiantStep:
    def test_baby_step_giant_step(self):
        # 70 = 2**x mod 131
        y, a, n = 70, 2, 131
        x = baby_step_giant_step(y, a, n)
        assert y == a**x % n


class TestIsNumber:
    def test_is_number(self):
        assert is_number(0)
        assert is_number(2)
        assert is_number(2.)
        assert not is_number(None)
        assert is_number(sqrt(-1))  # complex are numbers

    def test_is_complex(self):
        assert not is_complex(2.)
        assert is_number(sqrt(-1))

    def test_is_real(self):
        assert is_real(2.)
        assert not is_real(sqrt(-1))


class TestCoprimesGen:
    def test_coprimes_gen(self):
        res = ','.join(('%d/%d' % (n, d) for n, d in coprimes_gen(10)))
        assert res == '0/1,1/10,1/9,1/8,1/7,1/6,1/5,2/9,1/4,2/7,3/10,1/3,3/8,2/5,3/7,4/9,1/2,5/9,4/7,3/5,5/8,2/3,7/10,5/7,3/4,7/9,4/5,5/6,6/7,7/8,8/9,9/10'


class TestTetrahedral:
    def test_tetrahedral(self):
        # assert_equal(expected, tetrahedral(n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestSumOfSquares:
    def test_sum_of_squares(self):
        # assert_equal(expected, sum_of_squares(n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestSumOfCubes:
    def test_sum_of_cubes(self):
        # assert_equal(expected, sum_of_cubes(n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestBernouilliGen:
    def test_bernouilli_gen(self):
        # assert_equal(expected, bernouilli_gen(init))
        pytest.skip("not yet implemented")  # TODO: implement


class TestBernouilli:
    def test_bernouilli(self):
        # assert_equal(expected, bernouilli(n, init))
        pytest.skip("not yet implemented")  # TODO: implement


class TestDeBruijn:
    def test_de_bruijn(self):
        # assert_equal(expected, de_bruijn(k, n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestPascalGen:
    def test_pascal_gen(self):
        # assert_equal(expected, pascal_gen())
        pytest.skip("not yet implemented")  # TODO: implement


class TestIsPythagoreanTriple:
    def test_is_pythagorean_triple(self):
        # assert_equal(expected, is_pythagorean_triple(a, b, c))
        pytest.skip("not yet implemented")  # TODO: implement


class TestFormat:
    def test_format(self):
        # assert_equal(expected, format(x, decimals))
        pytest.skip("not yet implemented")  # TODO: implement


class TestMultiply:
    def test_multiply(self):
        from random import getrandbits
        for bits in [100, 1000, 10000]:
            a = getrandbits(bits)
            b = getrandbits(bits)
            assert multiply(a, b) == a*b


class TestSqrt:
    def test_sqrt(self):
        # assert_equal(expected, sqrt(n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestModMatmul:
    def test_mod_matmul(self):
        # assert_equal(expected, mod_matmul(A, B, mod))
        pytest.skip("not yet implemented")  # TODO: implement


class TestModMatpow:
    def test_mod_matpow(self):
        a = [[1, 2], [1, 0]]
        b = matrix_power(a, 50)
        assert b == [[750599937895083, 750599937895082],
                     [375299968947541, 375299968947542]]


class TestZeros:
    def test_zeros(self):
        # assert_equal(expected, zeros(shape))
        pytest.skip("not yet implemented")  # TODO: implement


class TestDiag:
    def test_diag(self):
        # assert_equal(expected, diag(v))
        pytest.skip("not yet implemented")  # TODO: implement


class TestFactors:
    def test_factors(self):
        # assert_equal(expected, factors(n))
        pytest.skip("not yet implemented")  # TODO: implement


class TestIsPrimitiveRoot:
    def test_is_primitive_root(self):
        pass  # tested below


class TestPrimitiveRootGen:
    def test_primitive_root_gen(self):
        pass  # tested below


class TestPrimitiveRoots:
    def test_primitive_roots(self):
        assert primitive_roots(17) == [3, 5, 6, 7, 10, 11, 12, 14]
        # assert_equal(primitive_roots(1),[1]  ) # how is it defined ?


class TestRandomPrime:
    def test_random_prime(self):
        for b in range(8, 128, 8):
            r = random_prime(b)
            assert is_prime(r)
            assert r > 2**(b-1)
            assert r < 2**b


class TestPrimeDivisors:
    def test_prime_divisors(self):
        # assert_equal(expected, prime_divisors(num, start))
        pytest.skip("not yet implemented")  # TODO: implement


class TestIsMultiple:
    def test_is_multiple(self):
        # assert_equal(expected, is_multiple(n, factors))
        pytest.skip("not yet implemented")  # TODO: implement


class TestRepunit:
    def test_repunit_gen(self):
        assert list(itertools2.take(5, repunit_gen(digit=1))) == [
            0, 1, 11, 111, 1111]
        assert list(itertools2.take(5, repunit_gen(digit=9))) == [
            0, 9, 99, 999, 9999]

    def test_repunit(self):
        assert repunit(0) == 0
        assert repunit(1) == 1
        assert repunit(2) == 11
        assert repunit(12) == 111111111111
        assert repunit(12, digit=2) == 222222222222


class TestRationalForm:
    def test_rational_form(self):
        pass  # tested below

    def test_rational_str(self):
        assert rational_str(1, 4) == '0.25'
        assert rational_str(1, 3) == '0.(3)'
        assert rational_str(2, 3) == '0.(6)'
        assert rational_str(1, 6) == '0.1(6)'
        assert rational_str(1, 9) == '0.(1)'
        assert rational_str(7, 11) == '0.(63)'
        assert rational_str(29, 12) == '2.41(6)'
        assert rational_str(9, 11) == '0.(81)'
        assert rational_str(7, 12) == '0.58(3)'
        assert rational_str(1, 81) == '0.(012345679)'
        assert rational_str(22, 7) == '3.(142857)'
        assert rational_str(11, 23) == '0.(4782608695652173913043)'
        assert rational_str(
            1, 97) == '0.(010309278350515463917525773195876288659793814432989690721649484536082474226804123711340206185567)'

    def test_rational_cycle(self):
        assert rational_cycle(1, 4) == 0
        assert rational_cycle(1, 3) == 3
        assert rational_cycle(1, 7) == 142857
        assert rational_cycle(1, 81) == 123456790
        assert rational_cycle(1, 92) == 8695652173913043478260
