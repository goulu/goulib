from goulib.tests import *  # pylint: disable=wildcard-import, unused-wildcard-import

from goulib.geom import *   # pylint: disable=wildcard-import, unused-wildcard-import

from math import *


class TestGeometry:
    # tested in derived classes
    def test_connect(self):
        circ = Circle(Point2(3., 2.), 2.)
        line = Line2(Point2(0., 0.), Point2(-1., 1.))
        c = line.connect(circ)
        assert c is not None

    def test_distance(self):
        p1 = Point2(0, 0)
        p2 = Point2(3, 4)
        assert p1.distance(p2) == pytest.approx(5)

    def test_intersect(self):
        l1 = Line2((0, 0), (1, 1))
        l2 = Line2((0, 1), (1, 0))
        assert l1.intersect(l2) == Point2(0.5, 0.5)

    def test_point(self):
        s = Segment2((0, 0), (2, 2))
        assert s.point(0.5) == Point2(1, 1)

    def test_tangent(self):
        s = Segment2((0, 0), (2, 2))
        assert s.tangent(0.5) is not None

    def test___contains__(self):
        s = Segment2((0, 0), (2, 2))
        assert Point2(1, 1) in s
        assert Point2(3, 3) not in s

    def test_hash(self):
        from goulib.geom import _hash
        assert _hash((1, 2, 3)) != 0


class TestPoint2:
    @classmethod
    def setup_class(self):
        self.p00 = Point2(0, 0)
        self.p10 = Point2(1, 0)
        self.p01 = Point2(0, 1)
        self.p11 = Point2(1, 1)
        self.diag = Segment2(self.p10, self.p01)
        self.circle = Circle((1, 2), 1)

    def test___repr__(self):
        assert repr(self.p10) == 'Point2(1, 0)'

    def test_connect(self):
        assert self.p10.connect(self.p01) == self.diag
        assert (self.p10.connect(self.circle) ==
                Segment2(self.p10, self.p11))
        assert (self.circle.connect(self.p10) ==
                Segment2(self.p11, self.p10))

    def test_distance(self):
        assert self.p10.distance(self.p10) == 0
        assert self.p10.distance(self.p00) == 1
        assert self.p10.distance(self.p01) == sqrt(2)

        assert self.p00.distance(self.diag) == sqrt(2)/2
        assert self.p11.distance(self.diag) == sqrt(2)/2

    def test_intersect(self):
        p = self.p11.intersect(self.p11)  # Point2 intersects with itself
        assert p == self.p11
        assert not p is self.p11  # but intersect should return a COPY

        assert self.p11.intersect(self.p10) == None

        assert self.p10 in self.diag
        assert self.p01 in self.diag
        assert not self.p11 in self.diag

        assert self.p11 in self.circle

    def test___contains__(self):
        assert self.p01 in self.p01
        assert not Vector2(0, 1) in self.p01  # Vector2 is not a Point2
        assert not self.p10 in self.p01


