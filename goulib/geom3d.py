"""
3D geometry
"""

__author__ = "Alex Holkner, Philippe Guglielmetti"
__copyright__ = "Copyright (c) 2006 Alex Holkner"
__license__ = "LGPL"
__credits__ = [
    'http://code.google.com/p/pyeuclid',
    'http://www.nmt.edu/tcc/help/lang/python/examples/homcoord/']

__docformat__ = 'restructuredtext'
__version__ = '$Id$'
__revision__ = '$Revision$'

import operator

from math import pi, sin, cos, tan, acos, asin, atan2, sqrt
import goulib.math2 as math2

from .geom import Geometry, copy

# 3D Geometry
# -------------------------------------------------------------------------

"""
**3D Geometry**

The following classes are available for dealing with simple 3D geometry.
The interfaces are very similar to the 2D classes (but note that you
cannot mix and match 2D and 3D operations).

For example, to find the closest point on a line to a sphere::

    >>> sphere = Sphere(Point3(1., 2., 3.,), 2.)
    >>> line = Line3(Point3(0., 0., 0.), Point3(-1., -1., 0.))
    >>> line.connect(sphere).p1
    Point3(1.50, 1.50, 0.00)

To find the corresponding closest point on the sphere to the line::

    >>> line.connect(sphere).p2
    Point3(1.32, 1.68, 1.05)

XXX I have not checked if these are correct.
"""


def _connect_point3_line3(P, L):
    d = L.v.mag2()
    # assert d != 0
    u = ((P.x - L.p.x) * L.v.x +
         (P.y - L.p.y) * L.v.y +
         (P.z - L.p.z) * L.v.z) / d
    if not L._u_in(u):
        u = max(min(u, 1.0), 0.0)
    return Segment3(P, Point3(L.p.x + u * L.v.x,
                              L.p.y + u * L.v.y,
                              L.p.z + u * L.v.z))


def _connect_point3_sphere(P, S):
    v = P - S.c
    v.normalize()
    v *= S.r
    return Segment3(P, Point3(S.c.x + v.x, S.c.y + v.y, S.c.z + v.z))


def _connect_point3_plane(p, plane):
    n = plane.n.normalized()
    d = p.dot(plane.n) - plane.k
    return Segment3(p, Point3(p.x - n.x * d, p.y - n.y * d, p.z - n.z * d))


def _connect_line3_line3(A, B):
    # assert A.v and B.v
    p13 = A.p - B.p
    d1343 = p13.dot(B.v)
    d4321 = B.v.dot(A.v)
    d1321 = p13.dot(A.v)
    d4343 = B.v.mag2()
    denom = A.v.mag2() * d4343 - d4321 ** 2
    if denom == 0:
        # Parallel, connect an endpoint with a line
        if isinstance(B, Ray3) or isinstance(B, Segment3):
            return _connect_point3_line3(B.p, A).swap()
        # No endpoint (or endpoint is on A), possibly choose arbitrary
        # point on line.
        return _connect_point3_line3(A.p, B)

    ua = (d1343 * d4321 - d1321 * d4343) / denom
    if not A._u_in(ua):
        ua = max(min(ua, 1.0), 0.0)
    ub = (d1343 + d4321 * ua) / d4343
    if not B._u_in(ub):
        ub = max(min(ub, 1.0), 0.0)
    return Segment3(Point3(A.p.x + ua * A.v.x,
                           A.p.y + ua * A.v.y,
                           A.p.z + ua * A.v.z),
                    Point3(B.p.x + ub * B.v.x,
                           B.p.y + ub * B.v.y,
                           B.p.z + ub * B.v.z))


def _connect_line3_plane(L, P):
    d = P.n.dot(L.v)
    if not d:
        # Parallel, choose an endpoint
        return _connect_point3_plane(L.p, P)
    u = (P.k - P.n.dot(L.p)) / d
    if not L._u_in(u):
        # intersects out of range, choose nearest endpoint
        u = max(min(u, 1.0), 0.0)
        return _connect_point3_plane(Point3(L.p.x + u * L.v.x,
                                            L.p.y + u * L.v.y,
                                            L.p.z + u * L.v.z), P)
    # Intersection
    return None


def _connect_sphere_line3(S, L):
    """
        Sphere/Line shortest joining segment
        :param S: Sphere
        :param L: Line
        :return: LineSegment3 of minimal length
        """
    d = L.v.mag2()
    # assert d != 0
    u = ((S.c.x - L.p.x) * L.v.x +
         (S.c.y - L.p.y) * L.v.y +
         (S.c.z - L.p.z) * L.v.z) / d
    if not L._u_in(u):
        u = max(min(u, 1.0), 0.0)
    point = L.point(u)
    v = (point - S.c)
    v.normalize()
    v *= S.r
    return Segment3(S.c + v, point)


def _connect_sphere_sphere(A, B):
    v = B.c - A.c
    d = v.mag()
    if A.r >= B.r and d < A.r:
        # centre B inside A
        s1, s2 = +1, +1
    elif B.r > A.r and d < B.r:
        # centre A inside B
        s1, s2 = -1, -1
    elif d >= A.r and d >= B.r:
        s1, s2 = +1, -1

    v.normalize()
    return Segment3(Point3(A.c.x + s1 * v.x * A.r,
                           A.c.y + s1 * v.y * A.r,
                           A.c.z + s1 * v.z * A.r),
                    Point3(B.c.x + s2 * v.x * B.r,
                           B.c.y + s2 * v.y * B.r,
                           B.c.z + s2 * v.z * B.r))


def _connect_sphere_plane(S, P):
    c = _connect_point3_plane(S.c, P)
    if not c:
        return None
    p2 = c.p2
    v = p2 - S.c
    v.normalize()
    v *= S.r
    return Segment3(Point3(S.c.x + v.x, S.c.y + v.y, S.c.z + v.z),
                    p2)


def _connect_plane_plane(A, B):
    if A.n.cross(B.n):
        # Planes intersect
        return None
    else:
        # Planes are parallel, connect to arbitrary point
        return _connect_point3_plane(A._get_point(), B)


def _intersect_line3_sphere(L, S):
    a = L.v.mag2()
    b = 2 * (L.v.x * (L.p.x - S.c.x) +
             L.v.y * (L.p.y - S.c.y) +
             L.v.z * (L.p.z - S.c.z))
    c = S.c.mag2() + \
        L.p.mag2() - \
        2 * S.c.dot(L.p) - \
        S.r ** 2
    det = b ** 2 - 4 * a * c
    if det < 0:
        return None
    sq = sqrt(det)
    u1 = (-b + sq) / (2 * a)
    u2 = (-b - sq) / (2 * a)
    p1 = L.point(u1)
    p2 = L.point(u2)
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    return Segment3(p1, p2)


def _intersect_line3_plane(L, P):
    d = P.n.dot(L.v)
    if not d:
        # Parallel
        return None
    u = (P.k - P.n.dot(L.p)) / d
    if not L._u_in(u):
        return None
    return Point3(L.p.x + u * L.v.x,
                  L.p.y + u * L.v.y,
                  L.p.z + u * L.v.z)


def _intersect_plane_plane(A, B):
    n1_m = A.n.mag2()
    n2_m = B.n.mag2()
    n1d2 = A.n.dot(B.n)
    det = n1_m * n2_m - n1d2 ** 2
    if det == 0:
        # Parallel
        return None
    c1 = (A.k * n2_m - B.k * n1d2) / det
    c2 = (B.k * n1_m - A.k * n1d2) / det
    return Line3(Point3(c1 * A.n.x + c2 * B.n.x,
                        c1 * A.n.y + c2 * B.n.y,
                        c1 * A.n.z + c2 * B.n.z),
                 A.n.cross(B.n))


