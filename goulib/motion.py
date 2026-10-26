"""
motion simulation (kinematics)
"""

__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2013, Philippe Guglielmetti"
__credits__ = ["http://osterone.bobstgroup.com/wiki/index.php?title=UtlCam"]
__license__ = "LGPL"

from . import plot, polynomial, itertools2, math2


class PVA(plot.Plot):  # TODO: make it an Expr
    """represents a function of time returning position, velocity, and acceleration
    """

    def __init__(self, funcs):
        self.funcs = funcs

    def __call__(self, t, t0=0):
        return tuple(f(t - t0) for f in self.funcs)


class Segment(PVA):
    """ a PVA defined between 2 times, null elsewhere
    """

    def __init__(self, t0, t1, funcs):
        super(Segment, self).__init__(funcs)
        self.t0 = t0
        self.t1 = t1
        self.ticks = []

    def dt(self):
        return self.t1 - self.t0

    def start(self):
        return super(Segment, self).__call__(self.t0, self.t0)

    def startPos(self):
        return self.start()[0]

    def startSpeed(self):
        return self.start()[1]

    def startAcc(self):
        return self.start()[2]

    def startJerk(self):
        return self.start()[3]

    def startTime(self):
        return self.t0

    def end(self):
        return super(Segment, self).__call__(self.t1, self.t0)

    def endPos(self):
        return self.end()[0]

    def endSpeed(self):
        return self.end()[1]

    def endAcc(self):
        return self.end()[2]

    def endJerk(self):
        return self.end()[3]

    def endTime(self):
        return (self.t1)

    def timeWhenPosBiggerThan(self, pos, resolution=0.010):
        """ search the first time when the position is bigger than pos
        :params pos: the pos that must at least be reached
        :params resolution: the time resolution in sec"""
        # brute force and stupid!!!
        for t in itertools2.arange(self.t0, self.t1, resolution):
            p= self(t)[0]
            if p >= pos:
                break
        return t

    def __call__(self, t):
        if t >= self.t0 and t < self.t1:
            return super(Segment, self).__call__(t, self.t0)
        else:
            return (0,) * len(self.funcs)

    def _plot(self, ax, t0=None, t1=None, ylim=None, **kwargs):
        """
        :params ticks: a list of (time,state) to add ticks
        """
        if t0 is None: t0 = self.t0
        if t1 is None: t1 = self.t1
        step = (t1 - t0) / 500.
        x = [t for t in itertools2.arange(t0, t1, step)]
        y = [self(t) for t in x]
        y = map(list, zip(*y))  # transpose because of
        labels = ['pos', 'vel', 'acc', 'jrk']
        for y_arr, label in zip(y, labels):
            ax.plot(x, y_arr, label=label)
        ax.legend(loc='best')
        #        for tick in self.ticks:
        #            ax.axvline(x=tick[0],color='0.5')
        return ax


class Segments(Segment):
    def __init__(self, segments=[], label='Segments'):
        """
        can be initialized with a list of segment (that of course can also be a Segments)
        :param label: a label can be given
        """
        self.label = label
        self.t0 = -float('inf')
        self.t1 = -float('inf')
        self.segments = []
        self.add(segments)

    def __str__(self):
        return self.label

    def html(self):
        t = self.label + '<br/>'
        for s in self.segments:
            t += 't=%f (%f,%f,%f,%f) --> t=%f (%f,%f,%f,%f)<br/>' % (
                s.t0, s.start()[0], s.start()[1], s.start()[2], s.start()[3],
                s.t1, s.endPos(), s.endSpeed(), s.endAcc(), s.end()[3])
        return t

    def update(self):
        """ yet only calculates t0 and t1 """
        for s in self.segments:
            if s.t0 < self.t0:
                self.t0 = s.t0
            if s.t1 > self.t1:
                self.t1 = s.t1

    def insert(self, segment, autoJoin=True):
        """insert a segment into Segments

        :param segment: the segment to add. must be in a range that is not already defined or it will rise a value error exception
        :param autoJoin: if True and the added segment has the same starting position as the last segment's end
            and both velocity are 0 then a segment of (pos,v=0,a=0) is automatically added.
            this help discribing movements only where there is curently a movement
        """

        t0 = segment.t0
        t1 = segment.t1
        if self.segments == []:
            self.segments = [segment]
            self.t0 = segment.t0
            self.t1 = segment.t1
            return
        if t0 >= self.segments[-1].t1:
            previous = self.segments[-1]
            previousP = previous.endPos()
            previousT = previous.endTime()
            previousV = previous.endSpeed()
            segmentP = segment.start()[0]
            segmentV = segment.start()[1]
            if autoJoin and t0 > previousT and math2.allclose([previousP, previousV, segmentV], [segmentP, 0, 0],
                                                              abs_tol=0.001):
                self.segments.append(SegmentPoly(previous.t1, t0, [previous.endPos()]))
            self.segments.append(segment)
            return
        if t1 <= self.segments[0].t0:
            self.segments.insert(0, segment)
            return
        for i in range(0, len(self.segments) - 1):
            if self.segments[i].t1 <= t0 and self.segments[i + 1].t0 >= t1:
                self.segments.insert(i + 1, segment)
                return
        l = ''
        for s in self.segments:
            l += '\n' + str(s.t0) + '-->' + str(s.t1)
        raise ValueError('impossible to add the segment t0=' + str(segment.t0) + ' t1=' + str(
            segment.t1) + ' to already existing segments' + l)

    def add(self, segments, autoJoin=True):
        """ add a segment or a list of segment to the segments """
        if type(segments) is not list:
            self.insert(segments, autoJoin)
        else:
            for s in segments:
                self.insert(s, autoJoin)
        self.update()
        self.label = 'Segments starts=' + str(self.t0) + ' ends=' + str(self.t1)

    def start(self):
        if self.segments != []:
            return self.segments[0].start()
        else:
            return (0, 0, 0, 0)

    def end(self):
        if self.segments != []:
            return self.segments[-1].end()
        else:
            return (0, 0, 0, 0)

    def __call__(self, t):
        for s in self.segments:
            if t >= s.t0 and t < s.t1:
                return s(t)
        return (0, 0, 0, 0)  # oversimplified: assuming PVAJ; should check that all segments are of the same nature