class TestVector2:

    @classmethod
    def setup_class(self):
        self.v00 = Vector2(0, 0)
        self.v10 = Vector2(1, 0)
        self.v01 = Vector2(0, 1)
        self.v11 = Vector2(1, 1)

    def test___init__(self):
        # copy constructor
        v10 = Vector2(self.v10)
        assert v10 == self.v10
        assert not v10 is self.v10

    def test___repr__(self):
        assert repr(self.v10) == 'Vector2(1, 0)'

    def test___len__(self):
        assert len(self.v11) == 2

    def test___iter__(self):
        v = [v for v in self.v11]
        assert v == [1]*len(self.v11)

    def test_xy(self):
        assert self.v11.xy == (1, 1)

    def test___eq__(self):
        assert self.v11 == self.v11
        assert not self.v11 == self.v01

        assert self.v10 == (1, 0)
        # more tests embedded below

    def test___ne__(self):
        assert not self.v11 != self.v11
        assert self.v11 != self.v01

    def test___copy__(self):
        v10 = copy(self.v10)
        assert v10 == self.v10
        assert not v10 is self.v10  # make sure copy is a deepcopy

    def test_mag2(self):
        assert self.v11.mag2() == 2

    def test___abs__(self):
        assert abs(self.v11) == sqrt(2)

    def test_normalized(self):
        assert self.v10.normalized()  # test that it returns something, not None
        assert 1 == pytest.approx(abs(self.v11.normalized()))

    def test_normalize(self):
        v = copy(self.v11)
        v.normalize()
        assert 1 == pytest.approx(abs(v))

    def test___add__(self):
        assert self.v10+self.v01 == self.v11  # Vector + Vector -> Vector
        # Vector + Point -> Point
        assert self.v10+Point2(0, 1) == Point2(1, 1)
        # Point + Point -> Vector
        assert Point2(1, 0)+Point2(0, 1) == self.v11

    def test___iadd__(self):
        v = copy(self.v10)
        v += self.v01
        assert v == self.v11

    def test___neg__(self):
        assert -self.v11 == Vector2(-1, -1)

    def test___sub__(self):
        assert self.v11-self.v10 == self.v01  # Vector - Vector -> Vector
        # Vector - Point -> Point
        assert self.v11-Point2(1, 0) == Point2(0, 1)
        # Point - Point -> Vector
        assert Point2(1, 1)-Point2(1, 0) == self.v01

    def test___rsub__(self):
        assert (1, 1)-self.v10 == Point2(0, 1)  # Point - Vector -> Point

    def test___mul__(self):
        assert 2*self.v11 == Vector2(2, 2)
        assert self.v11*2 == Vector2(2, 2)

    def test___imul__(self):
        v = copy(self.v10)
        v *= 2
        assert v == Vector2(2, 0)

    def test___div__(self):
        assert self.v11/2. == Vector2(.5, .5)

    def test___floordiv__(self):
        assert self.v11//2. == Vector2(0, 0)

    def test___rdiv__(self):
        assert 2./self.v11 == Vector2(2, 2)

    def test___rfloordiv__(self):
        assert 2.//self.v11 == Vector2(2, 2)

    def test___truediv__(self):
        assert operator.truediv(self.v11, 3) == Vector2(1/3., 1/3.)

    def test___rtruediv__(self):
        assert operator.truediv(3, self.v11) == Vector2(3., 3.)

    def test_dot(self):
        assert self.v10.dot(self.v01) == 0
        assert self.v11.dot(self.v01) == 1

    def test_angle(self):
        assert self.v10.angle(self.v01) == pytest.approx(pi/2)
        assert self.v11.angle(self.v01) == pytest.approx(pi/4)

    def test_cross(self):
        assert self.v10.cross() == -self.v01

    def test_project(self):
        assert self.v10.project(self.v11) == Vector2(.5, .5)

    def test_reflect(self):
        assert self.v11.reflect(self.v10) == Vector2(-1, 1)

    def test___pos__(self):
        v10 = +self.v10  # copy
        assert v10 == self.v10
        assert not v10 is self.v10

    def test___hash__(self):
        assert Vector2(1, 0) in (self.v00, self.v01, self.v10, self.v11)


