from goulib.tests import *
from goulib.motion import *

import os
path = os.path.dirname(os.path.abspath(__file__))


class TestPVA:
    def test___init__(self):
        pass  # tested below

    def test___call__(self):
        pass  # tested below


class TestSegment:
    def test___init__(self):
        pass  # tested below

    def test___call__(self):
        pass  # tested below

    def test_dt(self):
        pass  # tested below

    def test_end(self):
        pass  # tested below

    @classmethod
    def setup_class(self):
        self.seg = Segment2ndDegree(0, 2, (0, 0, 2))

    def test_start(self):
        assert self.seg.start() == (0, 0, 2, 0)

    def test_endAcc(self):
        assert self.seg.endAcc() == 2

    def test_endJerk(self):
        assert self.seg.endJerk() == 0

    def test_endPos(self):
        assert self.seg.endPos() == 4.0

    def test_endSpeed(self):
        assert self.seg.endSpeed() == 4.0

    def test_endTime(self):
        assert self.seg.endTime() == 2

    def test_startAcc(self):
        assert self.seg.startAcc() == 2

    def test_startJerk(self):
        assert self.seg.startJerk() == 0

    def test_startPos(self):
        assert self.seg.startPos() == 0

    def test_startSpeed(self):
        assert self.seg.startSpeed() == 0

    def test_startTime(self):
        assert self.seg.startTime() == 0

    def test_timeWhenPosBiggerThan(self):
        assert self.seg.timeWhenPosBiggerThan(1) > 0


class TestSegments:
    def test___init__(self):
        s1 = Segment2ndDegree(0, 2, (0, 0, 2))
        s2 = Segment2ndDegree(2, 4, (4.0, 4.0, -2.0))
        segs = Segments([s1, s2])
        assert segs.t0 == 0
        assert segs.t1 == 4
        assert segs(2) == (4.0, 4.0, -2.0, 0)
        assert segs.end() == (8.0, 0.0, -2.0, 0)
        s3 = Segment2ndDegree(4, 6, (8, 0, 1))
        segs.add(s3)
        assert segs.t1 == 6
        assert segs.end() == (10.0, 2.0, 1.0, 0)

    def test_add(self):
        s1 = Segment2ndDegree(0, 2, (0, 0, 2))
        segs = Segments([s1])
        s2 = Segment2ndDegree(2, 4, (4.0, 4.0, -2.0))
        segs.add(s2)
        s3 = Segment2ndDegree(6, 8, (8, 0, 1))
        segs.add(s3)  # should autoJoin
        assert segs.endTime() == 8
        assert segs.end() == (10.0, 2.0, 1.0, 0)
        assert len(
            segs.segments) == 4, 'must have 4 segments: 3 added and one from the autojoin'

    def test_add_bug(self):
        s1 = SegmentsTrapezoidalSpeed(t0=0, p0=0, p3=1.8, a=0.5, vmax=1)
        s1.add(SegmentsTrapezoidalSpeed(t0=25.688904, p0=1.8, p3=3.6, a=1))
        assert len(s1.segments) == 5, 's1 is initally 3 + 1 autojoin + 1 Segments'

    def test_timeWhenPosBiggerThan(self):
        s1 = SegmentsTrapezoidalSpeed(t0=0, p0=0, p3=1.8, a=0.5, vmax=1)
        t = s1.timeWhenPosBiggerThan(1, resolution=0.01)
        assert t == pytest.approx(2.01)

    def test_html(self):
        s1 = Segment2ndDegree(0, 2, (0, 0, 2))
        s2 = Segment2ndDegree(2, 4, (4.0, 4.0, -2.0))
        segs = Segments([s1, s2])
        assert segs.html() == 'Segments starts=0 ends=4<br/>t=0.000000 (0.000000,0.000000,2.000000,0.000000) --> t=2.000000 (4.000000,4.000000,2.000000,0.000000)<br/>t=2.000000 (4.000000,4.000000,-2.000000,0.000000) --> t=4.000000 (8.000000,0.000000,-2.000000,0.000000)<br/>'

    def test___call__(self):
        s1 = Segment2ndDegree(0, 2, (0, 0, 2))
        segs = Segments([s1])
        assert segs(1) == (1.0, 2.0, 2.0, 0)
        assert segs(5) == (0, 0, 0, 0)

    def test___str__(self):
        s1 = Segment2ndDegree(0, 2, (0, 0, 2))
        segs = Segments([s1])
        assert str(segs) == 'Segments starts=0 ends=2'

    def test_end(self):
        s1 = Segment2ndDegree(0, 2, (0, 0, 2))
        segs = Segments([s1])
        assert segs.end() == (4.0, 4.0, 2.0, 0)
        assert Segments().end() == (0, 0, 0, 0)

    def test_insert(self):
        segs = Segments()
        s1 = Segment2ndDegree(2, 4, (0, 0, 2))
        segs.insert(s1)
        s0 = Segment2ndDegree(0, 2, (0, 0, 2))
        segs.insert(s0)
        assert len(segs.segments) == 2

    def test_start(self):
        s1 = Segment2ndDegree(0, 2, (0, 0, 2))
        segs = Segments([s1])
        assert segs.start() == (0, 0, 2, 0)
        assert Segments().start() == (0, 0, 0, 0)

    def test_update(self):
        segs = Segments()
        segs.update()
        assert segs.t0 == -float('inf')