class SegmentPoly(Segment):
    """ a segment defined by a polynomial position law
    """

    def __init__(self, t0, t1, p):
        p = polynomial.Polynomial(p)
        v = p.derivative()
        a = v.derivative()
        j = a.derivative()
        super(SegmentPoly, self).__init__(t0, t1, (p, v, a, j))

    def _latex(self):
        """:return: string LaTex formula"""
        return 'pos(t)=%s' % self.funcs[0]._latex(x='t')

    def _repr_latex_(self):
        return '$%s$' % self._latex()


def _pva(val):
    try:
        p = val[0]
    except:
        p = val
    try:
        v = val[1]
    except:
        v = None
    try:
        a = val[2]
    except:
        a = None
    return p, v, a


def _delta(x0, x1):
    try:
        return float(x1 - x0)
    except:
        return None


def ramp(dp, v0, v1, a):
    """
    :param dp: float delta position or None if unknown
    :param v0: float initial velocity or None if unknown
    :param v1: float final velocity or None if unknown
    :param a: float acceleration
    :return: float shortest time to accelerate between constraints
    """
    dt = []
    dv = _delta(v0, v1)
    if dv:
        dt.append(dv / a)  # time to accelerate
    try:  # solve a.t^2/2+v0.t == dp
        dt.extend(list(math2.quad(a / 2., v0, -dp)))
    except:
        try:  # solve v1.t-a.t^2/2 == dp
            dt.extend(list(math2.quad(-a / 2., v1, -dp)))
        except:
            pass
    return min(t for t in dt if t > 0)  # return smallest positive


def trapeze(dp, vmax, a, v0=0, v2=0):
    """
    :param dp: float delta position
    :param vmax: float maximal velocity
    :param a: float acceleration
    :param v0: float initial velocity, 0 by default 
    :param v2: float final velocity, 0 by default 
    :return: tuple of 6 values:
    
    * time at end of acceleration
    * position at end of acceleration
    * velocity at end of acceleration
    * time at begin of deceleration
    * position at begin of deceleration
    * total time
    """
    t1 = ramp(dp / 2., v0, vmax, a)  # acceleration time
    v1 = v0 + a * t1  # speed reached
    p1 = t1 * (v0 + v1) / 2.  # position at end of acceleration
    t3 = ramp(dp / 2., v1, v2, -a)  # deceleration time
    p2 = t3 * (v1 + v2) / 2.  # distance to decelerate
    t2 = float(dp - p1 - p2) / v1  # time at constant velocity
    return t1, p1, v1, t1 + t2, dp - p2, t1 + t2 + t3


