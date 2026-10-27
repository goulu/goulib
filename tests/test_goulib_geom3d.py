from goulib.tests import *

from goulib.geom3d import *

from math import *


class TestVector3:
    @classmethod
    def setup_class(self):
        self.v00 = Vector3(0, 0, 0)
        self.v10 = Vector3(1, 0, 0)
        self.v01 = Vector3(0, 1, 0)
        self.v11 = Vector3(1, 1, 1)
        self.v011 = Vector3(0, 1, 1)
        self.v110 = Vector3(1, 1, 0)
        self.v123 = Vector3(1, 2, 3)
        self.v456 = Vector3(4, 5, 6)

    def test___init__(self):
        # test copy constructor
        v10 = Vector3(self.v10)
        assert v10 == self.v10
        assert not v10 is self.v10

    def test___repr__(self):
        assert repr(self.v10) == 'Vector3(1, 0, 0)'

    def test___len__(self):
        assert len(self.v11) == 3

    def test___iter__(self):
        v = [v for v in self.v11]
        assert v == [1]*len(self.v11)

    def test_xyz(self):
        assert self.v11.xyz == (1, 1, 1)

    def test___eq__(self):
        assert self.v11 == (1, 1, 1)
        assert self.v11 == self.v11
        assert not self.v11 == self.v01
        # more tests embedded below

    def test___ne__(self):
        assert not self.v11 != self.v11
        assert self.v11 != self.v01

    def test___nonzero__(self):
        assert self.v11
        assert not self.v00

    def test___copy__(self):
        v10 = copy(self.v10)
        assert v10 == self.v10
        assert not v10 is self.v10

    def test_mag2(self):
        assert self.v11.mag2() == 3

    def test___abs__(self):
        assert abs(self.v11) == sqrt(3)

    def test_normalized(self):
        assert self.v10.normalized()
        assert abs(self.v11.normalized()) == 1

    def test_normalize(self):
        v = copy(self.v11)
        v.normalize()
        assert abs(v) == 1

    def test___add__(self):
        assert self.v10+self.v01 == self.v110  # Vector + Vector -> Vector
        # Vector + Point -> Point
        assert self.v10+Point3(0, 1, 1) == Point3(1, 1, 1)
        # Point + Point -> Vector
        assert Point3(1, 0, 0.5)+Point3(0, 1, 0.5) == self.v11

    def test___iadd__(self):
        v = copy(self.v10)
        v += self.v01
        assert v == self.v110

    def test___neg__(self):
        assert -self.v11 == Vector3(-1, -1, -1)

    def test___sub__(self):
        assert self.v11-self.v10 == self.v011  # Vector - Vector -> Vector
        # Vector - Point -> Point
        assert self.v11-Point3(1, 0, 0) == Point3(0, 1, 1)
        # Point - Point -> Vector
        assert Point3(1, 1, 1)-Point3(1, 0, 1) == self.v01

    def test___rsub__(self):
        assert Point3(1, 1, 1)-self.v10 == Point3(0,
                                                  1, 1)  # Point - Vector -> Point

    def test___mul__(self):
        assert 2*self.v11 == Vector3(2, 2, 2)
        assert self.v11*2 == Vector3(2, 2, 2)

    def test___imul__(self):
        v = copy(self.v10)
        v *= 2
        assert v == Vector3(2, 0, 0)

    def test___div__(self):
        assert self.v11/2. == Vector3(0.5, 0.5, 0.5)

    def test___floordiv__(self):
        assert self.v11//2. == self.v00

    def test___rdiv__(self):
        assert 2./self.v11 == Vector3(2, 2, 2)

    def test___rfloordiv__(self):
        assert 2.//self.v11 == Vector3(2, 2, 2)

    def test___truediv__(self):
        assert operator.truediv(self.v11, 3) == Vector3(1/3., 1/3., 1/3.)

    def test___rtruediv__(self):
        assert operator.truediv(3, self.v11) == Vector3(3, 3, 3)

    def test_dot(self):
        assert self.v10.dot(self.v01) == 0
        assert self.v11.dot(self.v01) == 1

    def test_angle(self):
        assert self.v10.angle(self.v01) == pi/2.
        assert self.v11.angle(self.v01) == acos(1/sqrt(3))

    def test_cross(self):
        assert self.v123.cross(self.v456) == Vector3(-3.00, 6.00, -3.00)

    def test_project(self):
        assert self.v10.project(self.v11) == Vector3(1/3., 1/3., 1/3.)

    def test_reflect(self):
        assert self.v11.reflect(self.v10) == Vector3(-1, 1, 1)

    def test_rotate_around(self):
        v = Vector3(1, 0, 0)
        assert math2.allclose(v.rotate_around(Vector3(0, 0, 1), pi/2), Vector3(0, 1, 0), abs_tol=1e-7)

    def test___bool__(self):
        assert bool(self.v11)
        assert not bool(self.v00)

    def test___pos__(self):
        assert +self.v11 == self.v11