class TestMatrix3:
    @classmethod
    def setup_class(self):
        self.id3 = Matrix3()  # identity
        self.mat123 = Matrix3(1, 2, 3, 4, 5, 6, 7, 8, 9)  # singular
        self.mat456 = Matrix3(4, 5, 6, 9, 8, 7, 3, 1, 2)

    def test___init__(self):
        # default constructor makes an identity matrix
        assert self.id3 == Matrix3(1, 0, 0, 0, 1, 0, 0, 0, 1)
        # copy constructor
        mat123 = Matrix3(self.mat123)
        assert mat123 == self.mat123
        assert not mat123 is self.mat123

    def test___copy__(self):
        mat123 = copy(self.mat123)
        assert mat123 == self.mat123
        assert not mat123 is self.mat123

    def test___repr__(self):
        assert repr(self.mat123) == 'Matrix3(1, 4, 7, 2, 5, 8, 3, 6, 9)'

    def test_new_identity(self):
        mat = Matrix3.new_identity()
        assert mat == Matrix3()

    def test_new_scale(self):
        mat = Matrix3.new_scale(2, 3)
        assert mat == Matrix3(2, 0, 0, 0, 3, 0, 0, 0, 1)

    def test_new_rotate(self):
        mat = Matrix3.new_rotate(radians(60))
        s32 = sqrt(3)/2
        # warning : .new takes columnwise elements
        res = Matrix3(0.5, +s32, 0, -s32, 0.5, 0, 0, 0, 1)
        assert mat == res

    def test_new_translate(self):
        m = Matrix3.new_translate(3, 4)
        assert m.c == 3 and m.g == 4

    def test___call__(self):
        assert self.mat123(Vector2(10, 20)) == (90, 120)

    def test___getitem__(self):
        assert self.mat456.f == 8  # central element
        assert self.mat456[1, 1] == 8
        assert self.mat456[4] == 8

    def test___imul__(self):
        m = Matrix3.new_translate(1, 2)
        m *= Matrix3.new_scale(2, 3)
        assert m is not None

    def test___mul__(self):
        m = Matrix3.new_translate(1, 2) * Matrix3.new_scale(2, 3)
        assert m is not None

    def test___setitem__(self):
        pass  # used everywhere

    def test_angle(self):
        m = Matrix3.new_rotate(pi / 2)
        assert m.angle(0) == pytest.approx(pi / 2)

    def test_determinant(self):
        d = self.mat123.determinant()
        assert d == 0
        d = self.mat456.determinant()
        assert d == -39

    def test_identity(self):
        m = Matrix3.new_identity()
        assert m.a == 1 and m.f == 1 and m.k == 1

    def test_inverse(self):
        inv = self.mat123.inverse()
        assert inv == self.id3
        inv = self.mat456.inverse()
        assert inv[0, 0] == -0.23076923076923075

    def test_mag(self):
        m = Matrix3.new_scale(2, 2)
        assert m.mag() == pytest.approx(2)

    def test_offset(self):
        m = Matrix3.new_translate(3, 4)
        assert m.offset() == Point2(3, 4)

    def test_rotate(self):
        m = Matrix3().rotate(pi / 2)
        assert m is not None

    def test_scale(self):
        m = Matrix3().scale(2, 3)
        assert m is not None

    def test_translate(self):
        m = Matrix3().translate(2, 3)
        assert m is not None

    def test___abs__(self):
        assert abs(Matrix3()) > 0

    def test___eq__(self):
        assert Matrix3() == Matrix3.new_identity()

    def test___sub__(self):
        m = Matrix3() - Matrix3()
        assert m.a == 0

    def test_mag2(self):
        assert Matrix3().mag2() == 3

    def test_transpose(self):
        m = Matrix3.new_translate(2, 3)
        m.transpose()
        assert m is not None

    def test_transposed(self):
        m = Matrix3.new_translate(2, 3)
        mt = m.transposed()
        assert mt is not None

    def test___iter__(self):
        assert len(list(Matrix3())) == 9

    def test_orientation(self):
        assert Matrix3().orientation() == 1


class TestPolar:
    def test_polar(self):
        # assert_equal(expected, Polar(mag, angle))
        pytest.skip("not yet implemented")  # TODO: implement


