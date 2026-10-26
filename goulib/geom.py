"""
2D geometry
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
import abc
import copy as copier

from math import pi, sin, cos, atan2, sqrt, hypot, copysign
from goulib import math2, itertools2

rel_tol = 1e-6  # relative tolerance used in isclose comparisons


def _hash(v):
    """hash function for vectors"""
    # http://stackoverflow.com/questions/5928725/hashing-2d-3d-and-nd-vectors
    primes = [73856093, 19349663, 83492791]
    res = 0
    for x, p in zip(v, primes):
        res = res ^ int(x*p)  # ^ is xor
    return res


copy = copier.deepcopy

# Geometry
# Much maths thanks to Paul Bourke, http://astronomy.swin.edu.au/~pbourke
# --------------------------------------------------------------------------


class Geometry(object, metaclass=abc.ABCMeta):
    """
    The following classes are available for dealing with simple 2D geometry.
    The interface to each shape is similar; in particular, the ``connect``
    and ``distance`` methods are defined identically for each.

    For example, to find the closest point on a line to a circle::

        >>> circ = Circle(Point2(3., 2.), 2.)
        >>> line = Line2(Point2(0., 0.), Point2(-1., 1.))
        >>> line.connect(circ).p1
        Point2(0.50, -0.50)

    To find the corresponding closest point on the circle to the line::

        >>> line.connect(circ).p2
        Point2(1.59, 0.59)
    """

    def __init__(self, *args):
        """
        this constructor is called by descendant classes at copy
        it is replaced to copy some graphics attributes in module drawings
        """
        return

    def _connect_unimplemented(self, other):
        raise AttributeError('Cannot connect %s to %s' %
                             (self.__class__, other.__class__))

    def _intersect_unimplemented(self, other):
        raise AttributeError('Cannot intersect %s and %s' %
                             (self.__class__, other.__class__))

    _intersect_line2 = _intersect_unimplemented
    _intersect_circle = _intersect_unimplemented
    _connect_point2 = _connect_unimplemented
    _connect_line2 = _connect_unimplemented
    _connect_circle = _connect_unimplemented

    _intersect_line3 = _intersect_unimplemented
    _intersect_sphere = _intersect_unimplemented
    _intersect_plane = _intersect_unimplemented
    _connect_point3 = _connect_unimplemented
    _connect_line3 = _connect_unimplemented
    _connect_sphere = _connect_unimplemented
    _connect_plane = _connect_unimplemented

    def point(self, u):
        ":return: Point2 or Point3 at parameter u"
        raise NotImplementedError

    def tangent(self, u):
        ":return: Vector2 or Vector3 tangent at parameter u"
        raise NotImplementedError

    def intersect(self, other):
        raise NotImplementedError

    def connect(self, other):
        ":return: Geometry shortest (Segment2 or Segment3) that connects self to other"
        raise NotImplementedError

    def distance(self, other):
        c = self.connect(other)
        if c:
            return c.length
        else:
            return None

    def _u(self, pt):
        """:return: float parameter corresponding to pt"""
        raise NotImplementedError

    def _u_in(self, u):
        """:return: bool true if u is a valid parameter of geometry"""
        raise NotImplementedError

    def __contains__(self, pt):
        return math2.isclose(self.distance(pt), 0, rel_tol=rel_tol)


def argPair(x, y=None):
    """Process a pair of values passed in various ways."""
    if y is None:
        try:
            return x[0], x[1]
        except:
            pass

        try:
            return x.xy
        except:
            pass

        try:  # accepts complex
            return x.real, x.imag
        except:
            pass
    else:
        return x, y


class Vector2(object):
    """
    Mutable 2D vector:


    Construct a vector in the obvious way::

        >>> Vector2(1.5, 2.0)
        Vector2(1.50, 2.00)

        >>> Vector3(1.0, 2.0, 3.0)
        Vector3(1.00, 2.00, 3.00)

    **Element access**

    Components may be accessed as attributes (examples that follow use
    *Vector3*, but all results are similar for *Vector2*, using only the *x*
    and *y* components)::

        >>> v = Vector3(1, 2, 3)
        >>> v.x
        1
        >>> v.y
        2
        >>> v.z
        3

    Vectors support the list interface via slicing::

        >>> v = Vector3(1, 2, 3)
        >>> len(v)
        3
        >>> v[0]
        1
        >>> v[:]
        (1, 2, 3)

    You can also "swizzle" the components (*a la* GLSL or Cg)::

        >>> v = Vector3(1, 2, 3)
        >>> v.xyz
        (1, 2, 3)
        >>> v.zx
        (3, 1)
        >>> v.zzzz
        (3, 3, 3, 3)

    **Operators**

    Addition and subtraction are supported via operator overloading (note
    that in-place operators perform faster than those that create a new object)::

        >>> v1 = Vector3(1, 2, 3)
        >>> v2 = Vector3(4, 5, 6)
        >>> v1 + v2
        Vector3(5.00, 7.00, 9.00)
        >>> v1 -= v2
        >>> v1
        Vector3(-3.00, -3.00, -3.00)

    Multiplication and division can be performed with a scalar only::

        >>> Vector3(1, 2, 3) * 2
        Vector3(2.00, 4.00, 6.00)
        >>> v1 = Vector3(1., 2., 3.)
        >>> v1 /= 2
        >>> v1
        Vector3(0.50, 1.00, 1.50)

    The magnitude of a vector can be found with ``abs``::

        >>> v = Vector3(1., 2., 3.)
        >>> abs(v)
        3.7416573867739413

    A vector can be normalized in-place (note that the in-place method also
    returns ``self``, so you can chain it with further operators)::

        >>> v = Vector3(1., 2., 3.)
        >>> v.normalize()
        Vector3(0.27, 0.53, 0.80)
        >>> v
        Vector3(0.27, 0.53, 0.80)

    The following methods do *not* alter the original vector or their arguments:

    ``magnitude()``
        Returns the magnitude of the vector; equivalent to ``abs(v)``.  Example::

            >>> v = Vector3(1., 2., 3.)
            >>> v.magnitude()
            3.7416573867739413

    ``magnitude_squared()``
        Returns the sum of the squares of each component.  Useful for comparing
        the length of two vectors without the expensive square root operation.
        Example::

            >>> v = Vector3(1., 2., 3.)
            >>> v.magnitude_squared()
            14.0

    ``normalized()``
        Return a unit length vector in the same direction.  Note that this
        method differs from ``normalize`` in that it does not modify the
        vector in-place.  Example::

            >>> v = Vector3(1., 2., 3.)
            >>> v.normalized()
            Vector3(0.27, 0.53, 0.80)
            >>> v
            Vector3(1.00, 2.00, 3.00)

    ``dot(other)``
        Return the scalar "dot" product of two vectors.  Example::

            >>> v1 = Vector3(1., 2., 3.)
            >>> v2 = Vector3(4., 5., 6.)
            >>> v1.dot(v2)
            32.0

    ``cross()`` and ``cross(other)``
        Return the cross product of a vector (for **Vector2**), or the cross
        product of two vectors (for **Vector3**).  The return type is a
        vector.  Example::

            >>> v1 = Vector3(1., 2., 3.)
            >>> v2 = Vector3(4., 5., 6.)
            >>> v1.cross(v2)
            Vector3(-3.00, 6.00, -3.00)

        In two dimensions there can be no argument to ``cross``::

            >>> v1 = Vector2(1., 2.)
            >>> v1.cross()
            Vector2(2.00, -1.00)

    ``reflect(normal)``
        Return the vector reflected about the given normal.  In two dimensions,
        *normal* is the normal to a line, in three dimensions it is the normal
        to a plane.  The normal must have unit length.  Example::

            >>> v = Vector3(1., 2., 3.)
            >>> v.reflect(Vector3(0, 1, 0))
            Vector3(1.00, -2.00, 3.00)
            >>> v = Vector2(1., 2.)
            >>> v.reflect(Vector2(1, 0))
            Vector2(-1.00, 2.00)

    ``rotate_around(axes, theta)``
        For 3D vectors, return the vector rotated around axis by the angle theta.

            >>> v = Vector3(1., 2., 3.)
            >>> axes = Vector3(1.,1.,0)
            >>> v.rotate_around(axes,math.pi/4)
            Vector3(2.65, 0.35, 2.62)

    """

    def __init__(self, *args):
        """Constructor.
        :param args: x,y values
        """
        self.x, self.y = argPair(
            *args)  # pylint: disable=novalue-for-parameter

    @property
    def xy(self):
        """:return: tuple (x,y)"""
        return (self.x, self.y)

    def __repr__(self):
        return '%s%s' % (self.__class__.__name__, self.xy)

    def __hash__(self):
        return _hash(self.xy)

    def __eq__(self, other):
        """
        Tests for equality include comparing against other sequences:

        >>> v2 = Vector2(1, 2)
        >>> v2 == Vector2(3, 4)
        False
        >>> v2 != Vector2(1, 2)
        False
        >>> v2 == (1, 2)
        True

        >>> v3 = Vector3(1, 2, 3)
        >>> v3 == Vector3(3, 4, 5)
        False
        >>> v3 != Vector3(1, 2, 3)
        False
        >>> v3 == (1, 2, 3)
        True
        """
        try:  # quick
            if self.xy == other.xy:
                return True
        except:
            pass
        try:
            if self.x == other[0] and self.y == other[1]:
                return True
        except:
            pass
        return math2.isclose((self-Vector2(other)).mag(), 0, abs_tol=rel_tol)

    def __len__(self):
        return 2

    def __iter__(self):
        return iter(self.xy)

    def __add__(self, other):
        x, y = argPair(other)
        # Vector - Vector -> Vector
        # Vector - Point -> Point
        # Point - Point -> Vector
        if self.__class__ is other.__class__:
            _class = Vector2
        else:
            _class = Point2

        return _class(self.x + x, self.y + y)

    __radd__ = __add__

    def __iadd__(self, other):
        x, y = argPair(other)
        self.x += x
        self.y += y
        return self

    def __sub__(self, other):
        x, y = argPair(other)
        # Vector - Vector -> Vector
        # Vector - Point -> Point
        # Point - Point -> Vector
        if self.__class__ is other.__class__:
            _class = Vector2
        else:
            _class = Point2
        return _class(self.x - x, self.y - y)

    def __rsub__(self, other):
        """ Point2 - Vector 2 substraction
        :param other: Point2 or (x,y) tuple
        :return: Vector2
        """
        x, y = argPair(other)
        return Vector2(x - self.x, y - self.y)

    def __mul__(self, other):
        # assert type(other) in (int, int, float)
        return Vector2(self.x * other, self.y * other)

    __rmul__ = __mul__

    def __imul__(self, other):
        # assert type(other) in (int, int, float)
        self.x *= other
        self.y *= other
        return self

    # geometry requires truediv even in Python 2...

    def __div__(self, other):
        # assert type(other) in (int, int, float)
        return Vector2(operator.truediv(self.x, other),
                       operator.truediv(self.y, other))

    def __rdiv__(self, other):
        # assert type(other) in (int, int, float)
        return Vector2(operator.truediv(other, self.x),
                       operator.truediv(other, self.y))

    def __floordiv__(self, other):
        # assert type(other) in (int, int, float)
        return Vector2(operator.floordiv(self.x, other),
                       operator.floordiv(self.y, other))

    def __rfloordiv__(self, other):
        # assert type(other) in (int, int, float)
        return Vector2(operator.floordiv(other, self.x),
                       operator.floordiv(other, self.y))

    def __truediv__(self, other):
        # assert type(other) in (int, int, float)
        return Vector2(operator.truediv(self.x, other),
                       operator.truediv(self.y, other))

    def __rtruediv__(self, other):
        # assert type(other) in (int, int, float)
        return Vector2(operator.truediv(other, self.x),
                       operator.truediv(other, self.y))

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __pos__(self):
        return copy(self)

    def __abs__(self):
        return hypot(self.x, self.y)

    mag = __abs__

    length = property(lambda self: abs(self))

    def mag2(self):
        return self.x*self.x + self.y*self.y

    def normalize(self):
        d = self.mag()
        if d != 0:
            self.x /= d
            self.y /= d
        return self

    def normalized(self):
        res = copy(self)
        return res.normalize()

    def dot(self, other):
        x, y = argPair(other)
        return self.x * x + self.y * y

    def cross(self):
        return Vector2(self.y, -self.x)

    def reflect(self, normal):
        # assume normal is normalized
        # assert isinstance(normal, Vector2)
        d = 2 * (self.x * normal.x + self.y * normal.y)
        return Vector2(self.x - d * normal.x,
                       self.y - d * normal.y)

    def angle(self, other=None, unit=False):
        """angle between two vectors.
        :param unit: bool True if vectors are unit vectors. False increases computations
        :return: float angle in radians to the other vector, or self direction if other=None
        """
        if other is None:
            return atan2(self.y, self.x)
        else:
            return math2.angle(self, other, unit=unit)

    def project(self, other):
        """Return the projection (the component) of the vector on other."""
        n = other.normalized()
        return self.dot(n)*n

    def _apply_transform(self, mat3):
        x = mat3.a * self.x + mat3.b * self.y
        y = mat3.e * self.x + mat3.f * self.y
        self.x, self.y = x, y
        return self


def _intersect_line2_line2(A, B):
    d = B.v.y * A.v.x - B.v.x * A.v.y
    if d == 0:  # both lines are parallel
        if A.distance(B.p) == 0:  # colinear
            return A if isinstance(A, Segment2) else B
        else:
            return None

    dy = A.p.y - B.p.y
    dx = A.p.x - B.p.x
    ua = (B.v.x * dy - B.v.y * dx) / d
    if not A._u_in(ua):
        return None
    ub = (A.v.x * dy - A.v.y * dx) / d
    if not B._u_in(ub):
        return None

    return Point2(A.p.x + ua * A.v.x,
                  A.p.y + ua * A.v.y)


def _intersect_line2_circle(L, C):
    """Line2/Circle intersection
    :param L: Line2 (or derived class)
    :param C: Circle (or derived class)
    :return: None, single Point2 or [Point2,Point2]
    """
    a = L.v.mag2()
    b = 2 * (L.v.x * (L.p.x - C.c.x) + L.v.y * (L.p.y - C.c.y))
    c = C.c.mag2() + L.p.mag2() - 2 * C.c.dot(L.p) - C.r ** 2
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
    return [p1, p2]


def _intersect_circle_circle(c1, c2):
    """Circle/Circle intersection
    :param c1: Line2 (or derived class)
    :param c2: Circle (or derived class)
    :return: None, single Point2, [Point2,Point2] or smallest Circle if inscribed
    """
    # http://stackoverflow.com/questions/3349125/circle-circle-intersection-points

    v = c2.c-c1.c  # vector between centers

    d = v.mag()
    if d > (c1.r+c2.r):  # disjoint
        return None

    if d <= abs(c1.r-c2.r):  # one circle is inside the other.
        return c1 if c1.r <= c2.r else c2

    # http://mathworld.wolfram.com/Circle-CircleIntersection.html
    x = (d*d + c1.r*c1.r - c2.r*c2.r)/(2*d)
    y = sqrt(c1.r*c1.r - x*x)

    v.normalize()
    p = c1.c+x*v
    if math2.isclose(y, 0):
        return p

    v = v.cross()
    return [p+y*v, p-y*v]


def _connect_point2_line2(P, L):
    # http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
    d = L.v.mag2()
    if d == 0:  # L is degenerate to a point
        return Segment2(P, L.p)
    u = (L.v.dot(P-L.p))/d
    if not L._u_in(u):
        u = math2.sat(u, 0, 1)
    return Segment2(P, L.point(u))


def _connect_point2_circle(P, C):
    v = P - C.c
    v.normalize()
    v *= C.r
    return Segment2(P, Point2(C.c.x + v.x, C.c.y + v.y))


def _connect_line2_line2(A, B):
    d = B.v.y * A.v.x - B.v.x * A.v.y
    if d == 0:
        # Parallel, connect an endpoint with a line
        if isinstance(B, (Ray2, Segment2)):
            return _connect_point2_line2(B.p, A)
        # No endpoint (or endpoint is on A), possibly choose arbitrary point
        # on line.
        return _connect_point2_line2(A.p, B)

    dy = A.p.y - B.p.y
    dx = A.p.x - B.p.x
    ua = (B.v.x * dy - B.v.y * dx) / d
    if not A._u_in(ua):
        ua = max(min(ua, 1.0), 0.0)
    ub = (A.v.x * dy - A.v.y * dx) / d
    if not B._u_in(ub):
        ub = max(min(ub, 1.0), 0.0)

    return Segment2(Point2(A.p + ua * A.v), Point2(B.p + ub * B.v))


def _connect_circle_line2(C, L):
    d = L.v.mag2()
    # assert d != 0
    u = ((C.c.x - L.p.x) * L.v.x + (C.c.y - L.p.y) * L.v.y) / d
    if not L._u_in(u):
        u = max(min(u, 1.0), 0.0)
    point = Point2(L.p.x + u * L.v.x, L.p.y + u * L.v.y)
    v = (point - C.c)
    v.normalize()
    v *= C.r
    return Segment2(Point2(C.c.x + v.x, C.c.y + v.y), point)


def _connect_circle_circle(A, B):
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
    return Segment2(Point2(A.c + s1 * v * A.r), Point2(B.c + s2 * v * B.r))


class Point2(Vector2, Geometry):
    """A point on a 2D plane. Construct in the obvious way::

        >>> p = Point2(1.0, 2.0)
        >>> p
        Point2(1.00, 2.00)

    **Point2** subclasses **Vector2**, so all of **Vector2** operators and
    methods apply. In particular, subtracting two points gives a vector::

        >>> Point2(2.0, 3.0) - Point2(1.0, 0.0)
        Vector2(1.00, 3.00)

    ``connect(other)``
        Returns a **Segment2** which is the minimum length line segment
        that can connect the two shapes. *other* may be a **Point2**, **Line2**,
        **Ray2**, **Segment2** or **Circle**.
    """

    def dist(self, other):
        """
        absolute minimum distance to other object
        :param other: Point2, Line2 or Circle
        :return: float positive distance between self and other
        """
        try:  # quick for other Point2
            dx, dy = self.x-other.x, self.y-other.y
        except AttributeError:
            try:  # also quick for
                dx, dy = self.x-other[0], self.y-other[1]
            except IndexError:  # for all other objects
                return self.connect(other).length
        return hypot(dx, dy)

    def __abs__(self):
        """
        point has length=0 for coherency when calculating the length of large complex shapes having points
        """
        return 0

    def __contains__(self, pt):
        """
        :return: True if self and pt are the same point, False otherwise

        needed for coherency
        """
        if not isinstance(pt, Point2):
            return False
        return math2.isclose(self.distance(pt), 0, rel_tol=rel_tol)

    def intersect(self, other):
        """Point2/object intersection
        :return: Point2 copy of self if on other object, None if not
        """
        return Point2(self) if self in other else None

    def _intersect_circle(self, circle):
        return self.intersect(circle)

    def connect(self, other):
        return other._connect_point2(self)

    def _connect_point2(self, other):
        return Segment2(other, self)

    def _connect_line2(self, other):
        c = _connect_point2_line2(self, other)
        if c:
            return c.swap()

    def _connect_circle(self, other):
        c = _connect_point2_circle(self, other)
        if c:
            return c.swap()

    def _apply_transform(self, mat3):
        x = mat3.a * self.x + mat3.b * self.y + mat3.c
        y = mat3.e * self.x + mat3.f * self.y + mat3.g
        self.x, self.y = x, y
        return self


def Polar(mag, angle):
    return Vector2(mag*cos(angle), mag*sin(angle))


class Line2(Geometry):
    """
    A **Line2** is a line on a 2D plane extending to infinity in both directions;
    a **Ray2** has a finite end-point and extends to infinity in a single
    direction; a **Segment2** joins two points.

    All three classes support the same constructors, operators and methods,
    but may behave differently when calculating intersections etc.

    You may construct a line, ray or line segment using any of:

    * another line, ray or line segment
    * two points
    * a point and a vector
    * a point, a vector and a length

    For example::

        >>> Line2(Point2(1.0, 1.0), Point2(2.0, 3.0))
        Line2(<1.00, 1.00> + u<1.00, 2.00>)
        >>> Line2(Point2(1.0, 1.0), Vector2(1.0, 2.0))
        Line2(<1.00, 1.00> + u<1.00, 2.00>)
        >>> Ray2(Point2(1.0, 1.0), Vector2(1.0, 2.0), 1.0)
        Ray2(<1.00, 1.00> + u<0.45, 0.89>)

    Internally, lines, rays and line segments store a Point2 *p* and a
    Vector2 *v*.  You can also access (but not set) the two endpoints
    *p1* and *p2*.  These may or may not be meaningful for all types of lines.

    The following methods are supported by all three classes:

    ``intersect(other)``
        If *other* is a **Line2**, **Ray2** or **Segment2**, returns
        a **Point2** of intersection, or None if the lines are parallel.

        If *other* is a **Circle**, returns a **Segment2** or **Point2** giving
        the part of the line that intersects the circle, or None if there
        is no intersection.

    ``connect(other)``
        Returns a **Segment2** which is the minimum length line segment
        that can connect the two shapes.  For two parallel lines, this
        line segment may be in an arbitrary position.  *other* may be
        a **Point2**, **Line2**, **Ray2**, **Segment2** or **Circle**.

    ``distance(other)``
        Returns the absolute minimum distance to *other*.  Internally this
        simply returns the length of the result of ``connect``.

    **Segment2** also has a *length* property which is read-only.
    """

    def __init__(self, *args):
        super(Line2, self).__init__(*args)
        if len(args) == 1:  # Line2 or derived class
            self.p = Point2(args[0].p)
            self.v = Vector2(args[0].v)
        else:
            self.p = Point2(args[0])
            if type(args[1]) is Vector2:
                self.v = Vector2(args[1])
            else:
                self.v = Point2(args[1]) - self.p

            if len(args) == 3:
                self.v = self.v*args[2]/abs(self.v)

    def __eq__(self, other):
        """lines are "equal" only if base points and vector are strictly equal.
        to compare if lines are "same", use line1.distance(line2)==0
        """
        try:
            return self.p == other.p and self.v == other.v
        except:
            return False

    def __repr__(self):
        return '%s(%s,%s)' % (self.__class__.__name__, self.p, self.v)

    def _u_in(self, u):
        return True

    def point(self, u):
        ":return: Point2 at parameter u"
        if self._u_in(u):
            return self.p+u*self.v
        else:
            return None

    def tangent(self, u):
        ":return: Vector2 tangent at parameter u. Warning : tangent is generally not a unit vector"
        if self._u_in(u):
            return self.v
        else:
            return None

    def _apply_transform(self, t):
        self.p = t * self.p
        self.v = t * self.v

    def intersect(self, other):
        return other._intersect_line2(self)

    def _intersect_line2(self, line):
        return _intersect_line2_line2(self, line)

    def _intersect_circle(self, circle):
        """Line2/Circle intersection
        :return: None, Point2 or [Point2,Point2]
        """
        return _intersect_line2_circle(self, circle)

    def connect(self, other):
        return other._connect_line2(self)

    def _connect_point2(self, other):
        return _connect_point2_line2(other, self)

    def _connect_line2(self, other):
        return _connect_line2_line2(other, self)

    def _connect_circle(self, other):
        return _connect_circle_line2(other, self)


class Ray2(Line2):

    def _u_in(self, u):
        return u >= 0.0


class Segment2(Line2):
    p1 = property(lambda self: self.p)
    p2 = property(lambda self: Point2(
        self.p.x + self.v.x, self.p.y + self.v.y))

    def __repr__(self):
        return '%s(%s,%s)' % (self.__class__.__name__, self.p, self.p2)

    def _u_in(self, u):
        return u >= 0.0 and u <= 1.0

    def __abs__(self):
        return abs(self.v)

    def mag2(self):
        return self.v.mag2()

    length = property(lambda self: abs(self.v))

    def swap(self):
        # used by connect methods to switch order of points
        self.p = self.p2
        self.v *= -1
        return self

    def midpoint(self):
        return self.point(0.5)

    def bisect(self):
        res = Line2(self.midpoint(), self.v.cross())
        res.v.normalize()  # because usually we do geometry with it
        return res


class Surface(Geometry):

    @property
    def length(self):
        return abs(self)

    @property
    def area(self):
        raise NotImplementedError('virtual')

    @property
    def center(self):
        raise NotImplementedError('virtual')


class Polygon(Surface):
    def __init__(self, args):
        """
        :param args: can be

            * Polygon
            * iterator of points
        """
        super(Polygon, self).__init__()
        self.p = [Point2(x) for x in args]
        if self.p[0] == self.p[-1]:
            self.p = self.p[:-1]
        self.p = tuple(self.p)  # immutable

    def __repr__(self):
        return '%s%s' % (self.__class__.__name__, self.p)

    @property
    def xy(self):
        """:return: tuple (x,y)"""
        return (p.xy for p in self.p)

    def __iter__(self):
        return itertools2.pairwise(self.p, Segment2, True)

    def __abs__(self):
        """:return: float perimeter"""
        return sum(x.length for x in self)

    @property
    def area(self):
        # https://en.wikipedia.org/wiki/Shoelace_formula
        res = 0
        for p1, p2 in itertools2.pairwise(self.p, loop=True):
            res += p1.x * p2.y - p2.x * p1.y
        return res/2

    @property
    def center(self):
        """centroid

        :return: Point2 centroid of the Polygon
        """
        cx, cy = 0, 0
        for p1, p2 in itertools2.pairwise(self.p, loop=True):
            cx += (p1.x+p2.x)*(p1.x*p2.y-p2.x*p1.y)
            cy += (p1.y+p2.y)*(p1.x*p2.y-p2.x*p1.y)
        ar = self.area
        return Point2((1.0/(6.0*ar))*cx, (1.0/(6.0*ar))*cy)

    def __contains__(self, pt):
        # http://www.ariel.com.au/a/python-point-int-poly.html
        n = len(self.p)
        inside = False

        p1x, p1y = self.p[0]
        for i in range(n+1):
            p2x, p2y = self.p[i % n]
            if pt.y > min(p1y, p2y):
                if pt.y <= max(p1y, p2y):
                    if pt.x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (pt.y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or pt.x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def intersect(self, other):
        try:
            return other._intersect_polygon(self)
        except AttributeError:
            pass
        # do not recurse in Point2, Segment2 ...
        l = itertools2.flatten((other.intersect(s) for s in self), Geometry)
        res = []
        s = None
        for e in l:
            if e is None:
                continue
            if isinstance(e, Segment2):
                res.append(e)
                s = e
            else:  # Point2
                if (s is None) or (s.distance(e) > 1e-9):
                    res.append(e)

        return res


class Circle(Surface):
    """Circles are constructed with a center **Point2** and a radius::

        >>> c = Circle(Point2(1.0, 1.0), 0.5)
        >>> c
        Circle(<1.00, 1.00>, radius=0.50)

    Internally there are two attributes: *c*, giving the center point and
    *r*, giving the radius.

    The following methods are supported:



    ``connect(other)``
        Returns a **Segment2** which is the minimum length line segment
        that can connect the two shapes. *other* may be a **Point2**, **Line2**,
        **Ray2**, **Segment2** or **Circle**.

    ``distance(other)``
        Returns the absolute minimum distance to *other*.  Internally this
        simply returns the length of the result of ``connect``.
    """

    def __init__(self, *args):
        """
        :param args: can be

            * Circle
            * center, point on circle
            * center, radius
        """
        if len(args) == 1:  # Circle or derived class
            super(Circle, self).__init__(*args)
            self.c = Point2(args[0].c)
            self.p = Point2(args[0].p)
            self.r = args[0].r
        else:  # 2 first params are used to stay compatible with Arc2
            self.c = Point2(args[0])
            if isinstance(args[1], (float, int)):
                self.r = args[1]
                # for coherency + transform
                self.p = self.c+Vector2(args[1], 0)
            else:
                self.p = Point2(args[1])  # one point on circle
                self.r = self.p.distance(self.c)

    def __eq__(self, other):
        if not isinstance(other, Circle):
            return False
        return self.c == other.c and self.r == other.r

    def __repr__(self):
        return '%s(%s,%g)' % (self.__class__.__name__, self.c, self.r)

    def _apply_transform(self, t):
        self.c = t * self.c
        self.p = t * self.p
        self.r = abs(self.p-self.c)

    def __abs__(self):
        """:return: float perimeter"""
        return 2.0*pi*self.r

    @property
    def center(self):
        return self.c

    @property
    def area(self):
        return pi*self.r*self.r

    def point(self, u):
        ":return: Point2 at angle u radians"
        return self.c+Polar(self.r, u)

    def tangent(self, u):
        ":return: Vector2 tangent at angle u. Warning : tangent has magnitude r != 1"
        return Polar(self.r, u+pi/2.)

    def __contains__(self, pt):
        ":return: True if pt is ON or IN the circle"
        d = self.c.distance(pt)
        if d < self.r:
            return True  # IN the circle
        return math2.isclose(d, self.r, rel_tol=rel_tol)

    def intersect(self, other):
        """
        :param other: Line2, Ray2 or Segment2; returns a **Segment2** giving the
            part of the line that intersects the circle, or None if there is no intersection.
        """
        return other._intersect_circle(self)

    def _intersect_line2(self, other):
        return _intersect_line2_circle(other, self)

    def _intersect_circle(self, other):
        return _intersect_circle_circle(other, self)

    def connect(self, other):
        return other._connect_circle(self)

    def _connect_point2(self, other):
        return _connect_point2_circle(other, self)

    def _connect_line2(self, other):
        c = _connect_circle_line2(self, other)
        if c:
            return c.swap()

    def _connect_circle(self, other):
        return _connect_circle_circle(other, self)

    def swap(self):
        pass  # for consistency


def _center_of_circle_from_3_points(a, b, c):
    """
    constructs circle passing through 3 distinct points
    :param a,b,c: Point2 
    :return: x,y coordinates of center of circle

    geometrical implementation for reference:

        l1=Segment2(a,b).bisect()
        l2=Segment2(a,c).bisect()
        return = l1.intersect(l2).xy
    """
    # this implementation is much faster
    d = (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) * 2.0
    if d == 0.0:
        return None

    a2, b2, c2 = a.mag2(), b.mag2(), c.mag2()

    x = (a2 * (b.y - c.y) + b2 * (c.y - a.y) + c2 * (a.y - b.y)) / d
    y = (a2 * (c.x - b.x) + b2 * (a.x - c.x) + c2 * (b.x - a.x)) / d
    return x, y


def circle_from_3_points(a, b, c):
    """
    constructs Circle passing through 3 distinct points
    :param a,b,c: Point2 
    :return: the unique Circle through the three points a, b, c 
    """
    # future generalization : http://stackoverflow.com/questions/27673463/smallest-enclosing-circle-in-python-error-in-the-code
    x, y = _center_of_circle_from_3_points(a, b, c)
    return Circle((x, y), hypot(x - a.x, y - a.y))


def arc_from_3_points(a, b, c):
    """
    constructs Arc2 starting in a, going through b and ending in c
    :param a,b,c: Point2 
    :return: the unique Arc2 starting in a, going through b and ending in c
    """
    # more efficient method Ian Galton, "An efficient three-point arc algorithm"
    # see http://petrified.ucsd.edu/~ispg-adm/pubs/j_icga_89_1.pdf
    x, y = _center_of_circle_from_3_points(a, b, c)
    res = Arc2((x, y), a, c)
    if b not in res:
        res.dir = -res.dir
    return res


class Arc2(Circle):

    def __init__(self, center, p1=0, p2=2*pi, r=None, dir=1):
        """
        :param center: Point2 or (x,y) tuple
        :param p1: starting Point2 or angle in radians
        :param p2: ending Point2 or angle in radians
        :param r: float radius, needed only if p1 or p2 is an angle
        :param dir: arc direction. +1 is trig positive (CCW) and -1 is Clockwise

        """
        if isinstance(center, Arc2):  # copy constructor
            super(Arc2, self).__init__(center)
            self.p2 = Point2(center.p2)
            self.dir = center.dir
        else:
            c = Point2(center)
            if isinstance(p1, (int, float)):
                p = c+Polar(r, p1)
            else:
                p = Point2(p1)
                r = c.distance(p)
            super(Arc2, self).__init__(c, p)
            if isinstance(p2, (int, float)):
                self.p2 = c+Polar(r, p2)
            else:
                self.p2 = Point2(p2)
            self.dir = dir

        self._apply_transform(None)  # to set start/end angles
        # self.a is now start angle in [-pi,pi]
        # self.b is now end angle in [-pi,pi]

    def angle(self, b=None):
        """:return: float signed arc angle"""
        a = self.a
        if b is None:
            b = self.b
        if math2.isclose(a, b, rel_tol=rel_tol, abs_tol=rel_tol):  # handle complete arcs
            b = a
        res = b-a
        if math2.sign(res) == self.dir:
            return res
        else:  # return complementary angle
            return self.dir*(2*pi-abs(res))

    def __abs__(self):
        """:return: float arc length"""
        return abs(self.r*self.angle())

    # unlike Circle, Arc2 is parametrized on [0,1] for coherency with Segment2
    def _u_in(self, u):
        return u >= 0.0 and u <= 1.0

    def point(self, u):
        ":return: Point2 at parameter u"
        a = self.a+u*self.angle()
        return self.c+Polar(self.r, a)

    def tangent(self, u):
        """:return: Vector2 tangent at parameter u"""
        a = self.a+u*self.angle()
        res = Polar(self.r, a).cross()
        if self.dir > 0:
            return -res
        else:
            return res

    def _apply_transform(self, t):
        if t:
            super(Arc2, self)._apply_transform(
                t)  # TODO: support ellipsification
            self.p2 = t * self.p2
            self.dir = self.dir*t.orientation()  # to handle symmetries...
        self.a = (self.p-self.c).angle()  # start angle
        self.b = (self.p2-self.c).angle()  # end angle

    def __eq__(self, other):
        if not super(Arc2, self).__eq__(other):  # support Circles must be the same
            return False
        if self.dir == other.dir:
            return self.p == other.p and self.p2 == other.p2
        else:
            return self.p == other.p2 and self.p2 == other.p

    def __repr__(self):
        return '%s(center=%s,p1=%s,p2=%s,r=%s)' % (self.__class__.__name__, self.c, self.p, self.p2, self.r)

    def swap(self):
        # used by connect methods to switch order of points
        self.p, self.p2 = self.p2, self.p
        self.a, self.b = self.b, self.a
        self.dir = -self.dir
        return self

    def _u(self, pt):
        a = (pt-self.c).angle()
        res = self.angle(a)/self.angle()
        return None if res < 0 or res > 1 else res

    def __contains__(self, pt):
        ":return: True if pt is ON the Arc"
        return super(Arc2, self).__contains__(pt) and self._u(pt) is not None

    def intersect(self, other):
        inters = other._intersect_circle(self)
        if not inters:
            return None
        try:
            inters[1]
        except:
            inters = tuple(inters)
        res = []
        for pt in inters:
            if pt in self:
                res.append(pt)
        if len(res) == 0:
            return None
        elif len(res) == 1:
            return res[0]
        else:
            return res

    def _intersect_line2(self, other):
        return self.intersect(other)


class Ellipse(Circle):

    def __init__(self, *args):
        """
        :param args: can be

            * Ellipse
            * center, corner point
            * center, r1,r2,angle
        """
        super(Ellipse, self).__init__(*args)
        if len(args) == 1:  # Circle or derived class
            try:
                self.r2 = args[0].r2
            except:
                self.r2 = self.r
        else:  # 2 first params are used to stay compatible with Arc2
            try:
                self.r2 = args[2]
                # for coherency + transform
                self.p = self.c+Vector2(self.r, self.r2)
            except:
                self.p = Point2(args[1])  # point at ellipse "corner"
                self.r, self.r2 = (self.p-self.c).xy

    def __repr__(self):
        return '%s(%s,%g,%g)' % (self.__class__.__name__, self.c, self.r, self.r2)

    def __eq__(self, other):
        try:
            other = Ellipse(other)  # in case it's a Circle
        except:
            return False
        return self.c == other.c and self.r == other.r and self.r2 == other.r2

    def _apply_transform(self, t):
        self.c = t * self.c
        self.p = t * self.p
        self.r, self.r2 = (self.p-self.c).xy


class Matrix3(object):
    """
    Two matrix classes are supplied, *Matrix3*, a 3x3 matrix for working with 2D
    affine transformations, and *Matrix4*, a 4x4 matrix for working with 3D
    affine transformations.

    The default constructor intializes the matrix to the identity::

        >>> Matrix3()
        Matrix3([    1.00     0.00     0.00
                     0.00     1.00     0.00
                     0.00     0.00     1.00])
        >>> Matrix4()
        Matrix4([    1.00     0.00     0.00     0.00
                     0.00     1.00     0.00     0.00
                     0.00     0.00     1.00     0.00
                     0.00     0.00     0.00     1.00])

    **Element access**

    Internally each matrix is stored as a set of attributes named ``a`` to ``p``.
    The layout for Matrix3 is::

        # a b c
        # e f g
        # i j k

    and for Matrix4::

        # a b c d
        # e f g h
        # i j k l
        # m n o p

    If you wish to set or retrieve a number of elements at once, you can
    do so with a slice::

        >>> m = Matrix4()
        >>> m[:]
        [1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0]
        >>> m[12:15] = (5, 5, 5)
        >>> m
        Matrix4([    1.00     0.00     0.00     5.00
                     0.00     1.00     0.00     5.00
                     0.00     0.00     1.00     5.00
                     0.00     0.00     0.00     1.00])

    Note that slices operate in column-major order, which makes them
    suitable for working directly with OpenGL's ``glLoadMatrix`` and
    ``glGetFloatv`` functions.

    **Class constructors**

    There are class constructors for the most common types of transform.

    ``new_identity``
        Equivalent to the default constructor.  Example::

            >>> m = Matrix4.new_identity()
            >>> m
            Matrix4([    1.00     0.00     0.00     0.00
                         0.00     1.00     0.00     0.00
                         0.00     0.00     1.00     0.00
                         0.00     0.00     0.00     1.00])

    ``new_scale(x, y)`` and ``new_scale(x, y, z)``
        The former is defined on **Matrix3**, the latter on **Matrix4**.
        Equivalent to the OpenGL call ``glScalef``.
        Example::

            >>> m = Matrix4.new_scale(2.0, 3.0, 4.0)
            >>> m
            Matrix4([    2.00     0.00     0.00     0.00
                         0.00     3.00     0.00     0.00
                         0.00     0.00     4.00     0.00
                         0.00     0.00     0.00     1.00])

    ``new_translate(x, y)`` and ``new_translate(x, y, z)``
        The former is defined on **Matrix3**, the latter on **Matrix4**.
        Equivalent to the OpenGL call ``glTranslatef``.
        Example::

            >>> m = Matrix4.new_translate(3.0, 4.0, 5.0)
            >>> m
            Matrix4([    1.00     0.00     0.00     3.00
                         0.00     1.00     0.00     4.00
                         0.00     0.00     1.00     5.00
                         0.00     0.00     0.00     1.00])

    ``new_rotate(angle)``
        Create a **Matrix3** for a rotation around the origin.  *angle* is
        specified in radians, anti-clockwise.  This is not implemented in
        **Matrix4** (see below for equivalent methods).
        Example::

            >>> import math
            >>> m = Matrix3.new_rotate(math.pi / 2)
            >>> m
            Matrix3([    0.00    -1.00     0.00
                         1.00     0.00     0.00
                         0.00     0.00     1.00])

    The following constructors are defined for **Matrix4** only.

    ``new_rotatex(angle)``, ``new_rotatey(angle)``, ``new_rotatez(angle)``
        Create a **Matrix4** for a rotation around the X, Y or Z axis, respectively.
        *angle* is specified in radians.  Example::

            >>> m = Matrix4.new_rotatex(math.pi / 2)
            >>> m
            Matrix4([    1.00     0.00     0.00     0.00
                         0.00     0.00    -1.00     0.00
                         0.00     1.00     0.00     0.00
                         0.00     0.00     0.00     1.00])

    ``new_rotate_axis(angle, axis)``
        Create a **Matrix4** for a rotation around the given axis.  *angle*
        is specified in radians, and *axis* must be an instance of **Vector3**.
        It is not necessary to normalize the axis.  Example::

            >>> m = Matrix4.new_rotate_axis(math.pi / 2, Vector3(1.0, 0.0, 0.0))
            >>> m
            Matrix4([    1.00     0.00     0.00     0.00
                         0.00     0.00    -1.00     0.00
                         0.00     1.00     0.00     0.00
                         0.00     0.00     0.00     1.00])

    ``new_rotate_euler(heading, attitude, bank)``
        Create a **Matrix4** for the given Euler rotation.  *heading* is a rotation
        around the Y axis, *attitude* around the X axis and *bank* around the Z
        axis.  All rotations are performed simultaneously, so this method avoids
        "gimbal lock" and is the usual method for implemented 3D rotations in a
        game.  Example::

            >>> m = Matrix4.new_rotate_euler(math.pi / 2, math.pi / 2, 0.0)
            >>> m
            Matrix4([    0.00    -0.00     1.00     0.00
                         1.00     0.00    -0.00     0.00
                        -0.00     1.00     0.00     0.00
                         0.00     0.00     0.00     1.00])

    ``new_perspective(fov_y, aspect, near, far)``
        Create a **Matrix4** for projection onto the 2D viewing plane.  This
        method is equivalent to the OpenGL call ``gluPerspective``.  *fov_y* is
        the view angle in the Y direction, in radians.  *aspect* is the aspect
        ration *width* / *height* of the viewing plane.  *near* and *far* are
        the distance to the near and far clipping planes.  They must be
        positive and non-zero.  Example::

            >>> m = Matrix4.new_perspective(math.pi / 2, 1024.0 / 768, 1.0, 100.0)
            >>> m
            Matrix4([    0.75     0.00     0.00     0.00
                         0.00     1.00     0.00     0.00
                         0.00     0.00    -1.02    -2.02
                         0.00     0.00    -1.00     0.00])

    **Operators**

    Matrices of the same dimension may be multiplied to give a new matrix.
    For example, to create a transform which translates and scales::

        >>> m1 = Matrix3.new_translate(5.0, 6.0)
        >>> m2 = Matrix3.new_scale(1.0, 2.0)
        >>> m1 * m2
        Matrix3([    1.00     0.00     5.00
                     0.00     2.00     6.00
                     0.00     0.00     1.00])

    Note that multiplication is not commutative (the order that you apply
    transforms matters)::

        >>> m2 * m1
        Matrix3([    1.00     0.00     5.00
                     0.00     2.00    12.00
                     0.00     0.00     1.00])

    In-place multiplication is also permitted (and optimised)::

        >>> m1 *= m2
        >>> m1
        Matrix3([    1.00     0.00     5.00
                     0.00     2.00     6.00
                     0.00     0.00     1.00])

    Multiplying a matrix by a vector returns a vector, and is used to
    transform a vector::

        >>> m1 = Matrix3.new_rotate(math.pi / 2)
        >>> m1 * Vector2(1.0, 1.0)
        Vector2(-1.00, 1.00)

    Note that translations have no effect on vectors.  They do affect
    points, however::

        >>> m1 = Matrix3.new_translate(5.0, 6.0)
        >>> m1 * Vector2(1.0, 2.0)
        Vector2(1.00, 2.00)
        >>> m1 * Point2(1.0, 2.0)
        Point2(6.00, 8.00)

    Multiplication is currently incorrect between matrices and vectors -- the
    projection component is ignored.  Use the **Matrix4.transform** method
    instead.

    Matrix4 also defines **transpose** (in-place), **transposed** (functional),
    **determinant** and **inverse** (functional) methods.

    A **Matrix3** can be multiplied with a **Vector2** or any of the 2D geometry
    objects (**Point2**, **Line2**, **Circle**, etc).

    A **Matrix4** can be multiplied with a **Vector3** or any of the 3D geometry
    objects (**Point3**, **Line3**, **Sphere**, etc).

    For convenience, each of the matrix constructors are also available as
    in-place operators.  For example, instead of writing::

        >>> m1 = Matrix3.new_translate(5.0, 6.0)
        >>> m2 = Matrix3.new_scale(1.0, 2.0)
        >>> m1 *= m2

    you can apply the scale directly to *m1*::

        >>> m1 = Matrix3.new_translate(5.0, 6.0)
        >>> m1.scale(1.0, 2.0)
        Matrix3([    1.00     0.00     5.00
                     0.00     2.00     6.00
                     0.00     0.00     1.00])
        >>> m1
        Matrix3([    1.00     0.00     5.00
                     0.00     2.00     6.00
                     0.00     0.00     1.00])

    Note that these methods operate in-place (they modify the original matrix),
    and they also return themselves as a result.  This allows you to chain
    transforms together directly::

        >>> Matrix3().translate(1.0, 2.0).rotate(math.pi / 2).scale(4.0, 4.0)
        Matrix3([    0.00    -4.00     1.00
                     4.00     0.00     2.00
                     0.00     0.00     1.00])

    All constructors have an equivalent in-place method.  For **Matrix3**, they
    are ``identity``, ``translate``, ``scale`` and ``rotate``.  For **Matrix4**,
    they are ``identity``, ``translate``, ``scale``, ``rotatex``, ``rotatey``,
    ``rotatez``, ``rotate_axis`` and ``rotate_euler``.  Both **Matrix3** and
    **Matrix4** also have an in-place ``transpose`` method.

    The ``copy`` method is also implemented in both matrix classes and
    behaves in the obvious way.
    """

    def __init__(self, *args):
        self.identity()
        if not args:
            return
        if len(args) == 1:
            args = args[0][:]
        if len(args) == 9:
            self[:] = args
        else:
            raise RuntimeError('%s.__init__(%s) failed' %
                               (self.__class__.__name__, object))

    def __repr__(self):
        t = self.transposed()  # repr is by line while [:] is by column
        return ('%s%s') % (self.__class__.__name__, tuple(t))

    def __iter__(self):
        return iter((self.a, self.e, self.i,
                     self.b, self.f, self.j,
                     self.c, self.g, self.k))

    def __getitem__(self, key):
        try:  # is key a tuple ?
            key = 3*key[0]+key[1]
        except:
            pass
        return [self.a, self.e, self.i,
                self.b, self.f, self.j,
                self.c, self.g, self.k][key]

    def __setitem__(self, key, value):
        try:  # is key a tuple ?
            key = 3*key[0]+key[1]
        except:
            pass
        L = self[:]
        L[key] = value
        (self.a, self.e, self.i,
         self.b, self.f, self.j,
         self.c, self.g, self.k) = L

    def __eq__(self, other):
        return math2.allclose(self[:], other[:])

    def __sub__(self, other):
        return Matrix3(*(ai-bi for ai, bi in zip(self[:], other[:])))

    def __imul__(self, other):
        # assert isinstance(other, Matrix3)
        # Cache attributes in local vars (see Matrix3.__mul__).
        Aa = self.a
        Ab = self.b
        Ac = self.c
        Ae = self.e
        Af = self.f
        Ag = self.g
        Ai = self.i
        Aj = self.j
        Ak = self.k
        Ba = other.a
        Bb = other.b
        Bc = other.c
        Be = other.e
        Bf = other.f
        Bg = other.g
        Bi = other.i
        Bj = other.j
        Bk = other.k
        self.a = Aa * Ba + Ab * Be + Ac * Bi
        self.b = Aa * Bb + Ab * Bf + Ac * Bj
        self.c = Aa * Bc + Ab * Bg + Ac * Bk
        self.e = Ae * Ba + Af * Be + Ag * Bi
        self.f = Ae * Bb + Af * Bf + Ag * Bj
        self.g = Ae * Bc + Af * Bg + Ag * Bk
        self.i = Ai * Ba + Aj * Be + Ak * Bi
        self.j = Ai * Bb + Aj * Bf + Ak * Bj
        self.k = Ai * Bc + Aj * Bg + Ak * Bk
        return self

    def __mul__(self, other):
        if isinstance(other, Matrix3):
            res = copy(self)
            res *= other
        else:
            res = copy(other)
            res._apply_transform(self)
        return res

    def __call__(self, other):
        return self*other

    def identity(self):
        self.a = self.f = self.k = 1.
        self.b = self.c = self.e = self.g = self.i = self.j = 0
        return self

    def scale(self, x, y=None):
        if y is None:
            y = x
        return Matrix3.new_scale(x, y)*self

    def offset(self):
        return self*Point2(0, 0)

    def angle(self, angle=0):
        """
        :param angle: angle in radians of a unit vector starting at origin
        :return: float bearing in radians of the transformed vector
        """
        v = self*Polar(1.0, angle)
        return atan2(v.y, v.x)

    def mag(self, v=None):
        """Return the net (uniform) scaling of this transform.
        """
        if not v:
            v = Vector2(1, 1)
        return (self*v).mag()/v.mag()

    def translate(self, *args):
        """
        :param args: x,y values
        """
        x, y = argPair(*args)
        return Matrix3.new_translate(x, y)*self

    def rotate(self, angle):
        return Matrix3.new_rotate(angle)*self

    @classmethod
    def new_identity(cls):
        self = cls()
        return self

    @classmethod
    def new_scale(cls, x, y):
        self = cls()
        self.a = x
        self.f = y
        return self

    @classmethod
    def new_translate(cls, x, y):
        self = cls()
        self.c = x
        self.g = y
        return self

    @classmethod
    def new_rotate(cls, angle):
        self = cls()
        s = sin(angle)
        c = cos(angle)
        self.a = self.f = c
        self.b = -s
        self.e = s
        return self

    def mag2(self):
        return sum(x*x for x in self)

    def __abs__(self):
        return sqrt(self.mag2())

    def transpose(self):
        (self.a, self.e, self.i,
         self.b, self.f, self.j,
         self.c, self.g, self.k) = \
            (self.a, self.b, self.c,
             self.e, self.f, self.g,
             self.i, self.j, self.k)

    def transposed(self):
        M = copy(self)
        M.transpose()
        return M

    def determinant(self):
        return (self.a*self.f*self.k
                + self.b*self.g*self.i
                + self.c*self.e*self.j
                - self.a*self.g*self.j
                - self.b*self.e*self.k
                - self.c*self.f*self.i)

    def inverse(self):
        tmp = Matrix3()
        d = self.determinant()

        if abs(d) < 0.001:
            # No inverse, return identity
            return tmp
        else:
            d = 1.0 / d

            tmp.a = d * (self.f*self.k - self.g*self.j)
            tmp.b = d * (self.c*self.j - self.b*self.k)
            tmp.c = d * (self.b*self.g - self.c*self.f)
            tmp.e = d * (self.g*self.i - self.e*self.k)
            tmp.f = d * (self.a*self.k - self.c*self.i)
            tmp.g = d * (self.c*self.e - self.a*self.g)
            tmp.i = d * (self.e*self.j - self.f*self.i)
            tmp.j = d * (self.b*self.i - self.a*self.j)
            tmp.k = d * (self.a*self.f - self.b*self.e)

            return tmp

    def orientation(self):
        """
        :return: 1 if matrix is right handed, -1 if left handed
        """
        from .geom3d import Vector3  # TODO: remove this
        v1 = Vector3(self.a, self.b, self.c)
        v2 = Vector3(self.e, self.f, self.g)
        v3 = Vector3(self.i, self.j, self.k)
        return copysign(1, v1.cross(v2).dot(v3))