class TestMatrix4:
    @classmethod
    def setup_class(self):
        self.mat123 = Matrix4(1, 2, 3, 0, 4, 5, 6, 0, 7, 8, 9, 0, 0, 0, 0, 1)

    def test___init__(self):
        # default constructor makes an identity matrix
        assert Matrix4() == Matrix4(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
        # copy constructor
        mat123 = Matrix4(self.mat123)
        assert mat123 == self.mat123
        assert not mat123 is self.mat123

    def test___copy__(self):
        mat123 = copy(self.mat123)
        assert mat123 == self.mat123
        assert not mat123 is self.mat123

    def test___call__(self):
        assert self.mat123(Vector3(1, 10, 100)) == (741, 852, 963)

    def test___getitem__(self):
        assert self.mat123[1*4+2] == 6

    def test___imul__(self):
        m = Matrix4()
        m *= Matrix4.new_scale(2, 3, 4)
        assert m == Matrix4.new_scale(2, 3, 4)

    def test___mul__(self):
        assert self.mat123*Vector3(1, 10, 100) == (741, 852, 963)
        assert self.mat123 * Point3(1, 10, 100) == Point3(741, 852, 963)

    def test___repr__(self):
        assert 'Matrix4' in repr(self.mat123)

    def test___setitem__(self):
        m = Matrix4()
        m[0] = 5
        assert m[0] == 5

    def test_determinant(self):
        assert math2.isclose(Matrix4.new_scale(2, 3, 4).determinant(), 24)

    def test_identity(self):
        m = Matrix4().scale(2, 2, 2)
        m.identity()
        assert m == Matrix4()

    def test_inverse(self):
        m = Matrix4.new_translate(1, 2, 3)
        assert math2.allclose(m.inverse() * m, Matrix4(), abs_tol=1e-7)
        # degenerate matrix returns identity
        assert Matrix4.new_scale(0, 0, 0).inverse() == Matrix4()

    def test_new(self):
        assert Matrix4.new_identity() == Matrix4()

    def test_new_identity(self):
        assert Matrix4.new_identity() == Matrix4()

    def test_new_look_at(self):
        m = Matrix4.new_look_at(Point3(0, 0, 10), Point3(0, 0, 0), Vector3(0, 1, 0))
        assert isinstance(m, Matrix4)

    def test_new_perspective(self):
        m = Matrix4.new_perspective(pi/4, 1.33, 1.0, 100.0)
        assert isinstance(m, Matrix4)

    def test_new_rotate_axis(self):
        m = Matrix4.new_rotate_axis(pi/2, Vector3(0, 0, 1))
        p = m * Point3(1, 0, 0)
        assert math2.allclose(p, Point3(0, 1, 0), abs_tol=1e-7)

    def test_new_rotate_euler(self):
        assert Matrix4.new_rotate_euler(0, 0, 0) == Matrix4()

    def test_new_rotate_triple_axis(self):
        m = Matrix4.new_rotate_triple_axis(Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1))
        assert m == Matrix4()

    def test_new_rotatex(self):
        assert isinstance(Matrix4.new_rotatex(pi/2), Matrix4)

    def test_new_rotatey(self):
        assert isinstance(Matrix4.new_rotatey(pi/2), Matrix4)

    def test_new_rotatez(self):
        assert isinstance(Matrix4.new_rotatez(pi/2), Matrix4)

    def test_new_scale(self):
        assert Matrix4.new_scale(2, 3, 4) * Vector3(1, 1, 1) == Vector3(2, 3, 4)

    def test_new_translate(self):
        assert Matrix4.new_translate(2, 3, 4) * Point3(0, 0, 0) == Point3(2, 3, 4)

    def test_rotate_axis(self):
        m = Matrix4().rotate_axis(pi/2, Vector3(0, 0, 1))
        assert math2.allclose(m * Point3(1, 0, 0), Point3(0, 1, 0), abs_tol=1e-7)

    def test_rotate_euler(self):
        assert Matrix4().rotate_euler(0, 0, 0) == Matrix4()

    def test_rotate_triple_axis(self):
        assert Matrix4().rotate_triple_axis(Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1)) == Matrix4()

    def test_rotatex(self):
        assert isinstance(Matrix4().rotatex(pi/4), Matrix4)

    def test_rotatey(self):
        assert isinstance(Matrix4().rotatey(pi/4), Matrix4)

    def test_rotatez(self):
        assert isinstance(Matrix4().rotatez(pi/4), Matrix4)

    def test_scale(self):
        m = Matrix4().scale(2, 3, 4)
        assert m * Vector3(1, 1, 1) == Vector3(2, 3, 4)

    def test_transform(self):
        m = Matrix4.new_translate(1, 2, 3)
        assert m.transform(Point3(0, 0, 0)) == Point3(1, 2, 3)

    def test_translate(self):
        m = Matrix4().translate(1, 2, 3)
        assert m * Point3(0, 0, 0) == Point3(1, 2, 3)

    def test_transpose(self):
        m = Matrix4.new_translate(1, 2, 3)
        mt = m.transposed()
        m_copy = copy(m)
        m_copy.transpose()
        assert m_copy == mt

    def test_transposed(self):
        m = Matrix4.new_translate(1, 2, 3)
        assert m.transposed().transposed() == m

    def test___iter__(self):
        assert len(list(Matrix4())) == 16