class TestLine2:
    @classmethod
    def setup_class(self):
        self.l1 = Line2((1, 1), Vector2(1, 1))
        self.l2 = Line2((2, 2), Point2(-1, -1))  # parallel to l1
        assert self.l1.distance(self.l2) == 0
        # perpendicular to l1 and l2, normalized
        self.l3 = Line2((-1, -1), (-1, 1), 1)

    def test___init__(self):
        # copy constructor
        l1 = Line2(self.l1)
        assert l1 == self.l1
        assert not l1 is self.l1
        assert not l1.p is self.l1.p
        assert not l1.v is self.l1.v

    def test___repr__(self):
        assert repr(self.l3) == "Line2(Point2(-1, -1),Vector2(0.0, 1.0))"

    def test_connect(self):
        # line2 = Line2(*args)
        # assert_equal(expected, line2.connect(other))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_intersect(self):
        inter = self.l1.intersect(self.l2)
        assert self.l1.distance(inter) == 0
        assert self.l2.distance(inter) == 0
        inter = self.l2.intersect(self.l3)
        assert inter == Point2(-1, -1)
        inter = self.l1.intersect(self.l3)
        assert inter == Point2(-1, -1)

        # same tests as in Notebook
        a = Arc2((0, 0), (0, 1), (1, 0))
        l1 = Line2((-2, .5), Vector2(4, 0))  # horizontal at y=0.5
        l2 = Line2((-2, -.5), Vector2(4, 0))  # horizontal at y=-0.5

        # l1 has a single intersection with a
        p1 = Point2(-sqrt(3)/2, .5)
        inter = l1.intersect(a)
        assert inter == p1
        inter = a.intersect(l1)  # same intersection after entity swapping
        assert inter == p1

        # l2 has a two intersection with a
        p1 = Point2(sqrt(3)/2, -.5)
        p2 = Point2(-sqrt(3)/2, -.5)
        inter = l2.intersect(a)
        assert inter == [p1, p2]
        inter = a.intersect(l2)
        assert inter == [p1, p2]

    def test_point(self):
        assert self.l1.point(0) == self.l1.p
        assert self.l1.point(1) == self.l1.p+self.l1.v

    def test_tangent(self):
        assert self.l1.tangent(0) == self.l1.v

    def test___eq__(self):
        # line2 = Line2(*args)
        # assert_equal(expected, line2.__eq__(other))
        pytest.skip("not yet implemented")  # TODO: implement


class TestRay2:
    def test___repr__(self):
        # ray2 = Ray2()
        # assert_equal(expected, ray2.__repr__())
        pytest.skip("not yet implemented")  # TODO: implement


class TestSegment2:
    @classmethod
    def setup_class(self):
        self.s1 = Segment2((1, 1), Vector2(1, 1))  # (1,1) -> (2,2)
        # (2,2) -> (-1,-1) is parallel to s1
        self.s2 = Segment2((2, 2), Point2(-1, -1))
        # perpendicular to l1 and l2, normalized
        self.s3 = Segment2((-1, -1), (-1, 1), 1)

    def test___repr__(self):
        assert repr(self.s1) == "Segment2(Point2(1, 1),Point2(2, 2))"
        assert repr(self.s2) == "Segment2(Point2(2, 2),Point2(-1, -1))"
        assert repr(self.s3) == "Segment2(Point2(-1, -1),Point2(-1.0, 0.0))"

    def test___abs__(self):
        assert abs(self.s1) == sqrt(2)

    def test_mag2(self):
        assert self.s1.mag2() == 2

    def test_intersect(self):
        """TODO: implement intersect of colinear segments
        inter=self.s1.intersect(self.s2)
        assert_equal(self.s1.distance(inter),0)
        assert_equal(self.s2.distance(inter),0)
        """
        inter = self.s1.intersect(self.s3)
        assert inter == None
        inter = self.s2.intersect(self.s3)
        assert inter == Point2(-1, -1)

    def test_distance(self):
        assert self.s1.distance(self.s2) == 0
        assert self.s2.distance(self.s3) == 0
        assert self.s1.distance(self.s3) == 2*sqrt(2)

    def test_point(self):
        assert self.s1.point(0) == self.s1.p1
        assert self.s1.point(1) == self.s1.p2

    def test_tangent(self):
        assert self.s1.tangent(0) == self.s1.v
        assert self.s1.tangent(1) == self.s1.v
        assert self.s1.tangent(1.001) == None

    def test_swap(self):
        # segment2 = Segment2()
        # assert_equal(expected, segment2.swap())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_bisect(self):
        l = self.s1.bisect()
        assert l.intersect(self.s1) == self.s1.midpoint()
        assert l.v.dot(self.s1.v) == 0

    def test_midpoint(self):
        pass  # tested above


class TestPolygon:
    @classmethod
    def setup_class(self):
        def poly(n, r=1):
            for i in range(n):
                a = (2*i+1)*pi/n
                yield Point2(r*cos(a), r*sin(a))
        self.p4 = Polygon(poly(4, sqrt(2.)/2))
        self.p6 = Polygon(poly(6))

    def test___init__(self):
        pass  # tested above

    def test_length(self):
        assert self.p4.length == 4
        assert self.p6.length == 6

    def test_area(self):
        assert self.p4.area == pytest.approx(1)

    def test_center(self):
        assert self.p4.center == (0, 0)
        assert self.p6.center == (0, 0)

    def test_intersect(self):
        for x in self.p4.intersect(self.p4):
            print(x)
        # print(list(self.p4.intersect(self.p6)))