def Segment2ndDegree(t0, t1, start, end=(None))->SegmentPoly:
    """calculates a constant acceleration Segment between start and end
    
    :param t0,t1: float start,end time. one of both may be None for undefined
    :param start: (position, velocity, acceleration) float tuple. some values may be None for undefined
    :param end: (position, velocity, acceleration) float tuple. some values may be None for undefined
    :return: :class:`SegmentPoly`
    
    the function can cope with almost any combination of defined/undefined parameters,
    among others (see tests):
    
    * Segment2ndDegree(t0,t1,(p0,v0),p1) # time interval and start + end positions  + initial speed
    * Segment2ndDegree(t0,t1,(p0,v0,a)) # time interval and start with acceleration
    * Segment2ndDegree(t0,t1,None,(p1,v1,a)) # time interval and end pva
    * Segment2ndDegree(t0,None,(p0,v0),(p1,v1)) # start + end positions + velocities
    * Segment2ndDegree(t0,None,(p0,v0,a),(None,v1)) # start pva + end velocity
    * Segment2ndDegree(None,t1,p0,(p1,v1,a)) # end pva + start position
    
    the function also accepts some combinations of overconstraining parameters:
    
    * Segment2ndDegree(t0,t1,(p0,v0,a),p1) # time interval, start pva, end position => adjust t1
    * Segment2ndDegree(t0,t1,(p0,v0,a),(None,v1)) # time interval, start pva, v1=max vel => adjust t1
    
    :raise ValueError: when not enough parameters are specified to define the Segment univoquely
    
    """
    p0, v0, a0 = _pva(start)
    p1, v1, a1 = _pva(end)
    if a0 is None: a0 = a1
    # to handle the many possible cases, we evaluate missing information in a loop
    for _retries in range(2):  # two loops are enough to solve all cases , according to tests
        dt = _delta(t0, t1)
        dp = _delta(p0, p1)
        dv = _delta(v0, v1)

        if not itertools2.any((dt, p0, v0, a0), lambda x: x is None):  # we have all required data
            res = SegmentPoly(t0, t1, [p0, v0, a0 / 2.])
            end = res.end()
            if p1 is not None and not math2.isclose(end[0], p1):  # consider p1 as max position
                res2 = Segment2ndDegree(t0, None, (p0, v0, a0), p1)
                if res2.dt() < res.dt():  # this case arises earlier
                    res = res2
            if v1 is not None and not math2.isclose(end[1], v1):  # consider v1 as max velocity
                res2 = Segment2ndDegree(t0, None, (p0, v0, a0), (None, v1))
                if res2.dt() < res.dt():  # this case arises earlier
                    res = res2
            return res

        if dt is None:  # try to determine it from available params
            if a0:
                dt = ramp(dp, v0, v1, a0)
            else:
                try:
                    dt = 2. * dp / (v0 + v1)  # time to reach the position
                except:
                    pass

        if t0 is None:
            try:
                t0 = t1 - dt
            except:
                pass
        if t1 is None:
            try:
                t1 = t0 + dt
            except:
                pass

        if a0 is None:
            try:
                a0 = float(dv) / dt
            except:
                try:
                    a0 = 2. * (dp - v0 * dt) / dt * dt
                except:
                    pass
        if v0 is None:
            try:
                v0 = v1 - a0 * dt
            except:
                pass
        if p0 is None:
            try:
                p0 = p1 - dt * float(v1 + v0) / 2.
            except:
                pass

    raise ValueError


def Segment4thDegree(t0, t1, start, end):
    """smooth trajectory from an initial position and initial speed (p0,v0) to a final position and speed (p1,v1)
    * if t1<=t0, t1 is calculated
    """
    p0, v0, _a0 = _pva(start)
    p1, v1, _a1 = _pva(end)

    if t1 <= t0:
        dt = float(p1 - p0) / ((v1 - v0) / 2. + v0)  # truediv
        t1 = t0 + dt
    else:
        dt = t1 - t0
    return SegmentPoly(t0, t1, [p0, v0, 0, float(v1 - v0) / (dt * dt), -float(v1 - v0) / (2 * dt * dt * dt)])  # truediv


def SegmentsTrapezoidalSpeed(t0, p0, p3, a, T=0, vmax=float('inf'), v0=0, v3=0):
    """
    :param t0: float start time
    :param p0: float start position
    :param p3: float end position
    :param a: float specified acceleration. if =0, use specified time
    :param T: float specified time. if =0 (default), use specified acceleration
    :param vmax: float max speed. default is infinity (i.e. triangular speed)
    :param v0: initial speed
    :param v3: final speed (if T != 0 then v3 = v0)

    ::

           v1  +-------+    
              /         \
             /           +  v3
        v0  +
            |  |       | |
           t0  t1     t2 t3 
    """
    dp = p3 - p0
    if T != 0:
        assert t0 == 0.0, 'must fix this bug'
        assert v3 == v0, 'if T is the constraint, v0 must equal v3'
        t1 = T / 2
        v1 = dp / t1 - v0  # (v0+v1)/2 *t1 = dp/2  ==> v0*t1 + v1*t1 =dp
        if v1 > vmax:
            RuntimeError('vmax not yet implemented: must be infinite')
        else:
            a = (v1 - v0) / t1
    (t1, p1, v1, t2, p2, t3) = trapeze(dp, vmax, a, v0, v3)
    label = 'Trapeze start={0}, end={1}'.format(t0, t0 + t3)
    acc = Segment2ndDegree(t0, t1 + t0, (p0, v0, a))
    cst = SegmentPoly(t1 + t0, t2 + t0, [p1 + p0, v1])
    dec = Segment2ndDegree(t2 + t0, t3 + t0, (p2 + p0, v1, -a))
    trap = Segments([acc, cst, dec], label=label)
    return trap