class TestQuaternion:
    def test___init__(self):
        q = Quaternion(1, 0, 0, 0)
        assert q.w == 1 and q.x == 0 and q.y == 0 and q.z == 0

    def test___abs__(self):
        assert math2.isclose(abs(Quaternion(1, 0, 0, 0)), 1.0)

    def test___copy__(self):
        q = Quaternion(1, 2, 3, 4)
        assert copy(q).w == 1

    def test___imul__(self):
        q1 = Quaternion.new_rotate_axis(pi/2, Vector3(1, 0, 0))
        q2 = Quaternion.new_rotate_axis(pi/2, Vector3(0, 1, 0))
        q3 = q1 * q2
        q1 *= q2
        assert math2.isclose(q1.w, q3.w)

    def test___mul__(self):
        q1 = Quaternion.new_rotate_axis(pi/2, Vector3(1, 0, 0))
        q2 = Quaternion.new_rotate_axis(pi/2, Vector3(0, 1, 0))
        assert isinstance(q1 * q2, Quaternion)
        assert isinstance(q1 * Vector3(1, 0, 0), Vector3)

    def test___repr__(self):
        assert 'Quaternion' in repr(Quaternion())

    def test_conjugated(self):
        q = Quaternion(1, 2, 3, 4)
        qc = q.conjugated()
        assert (qc.w, qc.x, qc.y, qc.z) == (1, -2, -3, -4)

    def test_get_angle_axis(self):
        q = Quaternion.new_rotate_axis(pi/2, Vector3(1, 0, 0))
        angle, axis = q.get_angle_axis()
        assert math2.isclose(angle, pi/2)
        assert math2.allclose(axis, Vector3(1, 0, 0))

    def test_get_euler(self):
        q = Quaternion.new_rotate_euler(pi/2, 0, 0)
        assert len(q.get_euler()) == 3

    def test_get_matrix(self):
        q = Quaternion.new_rotate_axis(pi/2, Vector3(1, 0, 0))
        assert isinstance(q.get_matrix(), Matrix4)

    def test_identity(self):
        q = Quaternion(2, 3, 4, 5)
        q.identity()
        assert q.w == 1 and q.x == 0

    def test_mag2(self):
        assert Quaternion(1, 2, 2, 0).mag2() == 9

    def test_new_identity(self):
        assert Quaternion.new_identity().w == 1

    def test_new_interpolate(self):
        q1 = Quaternion.new_rotate_axis(pi/2, Vector3(1, 0, 0))
        q2 = Quaternion.new_rotate_axis(pi/2, Vector3(0, 1, 0))
        assert isinstance(Quaternion.new_interpolate(q1, q2, 0.5), Quaternion)

    def test_new_rotate_axis(self):
        assert isinstance(Quaternion.new_rotate_axis(pi/4, Vector3(0, 0, 1)), Quaternion)

    def test_new_rotate_euler(self):
        assert isinstance(Quaternion.new_rotate_euler(0.1, 0.2, 0.3), Quaternion)

    def test_new_rotate_matrix(self):
        assert isinstance(Quaternion.new_rotate_matrix(Matrix4()), Quaternion)
        m_x = Matrix4.new_rotatex(pi)
        assert isinstance(Quaternion.new_rotate_matrix(m_x), Quaternion)
        m_y = Matrix4.new_rotatey(pi)
        assert isinstance(Quaternion.new_rotate_matrix(m_y), Quaternion)
        m_z = Matrix4.new_rotatez(pi)
        assert isinstance(Quaternion.new_rotate_matrix(m_z), Quaternion)

    def test_normalize(self):
        q = Quaternion(2, 0, 0, 0)
        q.normalize()
        assert math2.isclose(abs(q), 1.0)

    def test_normalized(self):
        q = Quaternion(2, 0, 0, 0)
        assert math2.isclose(abs(q.normalized()), 1.0)

    def test_rotate_axis(self):
        assert isinstance(Quaternion().rotate_axis(pi/2, Vector3(1, 0, 0)), Quaternion)

    def test_rotate_euler(self):
        assert isinstance(Quaternion().rotate_euler(pi/2, 0, 0), Quaternion)

    def test_rotate_matrix(self):
        assert isinstance(Quaternion().rotate_matrix(Matrix4()), Quaternion)