class TestCircle:
    @classmethod
    def setup_class(self):
        self.c1 = Circle(Point2(0, 0), 1)
        self.c2 = Circle((1, 0), 1)  # intersects c1
        self.c3 = Circle((3, 0), 1)  # tangent to c2, disjoint to c1

    def test___init__(self):
        pass  # tested above

    def test_point(self):
        assert self.c1.point(0) == (1, 0)

    def test_tangent(self):
        assert self.c1.tangent(0) == (0, 1)

    def test_length(self):
        assert self.c1.length == 2*pi
        assert self.c2.length == 2*pi
        assert self.c3.length == 2*pi

    def test_area(self):
        assert self.c1.area == pi
        assert self.c2.area == pi
        assert self.c3.area == pi

    def test_intersect(self):
        res = self.c1.intersect(self.c2)
        assert isinstance(res, list)
        assert len(res) == 2
        assert isinstance(res[0], Point2)
        assert isinstance(res[0], Point2)

        res = self.c1.intersect(self.c3)
        assert res == None

        res = self.c2.intersect(self.c3)
        assert isinstance(res, Point2)

        assert self.c1.intersect(self.c1) == self.c1

        large = Circle(self.c1.c, 1.1*self.c1.r)
        assert large.intersect(self.c1) == self.c1

    def test_connect(self):
        # circle = Circle(center, radius)
        # assert_equal(expected, circle.connect(other))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___abs__(self):
        # circle = Circle(center, radius)
        # assert_equal(expected, circle.__abs__())
        pytest.skip("not yet implemented")  # TODO: implement

    def test___eq__(self):
        # circle = Circle(center, radius)
        # assert_equal(expected, circle.__eq__(other))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___contains__(self):
        # circle = Circle(*args)
        # assert_equal(expected, circle.__contains__(pt))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_swap(self):
        # circle = Circle(*args)
        # assert_equal(expected, circle.swap())
        pytest.skip("not yet implemented")  # TODO: implement


class TestArc2:
    @classmethod
    def setup_class(self):
        self.a1 = Arc2((0, 0), (1, 0), (0, 1))
        self.a2 = Arc2((0, 0), 0, pi/2., 1)  # should be the same as a1
        self.a3 = Arc2((0, 0), pi/2., 0, 1, dir=-1)  # same, inverted
        self.ap = Arc2(center=Point2(454.80692478710336, 69.74749779176005), p1=Point2(
            74.67492478710335, 86.62949779176006), p2=Point2(74.48092478710339, 58.021497791760055), r=380.506687652)
        self.ap2 = Arc2(center=Point2(-454.80607521289664, -9.203502208239968), p1=Point2(-74.67307521289663, -
                                                                                          26.08650220823995), p2=Point2(-74.47907521289662, 2.521497791760055), r=380.507731036)

    def test___init__(self):
        # copy constructor
        a1 = Arc2(self.a1)
        assert a1 == self.a1
        assert not a1 is self.a1
        assert not a1.c is self.a1.c
        assert not a1.p is self.a1.p
        assert not a1.p2 is self.a1.p2

    def test___eq__(self):
        assert self.a1 == self.a2
        # inverted parametrization, but same geometry
        assert self.a1 == self.a3
        assert not self.a1 == self.ap

    def test_angle(self):
        assert self.a1.angle() == self.a2.angle()
        assert self.a1.angle() == -self.a3.angle()
        # check the angle is not the complementary angle
        assert self.ap.angle() < radians(10)
        # check the angle is not the complementary angle
        assert self.ap2.angle() < radians(10)

        c = Arc2((1, 1), r=1)  # unit circle around (1,1)
        assert c.angle() == 2*pi

        cw = Arc2((1, 1), r=1, dir=-1)  # unit circle around (1,1) clockwise
        assert cw.angle() == -2*pi

    def test___abs__(self):
        assert abs(self.a1) == pi/2.
        # check the angle is not the complementary angle
        assert self.ap.length < 50
        # check the angle is not the complementary angle
        assert self.ap2.length < 50

    def test___repr__(self):
        # arc2 = Arc2(center, p1, p2, r)
        # assert_equal(expected, arc2.__repr__())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_point(self):
        assert self.a1.point(0) == (1, 0)
        assert self.a1.point(1) == (0, 1)

    def test_tangent(self):
        assert self.a1.tangent(0) == (0, 1)
        assert self.a1.tangent(1) == (-1, 0)
        assert self.a2.tangent(0) == (0, 1)
        assert self.a2.tangent(1) == (-1, 0)
        # a3 direction is inverted wr to a1 and a2
        assert self.a3.tangent(0) == (1, 0)
        assert self.a3.tangent(1) == (0, -1)

        a = Arc2((1, 1), (3, 0), (3, 2))
        assert a.tangent(0) == (1, 2)
        assert a.tangent(1) == (-1, 2)

    def test_swap(self):
        # arc2 = Arc2(center, p1, p2, r, dir)
        # assert_equal(expected, arc2.swap())
        pytest.skip("not yet implemented")  # TODO: implement

    def test___contains__(self):
        # arc2 = Arc2(center, p1, p2, r, dir)
        # assert_equal(expected, arc2.__contains__(pt))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_intersect(self):
        # arc2 = Arc2(center, p1, p2, r, dir)
        # assert_equal(expected, arc2.intersect(other))
        pytest.skip("not yet implemented")  # TODO: implement