class TestSegmentPoly:
    @classmethod
    def setup_class(self):
        self.seg = SegmentPoly(1, 2, [1, 2, 3])

    def test___init__(self):
        pass  # tested above

    def test_start(self):
        pva = self.seg.start()
        assert pva == (1, 2, 6, 0)

    def test_end(self):
        pva = self.seg.end()
        assert pva == (6, 8, 6, 0)

    def test___call__(self):
        assert pytest.approx(self.seg(.9)) == (0, 0, 0, 0)
        assert pytest.approx(self.seg(1)) == (1, 2, 6, 0)
        assert pytest.approx(self.seg(2-1e-12)) == (6, 8, 6, 0)
        assert pytest.approx(self.seg(2)) == (0, 0, 0, 0)

    def test_save(self):
        self.seg.save(path+'/results/motion.SegmentPoly.png')


class TestSegment2ndDegree:
    @classmethod
    def setup_class(self):
        self.t0, self.t1 = 1, 2
        self.p0, self.v0, self.a = -1, 1, 2
        self.start = (self.p0, self.v0, self.a, 0)
        self.p1, self.v1, self.a1 = 1, 3, self.a
        self.end = (self.p1, self.v1, self.a1, 0)

    def test1(self):
        t0, t1, p0, v0, p1 = self.t0, self.t1, self.p0, self.v0, self.p1
        # time interval and start + end positions  + initial velocity
        seg = Segment2ndDegree(t0, t1, (p0, v0), p1)
        assert seg.start() == self.start
        assert seg.end() == self.end

    def test2(self):
        t0, t1, p0, v0, a = self.t0, self.t1, self.p0, self.v0, self.a
        # time interval and start pva
        seg = Segment2ndDegree(t0, t1, (p0, v0, a))
        assert seg.start() == self.start
        assert seg.end() == self.end

    def test3(self):
        t0, t1, p1, v1, a = self.t0, self.t1, self.p1, self.v1, self.a
        # time interval and end pva
        seg = Segment2ndDegree(t0, t1, None, (p1, v1, a))
        assert seg.start() == self.start
        assert seg.end() == self.end

    def test4(self):
        t0, p0, v0, p1, v1 = self.t0, self.p0, self.v0, self.p1, self.v1
        # start + end positions + velocities
        seg = Segment2ndDegree(t0, None, (p0, v0), (p1, v1))
        assert seg.start() == self.start
        assert seg.end() == self.end

    def test5(self):
        t0, p0, v0, a, v1 = self.t0, self.p0, self.v0, self.a, self.v1
        # start pva + end velocity
        seg = Segment2ndDegree(t0, None, (p0, v0, a), (None, v1))
        assert seg.start() == self.start
        assert seg.end() == self.end

    def test6(self):
        t1, p0, p1, v1, a = self.t1, self.p0, self.p1, self.v1, self.a
        # end pva + start position
        seg = Segment2ndDegree(None, t1, p0, (p1, v1, a))
        assert seg.start() == self.start
        assert seg.end() == self.end

    def test7(self):
        t1, v0, p1, v1, a = self.t1, self.v0, self.p1, self.v1, self.a
        # end pva + start velocity
        seg = Segment2ndDegree(None, t1, (None, v0), (p1, v1, a))
        assert seg.start() == self.start
        assert seg.end() == self.end

    def test8(self):
        t0, p0, p1, v0, a = self.t0, self.p0, self.p1, self.v0, self.a
        # start pva + end position
        seg = Segment2ndDegree(t0, None, (p0, v0, a), p1)
        assert seg.start() == self.start
        assert seg.end() == self.end

    def testover1(self):
        t0, t1, p0, v0, p1, a = self.t0, self.t1, self.p0, self.v0, self.p1, self.a * \
            2  # double acceleration
        # time interval, start pva, end position => adjust t1
        seg = Segment2ndDegree(t0, t1, (p0, v0, a), p1)
        assert seg.start() == (p0, v0, a, 0)
        assert seg.end()[0] == self.p1

    def testover2(self):  # acceleration ramp
        t0, t1, p0, v0, v1, a = self.t0, self.t1, self.p0, self.v0, self.v1, self.a * \
            2  # double acceleration
        # time interval, start pva, v1= max vel => adjust t1
        seg = Segment2ndDegree(t0, t1, (p0, v0, a), (None, v1))
        assert seg.start() == (p0, v0, a, 0)
        assert seg.end()[1] == self.v1
        assert seg.dt() == (self.t1-self.t0)/2.  # double acceleration => half dt

    def test_segment2nd_degree(self):
        seg = Segment2ndDegree(0, 2, (0, 0, 2))
        assert seg(1) == (1.0, 2.0, 2.0, 0)