class TestPoint3:
    def test___repr__(self):
        p = Point3(1, 2, 3)
        assert repr(p) == 'Point3(1, 2, 3)'

    def test_connect(self):
        p1 = Point3(0, 0, 0)
        p2 = Point3(0, 0, 5)
        assert abs(p1.connect(p2)) == 5

    def test_intersect(self):
        s = Sphere(Point3(0, 0, 0), 2)
        assert Point3(0, 0, 1).intersect(s)
        assert not Point3(0, 0, 3).intersect(s)


class TestLine3:
    def test___copy__(self):
        l = Line3(Point3(0, 0, 0), Vector3(1, 0, 0))
        assert copy(l).p == l.p

    def test___init__(self):
        l1 = Line3(Point3(0, 0, 0), Vector3(1, 0, 0))
        l2 = Line3(Point3(0, 0, 0), Point3(1, 0, 0))
        assert l1.p == l2.p

    def test___repr__(self):
        assert 'Line3' in repr(Line3(Point3(0, 0, 0), Vector3(1, 0, 0)))

    def test_connect(self):
        l1 = Line3(Point3(0, 0, 0), Vector3(1, 0, 0))
        l2 = Line3(Point3(0, 1, 0), Vector3(0, 0, 1))
        assert math2.isclose(abs(l1.connect(l2)), 1.0)

    def test_intersect(self):
        plane = Plane(Point3(0, 0, 5), Vector3(0, 0, 1))
        l = Line3(Point3(0, 0, 0), Vector3(0, 0, 1))
        assert l.intersect(plane) == Point3(0, 0, 5)

    def test_point(self):
        l = Line3(Point3(0, 0, 0), Vector3(1, 0, 0))
        assert l.point(2) == Point3(2, 0, 0)


class TestRay3:
    def test___repr__(self):
        assert 'Ray3' in repr(Ray3(Point3(0, 0, 0), Vector3(1, 0, 0)))