class Vector3(object):
    """Mutable 3D Vector.
    See :class:`Vector2` documentation
    """

    def __init__(self, *args):
        """Constructor.
        :param args: x,y,z values
        """
        if len(args) == 1:
            value = args[0]
            # assert(len(value) == 3)
            x, y, z = value
        else:
            x, y, z = args
        self.x = x
        self.y = y
        self.z = z

    @property
    def xyz(self):
        """:return: tuple (x,y,z)"""
        return (self.x, self.y, self.z)

    def __eq__(self, other):
        try:
            return math2.allclose(self.xyz, other.xyz)
        except AttributeError:
            return math2.allclose(self.xyz, other)

    def __repr__(self):
        return '%s%s' % (self.__class__.__name__, self.xyz)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        return self.x != 0 or self.y != 0 or self.z != 0

    __nonzero__ = __bool__

    def __len__(self):
        return 3

    def __iter__(self):
        return iter(self.xyz)

    def __add__(self, other):
        try:
            # Vector + Vector -> Vector
            # Vector + Point -> Point
            # Point + Point -> Vector
            if self.__class__ is other.__class__:
                _class = Vector3
            else:
                _class = Point3
            return _class(self.x + other.x,
                          self.y + other.y,
                          self.z + other.z)
        except:
            return Vector3(self.x + other[0],
                           self.y + other[1],
                           self.z + other[2])

    __radd__ = __add__

    def __iadd__(self, other):
        try:
            self.x += other.x
            self.y += other.y
            self.z += other.z
        except:
            self.x += other[0]
            self.y += other[1]
            self.z += other[2]
        return self

    def __sub__(self, other):
        try:
            # Vector - Vector -> Vector
            # Vector - Point -> Point
            # Point - Point -> Vector
            if self.__class__ is other.__class__:
                _class = Vector3
            else:
                _class = Point3
            return _class(self.x - other.x,
                          self.y - other.y,
                          self.z - other.z)
        except:
            # assert hasattr(other, '__len__') and len(other) == 3
            return Vector3(self.x - other[0],
                           self.y - other[1],
                           self.z - other[2])

    def __rsub__(self, other):
        return Vector3(other.x - self.x,
                       other.y - self.y,
                       other.z - self.z)

    def __mul__(self, other):
        try:
            # TODO: component-wise mul/div in-place and on Vector2; docs.
            if self.__class__ is Point3 or other.__class__ is Point3:
                _class = Point3
            else:
                _class = Vector3
            return _class(self.x * other.x,
                          self.y * other.y,
                          self.z * other.z)
        except:
            # assert type(other) in (int, int, float)
            return Vector3(self.x * other,
                           self.y * other,
                           self.z * other)

    __rmul__ = __mul__

    def __imul__(self, other):
        # assert type(other) in (int, int, float)
        self.x *= other
        self.y *= other
        self.z *= other
        return self

    # geometry requires truediv even in Python2

    def __div__(self, other):
        # assert type(other) in (int, int, float)
        return Vector3(operator.truediv(self.x, other),
                       operator.truediv(self.y, other),
                       operator.truediv(self.z, other))

    def __rdiv__(self, other):
        # assert type(other) in (int, int, float)
        return Vector3(operator.truediv(other, self.x),
                       operator.truediv(other, self.y),
                       operator.truediv(other, self.z))

    def __floordiv__(self, other):
        # assert type(other) in (int, int, float)
        return Vector3(operator.floordiv(self.x, other),
                       operator.floordiv(self.y, other),
                       operator.floordiv(self.z, other))

    def __rfloordiv__(self, other):
        # assert type(other) in (int, int, float)
        return Vector3(operator.floordiv(other, self.x),
                       operator.floordiv(other, self.y),
                       operator.floordiv(other, self.z))

    def __truediv__(self, other):
        # assert type(other) in (int, int, float)
        return Vector3(operator.truediv(self.x, other),
                       operator.truediv(self.y, other),
                       operator.truediv(self.z, other))

    def __rtruediv__(self, other):
        # assert type(other) in (int, int, float)
        return Vector3(operator.truediv(other, self.x),
                       operator.truediv(other, self.y),
                       operator.truediv(other, self.z))

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    def __pos__(self):
        return Vector3(self)

    def __abs__(self):
        return sqrt(self.mag2())

    mag = __abs__

    def mag2(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def normalize(self):
        d = self.mag()
        if d:
            self.x /= d
            self.y /= d
            self.z /= d
        return self

    def normalized(self):
        res = copy(self)
        return res.normalize()

    def dot(self, other):
        # assert isinstance(other, Vector3)
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector3(self.y * other.z - self.z * other.y,
                       -self.x * other.z + self.z * other.x,
                       self.x * other.y - self.y * other.x)

    def reflect(self, normal):
        # assume normal is normalized
        # assert isinstance(normal, Vector3)
        d = 2 * (self.x * normal.x + self.y * normal.y + self.z * normal.z)
        return Vector3(self.x - d * normal.x,
                       self.y - d * normal.y,
                       self.z - d * normal.z)

    def rotate_around(self, axis, theta):
        """Return the vector rotated around axis through angle theta. Right hand rule applies"""

        # Adapted from equations published by Glenn Murray.
        # http://inside.mines.edu/~gmurray/ArbitraryAxisRotation/ArbitraryAxisRotation.html
        x, y, z = self.x, self.y, self.z
        u, v, w = axis.x, axis.y, axis.z

        # Extracted common factors for simplicity and efficiency
        r2 = u ** 2 + v ** 2 + w ** 2
        r = sqrt(r2)
        ct = cos(theta)
        st = sin(theta) / r
        dt = (u * x + v * y + w * z) * (1 - ct) / r2
        return Vector3((u * dt + x * ct + (-w * y + v * z) * st),
                       (v * dt + y * ct + (w * x - u * z) * st),
                       (w * dt + z * ct + (-v * x + u * y) * st))

    def angle(self, other):
        """angle between two vectors.
        :param other: Vector3
        :return: float angle in radians to the other vector, or self direction if other=None
        """
        return acos(self.dot(other) / (self.mag() * other.mag()))

    def project(self, other):
        """Return one vector projected on the vector other"""
        n = other.normalized()
        return self.dot(n) * n


class Point3(Vector3, Geometry):
    """
    A point on a 3D plane.  Construct in the obvious way::

        >>> p = Point3(1.0, 2.0, 3.0)
        >>> p
        Point3(1.00, 2.00, 3.00)

    **Point3** subclasses **Vector3**, so all of **Vector3** operators and
    methods apply.  In particular, subtracting two points gives a vector::

        >>> Point3(1.0, 2.0, 3.0) - Point3(1.0, 0.0, -2.0)
        Vector3(0.00, 2.00, 5.00)

    The following methods are also defined:

    ``intersect(other)``
        If *other* is a **Sphere**, returns ``True`` iff the point lies within
        the sphere.

    ``connect(other)``
        Returns a **LineSegment3** which is the minimum length line segment
        that can connect the two shapes.  *other* may be a **Point3**, **Line3**,
        **Ray3**, **LineSegment3**, **Sphere** or **Plane**.

    ``distance(other)``
        Returns the absolute minimum distance to *other*.  Internally this
        simply returns the length of the result of ``connect``.
    """

    def intersect(self, other):
        """Point3/object intersection
        :return: self Point3 if on other object, None if not
        """
        return self if self in other else None

    def connect(self, other):
        return other._connect_point3(self)

    def _connect_point3(self, other):
        if self != other:
            return Segment3(other, self)
        return None

    def _connect_line3(self, other):
        c = _connect_point3_line3(self, other)
        if c:
            return c.swap()

    def _connect_sphere(self, other):
        c = _connect_point3_sphere(self, other)
        if c:
            return c.swap()

    def _connect_plane(self, other):
        c = _connect_point3_plane(self, other)
        if c:
            return c.swap()


class Line3(Geometry):
    """
    A **Line3** is a line on a 3D plane extending to infinity in both directions;
    a **Ray3** has a finite end-point and extends to infinity in a single
    direction; a **LineSegment3** joins two points.

    All three classes support the same constructors, operators and methods,
    but may behave differently when calculating intersections etc.

    You may construct a line, ray or line segment using any of:

    * another line, ray or line segment
    * two points
    * a point and a vector
    * a point, a vector and a length

    For example::

        >>> Line3(Point3(1.0, 1.0, 1.0), Point3(1.0, 2.0, 3.0))
        Line3(<1.00, 1.00, 1.00> + u<0.00, 1.00, 2.00>)
        >>> Line3(Point3(0.0, 1.0, 1.0), Vector3(1.0, 1.0, 2.0))
        Line3(<0.00, 1.00, 1.00> + u<1.00, 1.00, 2.00>)
        >>> Ray3(Point3(1.0, 1.0, 1.0), Vector3(1.0, 1.0, 2.0), 1.0)
        Ray3(<1.00, 1.00, 1.00> + u<0.41, 0.41, 0.82>)

    Internally, lines, rays and line segments store a Point3 *p* and a
    Vector3 *v*.  You can also access (but not set) the two endpoints
    *p1* and *p2*.  These may or may not be meaningful for all types of lines.

    The following methods are supported by all three classes:

    ``intersect(other)``
        If *other* is a **Sphere**, returns a **LineSegment3** which is the
        intersection of the sphere and line, or ``None`` if there is no
        intersection.

        If *other* is a **Plane**, returns a **Point3** of intersection, or
        ``None``.

    ``connect(other)``
        Returns a **LineSegment3** which is the minimum length line segment
        that can connect the two shapes.  For two parallel lines, this
        line segment may be in an arbitrary position.  *other* may be
        a **Point3**, **Line3**, **Ray3**, **LineSegment3**, **Sphere** or
        **Plane**.

    ``distance(other)``
        Returns the absolute minimum distance to *other*.  Internally this
        simply returns the length of the result of ``connect``.

    **LineSegment3** also has a *length* property which is read-only.
    """

    def __init__(self, *args):
        if len(args) == 3:
            # assert isinstance(args[0], Point3) and isinstance(args[1], Vector3) and type(args[2]) == float
            self.p = Point3(args[0])
            self.v = args[1] * args[2] / abs(args[1])
        elif len(args) == 2:
            if isinstance(args[0], Point3) and isinstance(args[1], Point3):
                self.p = Point3(args[0])
                self.v = Vector3(args[1] - args[0])
            elif isinstance(args[0], Point3) and isinstance(args[1], Vector3):
                self.p = Point3(args[0])
                self.v = Vector3(args[1])
            else:
                raise AttributeError('%r' % (args,))
        elif len(args) == 1:  # copy constructor
            if isinstance(args[0], Line3):
                super(Line3, self).__init__(*args)
                self.p = Point3(args[0])
                self.v = Vector3(args[0])
            else:
                raise AttributeError('%r' % (args,))
        else:
            raise AttributeError('%r' % (args,))

        # XXX This is annoying.
        # if not self.v:
        #    raise AttributeError, 'Line has zero-length vector'

    def __repr__(self):
        return '%s(%s,%s)' % (self.__class__.__name__, self.p, self.v)

    p1 = property(lambda self: self.p)
    p2 = property(lambda self: Point3(self.p.x + self.v.x,
                                      self.p.y + self.v.y,
                                      self.p.z + self.v.z))

    def _apply_transform(self, t):
        self.p = t * self.p
        self.v = t * self.v

    def _u_in(self, u):
        return True

    def point(self, u):
        ":return: Point3 at parameter u"
        if self._u_in(u):
            return self.p + u * self.v
        else:
            return None

    def intersect(self, other):
        return other._intersect_line3(self)

    def _intersect_sphere(self, other):
        return _intersect_line3_sphere(self, other)

    def _intersect_plane(self, other):
        return _intersect_line3_plane(self, other)

    def connect(self, other):
        return other._connect_line3(self)

    def _connect_point3(self, other):
        return _connect_point3_line3(other, self)

    def _connect_line3(self, other):
        return _connect_line3_line3(other, self)

    def _connect_sphere(self, other):
        return _connect_sphere_line3(other, self)

    def _connect_plane(self, other):
        c = _connect_line3_plane(self, other)
        if c:
            return c


class Ray3(Line3):
    def _u_in(self, u):
        return u >= 0.0


class Segment3(Line3):
    def __repr__(self):
        return '%s(%s,%s)' % (self.__class__.__name__, self.p, self.p2)

    def _u_in(self, u):
        return u >= 0.0 and u <= 1.0

    def __abs__(self):
        return abs(self.v)

    def mag2(self):
        return self.v.mag2()

    def swap(self):
        # used by connect methods to switch order of points
        self.p = self.p2
        self.v *= -1
        return self

    length = property(lambda self: abs(self.v))


def Spherical(r, theta, phi):
    return Vector3(r * sin(theta) * cos(phi), r * sin(theta) * sin(phi), r * cos(phi))


class Sphere(Geometry):
    """Spheres are constructed with a center **Point3** and a radius::

        >>> s = Sphere(Point3(1.0, 1.0, 1.0), 0.5)
        >>> s
        Sphere(<1.00, 1.00, 1.00>, radius=0.50)

    Internally there are two attributes: *c*, giving the center point and
    *r*, giving the radius.

    The following methods are supported:

    ``intersect(other)``:
        If *other* is a **Point3**, returns ``True`` iff the point lies
        within the sphere.

        If *other* is a **Line3**, **Ray3** or **LineSegment3**, returns
        a **LineSegment3** giving the intersection, or ``None`` if the
        line does not intersect the sphere.


    ``distance(other)``
        Returns the absolute minimum distance to *other*.  Internally this
        simply returns the length of the result of ``connect``.
    """

    def __init__(self, *args):
        """
        :param args: can be

            * Sphere
            * center, point on sphere
            * center, radius
        """
        if len(args) == 1:  # Circle or derived class
            super(Sphere, self).__init__(*args)
            self.c = Point3(args[0].c)
            self.r = args[0].r
        else:  # 2 first params are used to stay compatible with Arc2
            self.c = Point3(args[0])
            if isinstance(args[1], (float, int)):
                self.r = args[1]
            else:
                p = Point3(args[1])  # one point on sphere
                self.r = abs(p - self.c)

    def __repr__(self):
        return '%s(%s,%g)' % (self.__class__.__name__, self.c, self.r)

    def __contains__(self, pt, precision=0):
        ":return: True if pt is ON or IN the sphere"
        return self.c.distance(pt) <= self.r + precision

    def point(self, u, v):
        """
        :param u: float angle from "north pole" (=radians(90-lat) in radians
        :param v: float angle from 0 meridian
        :return: Point3 on sphere at specified coordinates
        """
        return self.c + Spherical(self.r, u, v)

    def _apply_transform(self, t):
        self.c = t * self.c

    def intersect(self, other):
        return other._intersect_sphere(self)

    def _intersect_line3(self, other):
        return _intersect_line3_sphere(other, self)

    def connect(self, other):
        """
        minimal joining segment between Sphere and other 3D Object
        :param other: Point3, Line3, Sphere, Plane
        :return: LineSegment3 of minimal length
        """

        return other._connect_sphere(self)

    def _connect_point3(self, other):
        return _connect_point3_sphere(other, self)

    def _connect_line3(self, sphere):
        c = _connect_sphere_line3(self, sphere)
        if c:
            return c.swap()

    def _connect_sphere(self, other):
        return _connect_sphere_sphere(other, self)

    def _connect_plane(self, other):
        c = _connect_sphere_plane(self, other)
        if c:
            return c

    def distance_on_sphere(self, phi1, theta1, phi2, theta2):
        """
        :param phi1: float angle from "north pole" (=radians(90-lat) in radians
        :param theta1: float angle from 0 meridian
        :param phi2: float angle from "north pole" (=radians(90-lat) in radians
        :param theta2: float angle from 0 meridian
        """
        # http://www.johndcook.com/blog/python_longitude_latitude/

        c = (sin(phi1) * sin(phi2) * cos(theta1 - theta2) + cos(phi1) * cos(phi2))
        return self.r * acos(c)


class Plane(Geometry):
    """
    Planes can be constructed with any of:

    * three **Point3**'s lying on the plane
    * a **Point3** on the plane and the **Vector3** normal
    * a **Vector3** normal and *k*, described below.

    Internally, planes are stored with the normal *n* and constant *k* such
    that *n.p* = *k* for any point on the plane *p*.

    The following methods are supported:

    ``intersect(other)``
        If *other* is a **Line3**, **Ray3** or **LineSegment3**, returns a
        **Point3** of intersection, or ``None`` if there is no intersection.

        If *other* is a **Plane**, returns the **Line3** of intersection.

    ``connect(other)``
        Returns a **LineSegment3** which is the minimum length line segment
        that can connect the two shapes. *other* may be a **Point3**, **Line3**,
        **Ray3**, **LineSegment3**, **Sphere** or **Plane**.

    ``distance(other)``
        Returns the absolute minimum distance to *other*.  Internally this
        simply returns the length of the result of ``connect``.
    """

    # n.p = k, where n is normal, p is point on plane, k is constant scalar

    def __init__(self, *args):
        if len(args) == 3:
            self.n = (Point3(args[1]) - Point3(args[0])
                      ).cross(Point3(args[2]) - Point3(args[0]))
            self.n.normalize()
            self.k = self.n.dot(Point3(args[0]))
        elif len(args) == 2:
            if isinstance(args[0], Point3) and isinstance(args[1], Vector3):
                self.n = args[1].normalized()
                self.k = self.n.dot(args[0])
            elif isinstance(args[0], Vector3) and type(args[1]) == float:
                self.n = args[0].normalized()
                self.k = args[1]
            else:
                raise AttributeError('%r' % (args,))

        else:
            raise AttributeError('%r' % (args,))

        if not self.n:
            raise AttributeError('Points on plane are colinear')

    def __repr__(self):
        return 'Plane(<%.2f, %.2f, %.2f>.p = %.2f)' % \
               (self.n.x, self.n.y, self.n.z, self.k)

    def _get_point(self):
        # Return an arbitrary point on the plane
        if self.n.z:
            return Point3(0., 0., self.k / self.n.z)
        elif self.n.y:
            return Point3(0., self.k / self.n.y, 0.)
        else:
            return Point3(self.k / self.n.x, 0., 0.)

    def _apply_transform(self, t):
        p = t * self._get_point()
        self.n = t * self.n
        self.k = self.n.dot(p)

    def intersect(self, other):
        return other._intersect_plane(self)

    def _intersect_line3(self, other):
        return _intersect_line3_plane(other, self)

    def _intersect_plane(self, other):
        return _intersect_plane_plane(self, other)

    def connect(self, other):
        return other._connect_plane(self)

    def _connect_point3(self, other):
        return _connect_point3_plane(other, self)

    def _connect_line3(self, other):
        return _connect_line3_plane(other, self)

    def _connect_sphere(self, other):
        return _connect_sphere_plane(other, self)

    def _connect_plane(self, other):
        return _connect_plane_plane(other, self)

# a b c d
# e f g h
# i j k l
# m n o p


class Matrix4(object):

    def __init__(self, *args):
        self.identity()
        if not args:
            return
        if len(args) == 1:
            args = args[0][:]
        if len(args) == 16:
            self[:] = args
        else:
            raise RuntimeError('%s.__init__(%s) failed' %
                               (self.__class__.__name__, object))

    def __eq__(self, other):
        """Matrix equality test : return True if all elements are (almost) equal"""
        return math2.allclose(self, other)

    def __repr__(self):
        t = self.transposed()  # repr is by line while [:] is by column
        return ('%s%s') % (self.__class__.__name__, tuple(t))

    def __iter__(self):
        return iter((self.a, self.e, self.i, self.m,
                     self.b, self.f, self.j, self.n,
                     self.c, self.g, self.k, self.o,
                     self.d, self.h, self.l, self.p))

    def __getitem__(self, key):
        return [self.a, self.e, self.i, self.m,
                self.b, self.f, self.j, self.n,
                self.c, self.g, self.k, self.o,
                self.d, self.h, self.l, self.p][key]

    def __setitem__(self, key, value):
        L = self[:]
        L[key] = value
        (self.a, self.e, self.i, self.m,
         self.b, self.f, self.j, self.n,
         self.c, self.g, self.k, self.o,
         self.d, self.h, self.l, self.p) = L

    def __mul__(self, other):
        if isinstance(other, Matrix4):
            # Cache attributes in local vars (see Matrix3.__mul__).
            Aa = self.a
            Ab = self.b
            Ac = self.c
            Ad = self.d
            Ae = self.e
            Af = self.f
            Ag = self.g
            Ah = self.h
            Ai = self.i
            Aj = self.j
            Ak = self.k
            Al = self.l
            Am = self.m
            An = self.n
            Ao = self.o
            Ap = self.p
            Ba = other.a
            Bb = other.b
            Bc = other.c
            Bd = other.d
            Be = other.e
            Bf = other.f
            Bg = other.g
            Bh = other.h
            Bi = other.i
            Bj = other.j
            Bk = other.k
            Bl = other.l
            Bm = other.m
            Bn = other.n
            Bo = other.o
            Bp = other.p
            C = Matrix4()
            C.a = Aa * Ba + Ab * Be + Ac * Bi + Ad * Bm
            C.b = Aa * Bb + Ab * Bf + Ac * Bj + Ad * Bn
            C.c = Aa * Bc + Ab * Bg + Ac * Bk + Ad * Bo
            C.d = Aa * Bd + Ab * Bh + Ac * Bl + Ad * Bp
            C.e = Ae * Ba + Af * Be + Ag * Bi + Ah * Bm
            C.f = Ae * Bb + Af * Bf + Ag * Bj + Ah * Bn
            C.g = Ae * Bc + Af * Bg + Ag * Bk + Ah * Bo
            C.h = Ae * Bd + Af * Bh + Ag * Bl + Ah * Bp
            C.i = Ai * Ba + Aj * Be + Ak * Bi + Al * Bm
            C.j = Ai * Bb + Aj * Bf + Ak * Bj + Al * Bn
            C.k = Ai * Bc + Aj * Bg + Ak * Bk + Al * Bo
            C.l = Ai * Bd + Aj * Bh + Ak * Bl + Al * Bp
            C.m = Am * Ba + An * Be + Ao * Bi + Ap * Bm
            C.n = Am * Bb + An * Bf + Ao * Bj + Ap * Bn
            C.o = Am * Bc + An * Bg + Ao * Bk + Ap * Bo
            C.p = Am * Bd + An * Bh + Ao * Bl + Ap * Bp
            return C
        elif isinstance(other, Point3):
            A = self
            B = other
            P = Point3(0, 0, 0)
            P.x = A.a * B.x + A.b * B.y + A.c * B.z + A.d
            P.y = A.e * B.x + A.f * B.y + A.g * B.z + A.h
            P.z = A.i * B.x + A.j * B.y + A.k * B.z + A.l
            return P
        elif isinstance(other, Vector3):
            A = self
            B = other
            V = Vector3(0, 0, 0)
            V.x = A.a * B.x + A.b * B.y + A.c * B.z
            V.y = A.e * B.x + A.f * B.y + A.g * B.z
            V.z = A.i * B.x + A.j * B.y + A.k * B.z
            return V
        else:
            other = copy(other)
            other._apply_transform(self)
            return other

    def __call__(self, other):
        return self * other

    def __imul__(self, other):
        # assert isinstance(other, Matrix4)
        # Cache attributes in local vars (see Matrix3.__mul__).
        Aa = self.a
        Ab = self.b
        Ac = self.c
        Ad = self.d
        Ae = self.e
        Af = self.f
        Ag = self.g
        Ah = self.h
        Ai = self.i
        Aj = self.j
        Ak = self.k
        Al = self.l
        Am = self.m
        An = self.n
        Ao = self.o
        Ap = self.p
        Ba = other.a
        Bb = other.b
        Bc = other.c
        Bd = other.d
        Be = other.e
        Bf = other.f
        Bg = other.g
        Bh = other.h
        Bi = other.i
        Bj = other.j
        Bk = other.k
        Bl = other.l
        Bm = other.m
        Bn = other.n
        Bo = other.o
        Bp = other.p
        self.a = Aa * Ba + Ab * Be + Ac * Bi + Ad * Bm
        self.b = Aa * Bb + Ab * Bf + Ac * Bj + Ad * Bn
        self.c = Aa * Bc + Ab * Bg + Ac * Bk + Ad * Bo
        self.d = Aa * Bd + Ab * Bh + Ac * Bl + Ad * Bp
        self.e = Ae * Ba + Af * Be + Ag * Bi + Ah * Bm
        self.f = Ae * Bb + Af * Bf + Ag * Bj + Ah * Bn
        self.g = Ae * Bc + Af * Bg + Ag * Bk + Ah * Bo
        self.h = Ae * Bd + Af * Bh + Ag * Bl + Ah * Bp
        self.i = Ai * Ba + Aj * Be + Ak * Bi + Al * Bm
        self.j = Ai * Bb + Aj * Bf + Ak * Bj + Al * Bn
        self.k = Ai * Bc + Aj * Bg + Ak * Bk + Al * Bo
        self.l = Ai * Bd + Aj * Bh + Ak * Bl + Al * Bp
        self.m = Am * Ba + An * Be + Ao * Bi + Ap * Bm
        self.n = Am * Bb + An * Bf + Ao * Bj + Ap * Bn
        self.o = Am * Bc + An * Bg + Ao * Bk + Ap * Bo
        self.p = Am * Bd + An * Bh + Ao * Bl + Ap * Bp
        return self

    def transform(self, other):
        A = self
        B = other
        P = Point3(0, 0, 0)
        P.x = A.a * B.x + A.b * B.y + A.c * B.z + A.d
        P.y = A.e * B.x + A.f * B.y + A.g * B.z + A.h
        P.z = A.i * B.x + A.j * B.y + A.k * B.z + A.l
        w = A.m * B.x + A.n * B.y + A.o * B.z + A.p
        if w != 0:
            P.x /= w
            P.y /= w
            P.z /= w
        return P

    def identity(self):
        self.a = self.f = self.k = self.p = 1.
        self.b = self.c = self.d = self.e = self.g = self.h = \
            self.i = self.j = self.l = self.m = self.n = self.o = 0
        return self

    def scale(self, x, y, z):
        self *= Matrix4.new_scale(x, y, z)
        return self

    def translate(self, x, y, z):
        self *= Matrix4.new_translate(x, y, z)
        return self

    def rotatex(self, angle):
        self *= Matrix4.new_rotatex(angle)
        return self

    def rotatey(self, angle):
        self *= Matrix4.new_rotatey(angle)
        return self

    def rotatez(self, angle):
        self *= Matrix4.new_rotatez(angle)
        return self

    def rotate_axis(self, angle, axis):
        self *= Matrix4.new_rotate_axis(angle, axis)
        return self

    def rotate_euler(self, heading, attitude, bank):
        self *= Matrix4.new_rotate_euler(heading, attitude, bank)
        return self

    def rotate_triple_axis(self, x, y, z):
        self *= Matrix4.new_rotate_triple_axis(x, y, z)
        return self

    def transpose(self):
        (self.a, self.e, self.i, self.m,
         self.b, self.f, self.j, self.n,
         self.c, self.g, self.k, self.o,
         self.d, self.h, self.l, self.p) = \
            (self.a, self.b, self.c, self.d,
             self.e, self.f, self.g, self.h,
             self.i, self.j, self.k, self.l,
             self.m, self.n, self.o, self.p)

    def transposed(self):
        M = copy(self)
        M.transpose()
        return M

    # Static constructors
    @classmethod
    def new(cls, *values):
        M = cls()
        M[:] = values
        return M

    @classmethod
    def new_identity(cls):
        self = cls()
        return self

    @classmethod
    def new_scale(cls, x, y, z):
        self = cls()
        self.a = x
        self.f = y
        self.k = z
        return self

    @classmethod
    def new_translate(cls, x, y, z):
        self = cls()
        self.d = x
        self.h = y
        self.l = z
        return self

    @classmethod
    def new_rotatex(cls, angle):
        self = cls()
        s = sin(angle)
        c = cos(angle)
        self.f = self.k = c
        self.g = -s
        self.j = s
        return self

    @classmethod
    def new_rotatey(cls, angle):
        self = cls()
        s = sin(angle)
        c = cos(angle)
        self.a = self.k = c
        self.c = s
        self.i = -s
        return self

    @classmethod
    def new_rotatez(cls, angle):
        self = cls()
        s = sin(angle)
        c = cos(angle)
        self.a = self.f = c
        self.b = -s
        self.e = s
        return self

    @classmethod
    def new_rotate_axis(cls, angle, axis):
        # assert(isinstance(axis, Vector3))
        vector = axis.normalized()
        x = vector.x
        y = vector.y
        z = vector.z

        self = cls()
        s = sin(angle)
        c = cos(angle)
        c1 = 1. - c

        # from the glRotate man page
        self.a = x * x * c1 + c
        self.b = x * y * c1 - z * s
        self.c = x * z * c1 + y * s
        self.e = y * x * c1 + z * s
        self.f = y * y * c1 + c
        self.g = y * z * c1 - x * s
        self.i = x * z * c1 - y * s
        self.j = y * z * c1 + x * s
        self.k = z * z * c1 + c
        return self

    @classmethod
    def new_rotate_euler(cls, heading, attitude, bank):
        # from http://www.euclideanspace.com/
        ch = cos(heading)
        sh = sin(heading)
        ca = cos(attitude)
        sa = sin(attitude)
        cb = cos(bank)
        sb = sin(bank)

        self = cls()
        self.a = ch * ca
        self.b = sh * sb - ch * sa * cb
        self.c = ch * sa * sb + sh * cb
        self.e = sa
        self.f = ca * cb
        self.g = -ca * sb
        self.i = -sh * ca
        self.j = sh * sa * cb + ch * sb
        self.k = -sh * sa * sb + ch * cb
        return self

    @classmethod
    def new_rotate_triple_axis(cls, x, y, z):
        m = cls()

        m.a, m.b, m.c = x.x, y.x, z.x
        m.e, m.f, m.g = x.y, y.y, z.y
        m.i, m.j, m.k = x.z, y.z, z.z

        return m

    @classmethod
    def new_look_at(cls, eye, at, up):
        z = (eye - at).normalized()
        x = up.cross(z).normalized()
        y = z.cross(x)

        m = cls.new_rotate_triple_axis(x, y, z)
        m.d, m.h, m.l = eye.x, eye.y, eye.z
        return m

    @classmethod
    def new_perspective(cls, fov_y, aspect, near, far):
        # from the gluPerspective man page
        f = 1 / tan(fov_y / 2)
        self = cls()
        # assert near != 0.0 and near != far
        self.a = f / aspect
        self.f = f
        self.k = (far + near) / (near - far)
        self.l = 2 * far * near / (near - far)
        self.o = -1
        self.p = 0
        return self

    def determinant(self):
        return ((self.a * self.f - self.e * self.b)
                * (self.k * self.p - self.o * self.l)
                - (self.a * self.j - self.i * self.b)
                * (self.g * self.p - self.o * self.h)
                + (self.a * self.n - self.m * self.b)
                * (self.g * self.l - self.k * self.h)
                + (self.e * self.j - self.i * self.f)
                * (self.c * self.p - self.o * self.d)
                - (self.e * self.n - self.m * self.f)
                * (self.c * self.l - self.k * self.d)
                + (self.i * self.n - self.m * self.j)
                * (self.c * self.h - self.g * self.d))

    def inverse(self):
        tmp = Matrix4()
        d = self.determinant()

        if abs(d) < 0.001:
            # No inverse, return identity
            return tmp
        else:
            d = 1.0 / d

            tmp.a = d * (self.f * (self.k * self.p - self.o * self.l) + self.j * (
                self.o * self.h - self.g * self.p) + self.n * (self.g * self.l - self.k * self.h))
            tmp.e = d * (self.g * (self.i * self.p - self.m * self.l) + self.k * (
                self.m * self.h - self.e * self.p) + self.o * (self.e * self.l - self.i * self.h))
            tmp.i = d * (self.h * (self.i * self.n - self.m * self.j) + self.l * (
                self.m * self.f - self.e * self.n) + self.p * (self.e * self.j - self.i * self.f))
            tmp.m = d * (self.e * (self.n * self.k - self.j * self.o) + self.i * (
                self.f * self.o - self.n * self.g) + self.m * (self.j * self.g - self.f * self.k))

            tmp.b = d * (self.j * (self.c * self.p - self.o * self.d) + self.n * (
                self.k * self.d - self.c * self.l) + self.b * (self.o * self.l - self.k * self.p))
            tmp.f = d * (self.k * (self.a * self.p - self.m * self.d) + self.o * (
                self.i * self.d - self.a * self.l) + self.c * (self.m * self.l - self.i * self.p))
            tmp.j = d * (self.l * (self.a * self.n - self.m * self.b) + self.p * (
                self.i * self.b - self.a * self.j) + self.d * (self.m * self.j - self.i * self.n))
            tmp.n = d * (self.i * (self.n * self.c - self.b * self.o) + self.m * (
                self.b * self.k - self.j * self.c) + self.a * (self.j * self.o - self.n * self.k))

            tmp.c = d * (self.n * (self.c * self.h - self.g * self.d) + self.b * (
                self.g * self.p - self.o * self.h) + self.f * (self.o * self.d - self.c * self.p))
            tmp.g = d * (self.o * (self.a * self.h - self.e * self.d) + self.c * (
                self.e * self.p - self.m * self.h) + self.g * (self.m * self.d - self.a * self.p))
            tmp.k = d * (self.p * (self.a * self.f - self.e * self.b) + self.d * (
                self.e * self.n - self.m * self.f) + self.h * (self.m * self.b - self.a * self.n))
            tmp.o = d * (self.m * (self.f * self.c - self.b * self.g) + self.a * (
                self.n * self.g - self.f * self.o) + self.e * (self.b * self.o - self.n * self.c))

            tmp.d = d * (self.b * (self.k * self.h - self.g * self.l) + self.f * (
                self.c * self.l - self.k * self.d) + self.j * (self.g * self.d - self.c * self.h))
            tmp.h = d * (self.c * (self.i * self.h - self.e * self.l) + self.g * (
                self.a * self.l - self.i * self.d) + self.k * (self.e * self.d - self.a * self.h))
            tmp.l = d * (self.d * (self.i * self.f - self.e * self.j) + self.h * (
                self.a * self.j - self.i * self.b) + self.l * (self.e * self.b - self.a * self.f))
            tmp.p = d * (self.a * (self.f * self.k - self.j * self.g) + self.e * (
                self.j * self.c - self.b * self.k) + self.i * (self.b * self.g - self.f * self.c))

        return tmp


class Quaternion:
    """
    A quaternion represents a three-dimensional rotation or reflection
    transformation.  They are the preferred way to store and manipulate
    rotations in 3D applications, as they do not suffer the same numerical
    degradation that matrices do.

    The quaternion constructor initializes to the identity transform::

        >>> q = Quaternion()
        >>> q
        Quaternion(real=1.00, imag=<0.00, 0.00, 0.00>)

    **Element access**

    Internally, the quaternion is stored as four attributes: ``x``, ``y`` and
    ``z`` forming the imaginary vector, and ``w`` the real component.

    **Constructors**

    Rotations can be formed using the constructors:

    ``new_identity()``
        Equivalent to the default constructor.

    ``new_rotate_axis(angle, axis)``
        Equivalent to the Matrix4 constructor of the same name.  *angle* is
        specified in radians, *axis* is an instance of **Vector3**.  It is
        not necessary to normalize the axis.  Example::

            >>> q = Quaternion.new_rotate_axis(math.pi / 2, Vector3(1, 0, 0))
            >>> q
            Quaternion(real=0.71, imag=<0.71, 0.00, 0.00>)

    ``new_rotate_euler(heading, attitude, bank)``
        Equivalent to the Matrix4 constructor of the same name.  *heading*
        is a rotation around the Y axis, *attitude* around the X axis and
        *bank* around the Z axis.  All angles are given in radians.  Example::

            >>> q = Quaternion.new_rotate_euler(math.pi / 2, math.pi / 2, 0)
            >>> q
            Quaternion(real=0.50, imag=<0.50, 0.50, 0.50>)

    ``new_interpolate(q1, q2, t)``
        Create a quaternion which gives a (SLERP) interpolated rotation
        between *q1* and *q2*.  *q1* and *q2* are instances of **Quaternion**,
        and *t* is a value between 0.0 and 1.0.  For example::

            >>> q1 = Quaternion.new_rotate_axis(math.pi / 2, Vector3(1, 0, 0))
            >>> q2 = Quaternion.new_rotate_axis(math.pi / 2, Vector3(0, 1, 0))
            >>> for i in range(11):
            ...     print Quaternion.new_interpolate(q1, q2, i / 10.0)
            ...
            Quaternion(real=0.71, imag=<0.71, 0.00, 0.00>)
            Quaternion(real=0.75, imag=<0.66, 0.09, 0.00>)
            Quaternion(real=0.78, imag=<0.61, 0.17, 0.00>)
            Quaternion(real=0.80, imag=<0.55, 0.25, 0.00>)
            Quaternion(real=0.81, imag=<0.48, 0.33, 0.00>)
            Quaternion(real=0.82, imag=<0.41, 0.41, 0.00>)
            Quaternion(real=0.81, imag=<0.33, 0.48, 0.00>)
            Quaternion(real=0.80, imag=<0.25, 0.55, 0.00>)
            Quaternion(real=0.78, imag=<0.17, 0.61, 0.00>)
            Quaternion(real=0.75, imag=<0.09, 0.66, 0.00>)
            Quaternion(real=0.71, imag=<0.00, 0.71, 0.00>)


    **Operators**

    Quaternions may be multiplied to compound rotations.  For example, to
    rotate 90 degrees around the X axis and then 90 degrees around the Y axis::

        >>> q1 = Quaternion.new_rotate_axis(math.pi / 2, Vector3(1, 0, 0))
        >>> q2 = Quaternion.new_rotate_axis(math.pi / 2, Vector3(0, 1, 0))
        >>> q1 * q2
        Quaternion(real=0.50, imag=<0.50, 0.50, 0.50>)

    Multiplying a quaternion by a vector gives a vector, transformed
    appropriately::

        >>> q = Quaternion.new_rotate_axis(math.pi / 2, Vector3(0, 1, 0))
        >>> q * Vector3(1.0, 0, 0)
        Vector3(0.00, 0.00, -1.00)

    Similarly, any 3D object can be multiplied (e.g., **Point3**, **Line3**,
    **Sphere**, etc)::

        >>> q * Ray3(Point3(1., 1., 1.), Vector3(1., 1., 1.))
        Ray3(<1.00, 1.00, -1.00> + u<1.00, 1.00, -1.00>)

    As with the matrix classes, the constructors are also available as in-place
    operators.  These are named ``identity``, ``rotate_euler`` and
    ``rotate_axis``.  For example::

        >>> q1 = Quaternion()
        >>> q1.rotate_euler(math.pi / 2, math.pi / 2, 0)
        Quaternion(real=0.50, imag=<0.50, 0.50, 0.50>)
        >>> q1
        Quaternion(real=0.50, imag=<0.50, 0.50, 0.50>)

    Quaternions are usually unit length, but you may wish to use sized
    quaternions.  In this case, you can find the magnitude using ``abs``,
    ``magnitude`` and ``magnitude_squared``, as with the vector classes.
    Example::

        >>> q1 = Quaternion()
        >>> abs(q1)
        1.0
        >>> q1.magnitude()
        1.0

    Similarly, the class implements ``normalize`` and ``normalized`` in the
    same way as the vectors.

    The following methods do not alter the quaternion:

    ``conjugated()``
        Returns a quaternion that is the conjugate of the instance.  For
        example::

            >>> q1 = Quaternion.new_rotate_axis(math.pi / 2, Vector3(1, 0, 0))
            >>> q1.conjugated()
            Quaternion(real=0.71, imag=<-0.71, -0.00, -0.00>)
            >>> q1
            Quaternion(real=0.71, imag=<0.71, 0.00, 0.00>)

    ``get_angle_axis()``
        Returns a tuple (angle, axis), giving the angle to rotate around an
        axis equivalent to the quaternion.  For example::

            >>> q1 = Quaternion.new_rotate_axis(math.pi / 2, Vector3(1, 0, 0))
            >>> q1.get_angle_axis()
            (1.5707963267948966, Vector3(1.00, 0.00, 0.00))

    ``get_matrix()``
        Returns a **Matrix4** implementing the transformation of the quaternion.
        For example::

            >>> q1 = Quaternion.new_rotate_axis(math.pi / 2, Vector3(1, 0, 0))
            >>> q1.get_matrix()
            Matrix4([    1.00     0.00     0.00     0.00
                         0.00     0.00    -1.00     0.00
                         0.00     1.00     0.00     0.00
                         0.00     0.00     0.00     1.00])
    """

    # All methods and naming conventions based off
    # http://www.euclideanspace.com/maths/algebra/realNormedAlgebra/quaternions

    # w is the real part, (x, y, z) are the imaginary parts

    def __init__(self, w=1, x=0, y=0, z=0):
        # TODO: add a copy constructor one day
        super(Quaternion, self).__init__()
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return '%s(%g,%g,%g,%g)' % (self.__class__.__name__, self.w, self.x, self.y, self.z)

    def __mul__(self, other):
        if isinstance(other, Quaternion):
            Ax = self.x
            Ay = self.y
            Az = self.z
            Aw = self.w
            Bx = other.x
            By = other.y
            Bz = other.z
            Bw = other.w
            Q = Quaternion()
            Q.x = Ax * Bw + Ay * Bz - Az * By + Aw * Bx
            Q.y = -Ax * Bz + Ay * Bw + Az * Bx + Aw * By
            Q.z = Ax * By - Ay * Bx + Az * Bw + Aw * Bz
            Q.w = -Ax * Bx - Ay * By - Az * Bz + Aw * Bw
            return Q
        elif isinstance(other, Vector3):
            w = self.w
            x = self.x
            y = self.y
            z = self.z
            Vx = other.x
            Vy = other.y
            Vz = other.z
            ww = w * w
            w2 = w * 2
            wx2 = w2 * x
            wy2 = w2 * y
            wz2 = w2 * z
            xx = x * x
            x2 = x * 2
            xy2 = x2 * y
            xz2 = x2 * z
            yy = y * y
            yz2 = 2 * y * z
            zz = z * z
            return other.__class__(
                ww * Vx + wy2 * Vz - wz2 * Vy +
                xx * Vx + xy2 * Vy + xz2 * Vz -
                zz * Vx - yy * Vx,
                xy2 * Vx + yy * Vy + yz2 * Vz +
                wz2 * Vx - zz * Vy + ww * Vy -
                wx2 * Vz - xx * Vy,
                xz2 * Vx + yz2 * Vy +
                zz * Vz - wy2 * Vx - yy * Vz +
                wx2 * Vy - xx * Vz + ww * Vz)
        else:
            other = copy(other)
            other._apply_transform(self)
            return other

    def __imul__(self, other):
        # assert isinstance(other, Quaternion)
        Ax = self.x
        Ay = self.y
        Az = self.z
        Aw = self.w
        Bx = other.x
        By = other.y
        Bz = other.z
        Bw = other.w
        self.x = Ax * Bw + Ay * Bz - Az * By + Aw * Bx
        self.y = -Ax * Bz + Ay * Bw + Az * Bx + Aw * By
        self.z = Ax * By - Ay * Bx + Az * Bw + Aw * Bz
        self.w = -Ax * Bx - Ay * By - Az * Bz + Aw * Bw
        return self

    def mag2(self):
        return self.w ** 2 + self.x ** 2 + self.y ** 2 + self.z ** 2

    def __abs__(self):
        return sqrt(self.mag2())

    mag = __abs__

    def identity(self):
        self.w = 1
        self.x = 0
        self.y = 0
        self.z = 0
        return self

    def rotate_axis(self, angle, axis):
        self *= Quaternion.new_rotate_axis(angle, axis)
        return self

    def rotate_euler(self, heading, attitude, bank):
        self *= Quaternion.new_rotate_euler(heading, attitude, bank)
        return self

    def rotate_matrix(self, m):
        self *= Quaternion.new_rotate_matrix(m)
        return self

    def conjugated(self):
        Q = Quaternion()
        Q.w = self.w
        Q.x = -self.x
        Q.y = -self.y
        Q.z = -self.z
        return Q

    def normalize(self):
        d = self.mag()
        if d != 0:
            self.w /= d
            self.x /= d
            self.y /= d
            self.z /= d
        return self

    def normalized(self):
        res = copy(self)
        return res.normalize()

    def get_angle_axis(self):
        if self.w > 1:
            self = self.normalized()
        angle = 2 * acos(self.w)
        s = sqrt(1 - self.w ** 2)
        if s < 0.001:
            return angle, Vector3(1, 0, 0)
        else:
            return angle, Vector3(self.x / s, self.y / s, self.z / s)

    def get_euler(self):
        t = self.x * self.y + self.z * self.w
        if t > 0.4999:
            heading = 2 * atan2(self.x, self.w)
            attitude = pi / 2
            bank = 0
        elif t < -0.4999:
            heading = -2 * atan2(self.x, self.w)
            attitude = -pi / 2
            bank = 0
        else:
            sqx = self.x ** 2
            sqy = self.y ** 2
            sqz = self.z ** 2
            heading = atan2(2 * self.y * self.w - 2 * self.x * self.z,
                            1 - 2 * sqy - 2 * sqz)
            attitude = asin(2 * t)
            bank = atan2(2 * self.x * self.w - 2 * self.y * self.z,
                         1 - 2 * sqx - 2 * sqz)
        return heading, attitude, bank

    def get_matrix(self):
        xx = self.x ** 2
        xy = self.x * self.y
        xz = self.x * self.z
        xw = self.x * self.w
        yy = self.y ** 2
        yz = self.y * self.z
        yw = self.y * self.w
        zz = self.z ** 2
        zw = self.z * self.w
        M = Matrix4()
        M.a = 1 - 2 * (yy + zz)
        M.b = 2 * (xy - zw)
        M.c = 2 * (xz + yw)
        M.e = 2 * (xy + zw)
        M.f = 1 - 2 * (xx + zz)
        M.g = 2 * (yz - xw)
        M.i = 2 * (xz - yw)
        M.j = 2 * (yz + xw)
        M.k = 1 - 2 * (xx + yy)
        return M

    # Static constructors
    @classmethod
    def new_identity(cls):
        return cls()

    @classmethod
    def new_rotate_axis(cls, angle, axis):
        # assert(isinstance(axis, Vector3))
        axis = axis.normalized()
        s = sin(angle / 2)
        Q = cls()
        Q.w = cos(angle / 2)
        Q.x = axis.x * s
        Q.y = axis.y * s
        Q.z = axis.z * s
        return Q

    @classmethod
    def new_rotate_euler(cls, heading, attitude, bank):
        Q = cls()
        c1 = cos(heading / 2)
        s1 = sin(heading / 2)
        c2 = cos(attitude / 2)
        s2 = sin(attitude / 2)
        c3 = cos(bank / 2)
        s3 = sin(bank / 2)

        Q.w = c1 * c2 * c3 - s1 * s2 * s3
        Q.x = s1 * s2 * c3 + c1 * c2 * s3
        Q.y = s1 * c2 * c3 + c1 * s2 * s3
        Q.z = c1 * s2 * c3 - s1 * c2 * s3
        return Q

    @classmethod
    def new_rotate_matrix(cls, m):
        if m[0 * 4 + 0] + m[1 * 4 + 1] + m[2 * 4 + 2] > 0.00000001:
            t = m[0 * 4 + 0] + m[1 * 4 + 1] + m[2 * 4 + 2] + 1.0
            s = 0.5 / sqrt(t)

            return cls(
                s * t,
                (m[1 * 4 + 2] - m[2 * 4 + 1]) * s,
                (m[2 * 4 + 0] - m[0 * 4 + 2]) * s,
                (m[0 * 4 + 1] - m[1 * 4 + 0]) * s
            )

        elif m[0 * 4 + 0] > m[1 * 4 + 1] and m[0 * 4 + 0] > m[2 * 4 + 2]:
            t = m[0 * 4 + 0] - m[1 * 4 + 1] - m[2 * 4 + 2] + 1.0
            s = 0.5 / sqrt(t)

            return cls(
                (m[1 * 4 + 2] - m[2 * 4 + 1]) * s,
                s * t,
                (m[0 * 4 + 1] + m[1 * 4 + 0]) * s,
                (m[2 * 4 + 0] + m[0 * 4 + 2]) * s
            )

        elif m[1 * 4 + 1] > m[2 * 4 + 2]:
            t = -m[0 * 4 + 0] + m[1 * 4 + 1] - m[2 * 4 + 2] + 1.0
            s = 0.5 / sqrt(t)

            return cls(
                (m[2 * 4 + 0] - m[0 * 4 + 2]) * s,
                (m[0 * 4 + 1] + m[1 * 4 + 0]) * s,
                s * t,
                (m[1 * 4 + 2] + m[2 * 4 + 1]) * s
            )

        else:
            t = -m[0 * 4 + 0] - m[1 * 4 + 1] + m[2 * 4 + 2] + 1.0
            s = 0.5 / sqrt(t)

            return cls(
                (m[0 * 4 + 1] - m[1 * 4 + 0]) * s,
                (m[2 * 4 + 0] + m[0 * 4 + 2]) * s,
                (m[1 * 4 + 2] + m[2 * 4 + 1]) * s,
                s * t
            )

    @classmethod
    def new_interpolate(cls, q1, q2, t):
        # assert isinstance(q1, Quaternion) and isinstance(q2, Quaternion)
        Q = cls()

        costheta = q1.w * q2.w + q1.x * q2.x + q1.y * q2.y + q1.z * q2.z
        if costheta < 0.:
            costheta = -costheta
            q1 = q1.conjugated()
        elif costheta > 1:
            costheta = 1

        theta = acos(costheta)
        if abs(theta) < 0.01:
            Q.w = q2.w
            Q.x = q2.x
            Q.y = q2.y
            Q.z = q2.z
            return Q

        sintheta = sqrt(1.0 - costheta * costheta)
        if abs(sintheta) < 0.01:
            Q.w = (q1.w + q2.w) * 0.5
            Q.x = (q1.x + q2.x) * 0.5
            Q.y = (q1.y + q2.y) * 0.5
            Q.z = (q1.z + q2.z) * 0.5
            return Q

        ratio1 = sin((1 - t) * theta) / sintheta
        ratio2 = sin(t * theta) / sintheta

        Q.w = q1.w * ratio1 + q2.w * ratio2
        Q.x = q1.x * ratio1 + q2.x * ratio2
        Q.y = q1.y * ratio1 + q2.y * ratio2
        Q.z = q1.z * ratio1 + q2.z * ratio2
        return Q