class TestArgPair:
    def test_arg_pair(self):
        assert argPair(1, 2) == (1, 2)
        assert argPair((1, 2)) == (1, 2)
        assert argPair([1, 2]) == (1, 2)

        # assert_equal(argPair(1),(1,1)) # not allowed anymore


class TestCopy:
    def test_copy(self):
        # assert_equal(expected, copy(object))
        pytest.skip("not yet implemented")  # TODO: implement


class TestCircleFrom3Points:
    def test_circle_from_3_points(self):
        p1 = Point2(-1, 0)
        p2 = Point2(0, 1)
        p3 = Point2(1, 0)
        c = circle_from_3_points(p1, p2, p3)
        assert c.c.xy == (0, 0)
        assert c.r == 1


class TestArcFrom3Points:
    def test_arc_from_3_points(self):
        p1 = Point2(-1, 0)
        p2 = Point2(0, 1)
        p3 = Point2(1, 0)
        a = arc_from_3_points(p1, p2, p3)
        assert a.c.xy == (0, 0)
        assert a.r == 1
        assert a.point(0.5) == p2

        p1 = Point2(-1, 0)
        p2 = Point2(0, -1)
        p3 = Point2(1, 0)
        a = arc_from_3_points(p1, p2, p3)
        assert a.c.xy == (0, 0)
        assert a.r == 1
        assert a.point(0.5) == p2

        p1 = Point2(1, 0)
        p2 = Point2(0, 1)
        p3 = Point2(-1, 0)
        a = arc_from_3_points(p1, p2, p3)
        assert a.c.xy == (0, 0)
        assert a.r == 1
        assert a.point(0.5) == p2

        p1 = Point2(1, 0)
        p2 = Point2(0, -1)
        p3 = Point2(-1, 0)
        a = arc_from_3_points(p1, p2, p3)
        assert a.c.xy == (0, 0)
        assert a.r == 1
        assert a.point(0.5) == p2


class TestEllipse:
    @classmethod
    def setup_class(self):
        self.e1 = Ellipse((1, 2), (3, 4))
        self.e2 = Ellipse((1, 2), 2, 2, pi/2)
        self.e3 = Ellipse(self.e2)
        assert self.e1 == self.e2

    def test___init__(self):
        pass

    def test___repr__(self):
        s = str(self.e1)
        assert s == 'Ellipse(Point2(1, 2),2,2)'

    def test___eq__(self):
        # ellipse = Ellipse(*args)
        # assert_equal(expected, ellipse.__eq__(other))
        pytest.skip("not yet implemented")  # TODO: implement