class TestSegment3:
    def test___abs__(self):
        seg = Segment3(Point3(0, 0, 0), Point3(3, 4, 0))
        assert math2.isclose(abs(seg), 5.0)

    def test___repr__(self):
        assert 'Segment3' in repr(Segment3(Point3(0, 0, 0), Point3(1, 1, 1)))

    def test_mag2(self):
        assert Segment3(Point3(0, 0, 0), Point3(3, 4, 0)).mag2() == 25

    def test_swap(self):
        seg = Segment3(Point3(0, 0, 0), Point3(1, 0, 0))
        assert seg.swap().p1 == Point3(1, 0, 0)


class TestSphere:
    def test___copy__(self):
        s = Sphere(Point3(0, 0, 0), 2)
        assert copy(s).r == 2

    def test___init__(self):
        s = Sphere(Point3(1, 2, 3), 2)
        assert s.r == 2

    def test___repr__(self):
        assert 'Sphere' in repr(Sphere(Point3(0, 0, 0), 1))

    def test_connect(self):
        s1 = Sphere(Point3(0, 0, 0), 2)
        s2 = Sphere(Point3(5, 0, 0), 1)
        assert math2.isclose(abs(s1.connect(s2)), 2.0)

    def test_intersect(self):
        s = Sphere(Point3(0, 0, 0), 2)
        l = Line3(Point3(-5, 0, 0), Vector3(1, 0, 0))
        assert s.intersect(l) is not None

    def test___contains__(self):
        s = Sphere(Point3(0, 0, 0), 2)
        assert Point3(1, 0, 0) in s
        assert Point3(3, 0, 0) not in s

    def test_distance_on_sphere(self):
        s = Sphere(Point3(0, 0, 0), 2)
        assert math2.isclose(s.distance_on_sphere(0, 0, pi/2, 0), pi)

    def test_point(self):
        s = Sphere(Point3(0, 0, 0), 2)
        assert math2.allclose(s.point(pi/2, 0), Point3(2, 0, 2), abs_tol=1e-7)


class TestPlane:
    def test___copy__(self):
        p = Plane(Point3(0, 0, 0), Vector3(0, 0, 1))
        assert copy(p).k == p.k

    def test___init__(self):
        p = Plane(Point3(0, 0, 0), Vector3(0, 0, 1))
        assert p.k == 0

    def test___repr__(self):
        assert 'Plane' in repr(Plane(Point3(0, 0, 0), Vector3(0, 0, 1)))

    def test_connect(self):
        p = Plane(Point3(0, 0, 0), Vector3(0, 0, 1))
        assert math2.isclose(abs(p.connect(Point3(0, 0, 5))), 5.0)

    def test_intersect(self):
        p1 = Plane(Point3(0, 0, 0), Vector3(0, 0, 1))
        p2 = Plane(Point3(0, 0, 0), Vector3(0, 1, 0))
        assert isinstance(p1.intersect(p2), Line3)

    def test_distance(self):
        p1, p2, p3, p4 = Point3(1, 2, 0), Point3(2, 3, 0), Point3(4, 0, 0), Point3(0, 0, 0)
        plane = Plane(p1, p2, p3)
        assert plane.distance(p4) == 0
        assert Point3(1, 2, 3).distance(plane) == 3

    def test_connect_more(self):
        s = Sphere(Point3(0, 0, 0), 1)
        p = Plane(Point3(0, 0, 5), Vector3(0, 0, 1))
        assert s.connect(p) is not None
        l = Line3(Point3(0, 5, 0), Vector3(1, 0, 0))
        assert s.connect(l) is not None
        assert l.connect(p) is not None
        p2 = Plane(Point3(0, 0, 10), Vector3(0, 0, 1))
        assert p.connect(p2) is not None
        assert p.connect(Plane(Point3(0, 0, 0), Vector3(1, 0, 0))) is None
        l2 = Line3(Point3(0, 6, 0), Vector3(1, 0, 0))
        assert l.connect(l2) is not None
        r = Ray3(Point3(0, 6, 0), Vector3(1, 0, 0))
        assert l.connect(r) is not None
        pt = Point3(0, 0, 0)
        assert pt.connect(s) is not None
        s2 = Sphere(Point3(0.5, 0, 0), 0.2)
        assert s.connect(s2) is not None
        assert s2.connect(s) is not None


class TestSpherical:
    def test_spherical(self):
        v = Spherical(1, pi/2, 0)
        assert math2.allclose(v, Vector3(1, 0, 1), abs_tol=1e-7)