class TestRamp:
    def test_ramp(self):
        pass  # tested above and below


class TestTrapeze:
    def test_trapeze(self):
        assert trapeze(1, 1, 1) == (1.0, 0.5, 1.0, 1.0, 0.5, 2.0)
        assert trapeze(2, 1, 1) == (1.0, 0.5, 1.0, 2.0, 1.5, 3.0)
        assert trapeze(0.1, 12, 10000)[-1] > trapeze(0.1, 25, 10000)[-1]


class TestSegmentTrapezoidalSpeed:
    def test_segmentTrapezoidalSpeed(self):
        trap = SegmentsTrapezoidalSpeed(
            t0=0, p0=0, p3=10.25, a=2.0, vmax=3.0, v0=1, v3=0)  # start @t0 = 0
        assert trap.t1 == 4.5
        assert trap.end() == (10.25, 0, -2, 0)
        trap = SegmentsTrapezoidalSpeed(
            t0=1, p0=0, p3=10.25, a=2.0, vmax=3.0, v0=1, v3=0)  # start @t0 != 0
        assert trap.endTime() == 5.5
        assert trap.t0 == 1
        assert trap.t1 == 5.5
        assert trap.segments[0].t1 == 2.0
        assert trap.segments[1].t1 == 4.0
        assert trap.segments[2].t1 == 5.5
        assert trap.end() == (10.25, 0, -2, 0)
        # time constraint with t0 = 0
        trap = SegmentsTrapezoidalSpeed(
            t0=0, p0=0, p3=6.0, T=2.0, a=0.0, v0=2, v3=2)
        assert trap.end() == (6.0, 2, -2, 0)
        # time constraint with t0 != 0 not yet implemented


class TestSegment4thDegree:
    @classmethod
    def setup_class(self):
        self.t0, self.t1 = 1, 2
        self.p0, self.v0, self.a0 = -1, 1, 0
        self.start = (self.p0, self.v0, self.a0, 0)
        self.p1, self.v1, self.a1 = 1, 3, 0
        self.end = (self.p1, self.v1, self.a1, 0)

    def test_segment4th_degree(self):
        seg = Segment4thDegree(self.t0, self.t1, self.start, self.end)
        assert seg.start()[:3] == pytest.approx(self.start[:3])  # ignore jerk
        assert seg.end()[:3] == pytest.approx(self.end[:3])  # ignore jerk
        assert seg((self.t0+self.t1)/2.) == pytest.approx((-0.3125, 2.0, 3.0, 0.0))  # truediv


class TestSegmentsTrapezoidalSpeed:
    def test_segments_trapezoidal_speed(self):
        s = SegmentsTrapezoidalSpeed(t0=0, p0=0, p3=10, a=2, vmax=4)
        assert s.t1 > 0
        assert s.end()[0] == 10
