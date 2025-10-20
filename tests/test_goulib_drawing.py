from goulib.tests import *


from goulib.geom import *
from goulib.drawing import *

import os
path = os.path.dirname(os.path.abspath(__file__))
results = os.path.join(path, 'results', 'drawing')  # path for results


class TestTrans:
    def test_trans(self):
        assert Trans() == Matrix3(1, 0, 0, 0, 1, 0, 0, 0, 1)
        assert Trans(scale=2) == Matrix3(
            2, 0, 0, 0, 2, 0, 0, 0, 1)
        assert Trans(offset=(2, 3)) == Matrix3(1, 0, 0, 0, 1, 0, 2, 3, 1)
        s32 = sqrt(3)/2
        # warning : .new takes columnwise elements
        assert Trans(rotation=60) == Matrix3(
            0.5, +s32, 0, -s32, 0.5, 0, 0, 0, 1)


class TestBBox:
    @classmethod
    def setup_class(self):
        self.empty = BBox()
        self.unit = BBox((0, 1), (1, 0))
        self.box = BBox((-1, -2), (3, 4))

    def test___init__(self):
        pass

    def test___repr__(self):
        assert repr(self.box) == "[[-1,3), [-2,4)]"

    def test___call__(self):
        assert self.box() == [-1, -2, 3, 4]

    def test___iadd__(self):
        self.box += None  # must pass

    def test___add__(self):
        b1 = self.unit+self.box
        b2 = self.box+self.unit
        assert b1 == b2
        pytest.skip("not yet implemented")  # TODO: implement

    def test_xmin(self):
        assert self.unit.xmin == 0
        assert self.box.xmin == -1

    def test_xmax(self):
        assert self.unit.xmax == 1
        assert self.box.xmax == 3

    def test_ymin(self):
        assert self.unit.ymin == 0
        assert self.box.ymin == -2

    def test_ymax(self):
        assert self.unit.ymax == 1
        assert self.box.ymax == 4

    def test_xmed(self):
        assert self.unit.xmed == 0.5
        assert self.box.xmed == 1

    def test_ymed(self):
        assert self.unit.ymed == 0.5
        assert self.box.ymed == 1

    def test_width(self):
        assert self.unit.width == 1
        assert self.box.width == 4

    def test_height(self):
        assert self.unit.height == 1
        assert self.box.height == 6

    def test_center(self):
        assert self.box.center() == Point2(1, 1)

    def test_size(self):
        assert self.box.size() == (4, 6)

    def test___contains__(self):

        p1 = (.5, .5)
        p2 = Point2(.99, 1.01)

        assert p1 in self.unit
        assert not p2 in self.unit
        assert not Segment2(p1, p2) in self.unit
        assert not [p1, p2] in self.unit

        # tangent to box is not in box ...
        assert not Circle(p1, 0.5) in self.unit
        assert Circle(p1, 0.4999999) in self.unit

        assert self.unit in self.box

    def test_trans(self):
        t = Trans(offset=(-1, -2), scale=(4, 6), rotation=0)
        assert self.unit.trans(t) == self.box

    def test_area(self):
        # b_box = BBox(p1, p2)
        # assert_equal(expected, b_box.area())
        # TODO: implement  # implement your test here
        pytest.skip("not yet implemented")


class TestEntity:
    @classmethod
    def setup_class(self):
        self.seg = Segment2((1, 0), (2, 3))
        self.arc = Arc2((1, 1), (0, 0), radians(120))
        self.circle = Circle((1, 1), 2)
        self.point = Point2(0, 0)

    def test___init__(self):
        pass

    def test___repr__(self):
        # entity = Entity()
        # assert_equal(expected, entity.__repr__())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_bbox(self):
        # entity = Entity()
        # assert_equal(expected, entity.bbox())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_end(self):
        # entity = Entity()
        # assert_equal(expected, entity.end())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_from_dxf(self):
        # entity = Entity()
        # assert_equal(expected, entity.from_dxf(trans))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_isclosed(self):
        # entity = Entity()
        # assert_equal(expected, entity.isclosed())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_ishorizontal(self):
        # entity = Entity()
        # assert_equal(expected, entity.ishorizontal(tol))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_isline(self):
        # entity = Entity()
        # assert_equal(expected, entity.isline())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_isvertical(self):
        # entity = Entity()
        # assert_equal(expected, entity.isvertical(tol))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_start(self):
        # entity = Entity()
        # assert_equal(expected, entity.start())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_to_dxf(self):
        # entity = Entity()
        # assert_equal(expected, entity.to_dxf(**attr))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_center(self):
        # entity = Entity()
        # assert_equal(expected, entity.center())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_from_svg(self):
        # entity = Entity()
        # assert_equal(expected, entity.from_svg())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_artist(self):
        # entity = Entity()
        # assert_equal(expected, entity.artist(ax, **kwargs))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_from_pdf(self):
        pass  # tested elsewhere

    def test_svg_path(self):
        # entity = Entity()
        # assert_equal(expected, entity.svg_path(currentpos))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_patches(self):
        # entity = Entity()
        # assert_equal(expected, entity.patches(**kwargs))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___copy__(self):
        s2 = copy(self.seg)
        assert not self.seg.p is s2.p  # Segment2.copy is in fact a deepcopy
        s2.layer = "something"
        s3 = copy(s2)
        assert s3.layer == "something"

    def test_draw(self):
        # entity = Entity()
        # assert_equal(expected, entity.draw(fig, **kwargs))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_figure(self):
        # entity = Entity()
        # assert_equal(expected, entity.figure(**kwargs))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_render(self):
        a = Point2(0, 1)
        b = Point2(1, 1)
        c = Point2(1, 0)
        g = Group([a, b, c])
        g.render('svg')

    def test_setattr(self):
        # entity = Entity()
        # assert_equal(expected, entity.setattr(**kwargs))
        pytest.skip("not yet implemented")  # TODO: implement


class TestGroup:
    @classmethod
    def setup_class(self):
        # example from notebook
        a = Arc2((0, 0), (0, 1), (1, 0))
        l1 = Segment2((-2, .5), Vector2(4, 0))  # horizontal at y=0.5
        l2 = Segment2((-2, -.5), Vector2(4, 0))  # horizontal at y=-0.5
        lines = Group([l1, l2])
        lines.color = 'blue'
        # list of intersection points
        pts = Group([i[0] for i in lines.intersect(a)])
        self.group = Group([lines, a, pts])
        self.group.render('svg')

        # second example from notebook
        r1 = Rect((0, 0), (-1, 1))
        r2 = Rect((1, -1), (2, 2))
        c1 = Circle(Point2(4, 4), 1)
        c2 = Circle(Point2(0, 2), .5)
        s1 = r1.connect(r2)
        s1.color = 'red'
        s2 = r2.connect(c1)
        s2.color = 'red'
        s3 = c1.connect(c2)
        s3.color = 'red'

        self.group = Group([r1, r2, c1, c2, s1, s2, s3])

    def test_distance(self):
        g2 = Trans(scale=2, offset=(10, 1), rotation=30)*self.group
        g2.color = 'blue'
        Drawing([self.group, g2]).save(results+'drawing.Group.distance.png')
        assert self.group.distance(g2) == pytest.approx(2.026833782163534)

    def test_append(self):
        # group = Group()
        # assert_equal(expected, group.append(entity, **kwargs))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_extend(self):
        # group = Group()
        # assert_equal(expected, group.extend(entities, **kwargs))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_from_dxf(self):
        try:
            import dxfgrabber
        except:
            pytest.skip("not yet implemented")  # TODO: implement  # optional

        dxf = Drawing(path+'/data/Homer_Simpson_by_CyberDrone.dxf')
        self.blocks = dxf.block
        assert 'hand 1' in self.blocks

    def test_swap(self):
        # group = Group()
        # assert_equal(expected, group.swap())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_length(self):
        assert self.group.length == 27.22534104051515

    def test___copy__(self):
        # group = Group()
        # assert_equal(expected, group.__copy__())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_color(self):
        # group = Group()
        # assert_equal(expected, group.color())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_color_case_2(self):
        # group = Group()
        # assert_equal(expected, group.color(c))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_chainify(self):
        # group = Group()
        # assert_equal(expected, group.chainify(mergeable))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_layer(self):
        # group = Group()
        # assert_equal(expected, group.layer())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_layer_case_2(self):
        # group = Group()
        # assert_equal(expected, group.layer(l))
        pytest.skip("not yet implemented")  # TODO: implement


class TestChain:
    @classmethod
    def setup_class(self):
        group = Group()
        group.append(Segment2((0, 0), (1, 1)))
        group.append(Segment2((2, 0), Point2(1, 1)))
        self.chain = Chain(group)

    def test___init__(self):
        pass  # tested above

    def test_append(self):
        chain = Chain(self.chain)  # copy
        assert not chain.isclosed()
        chain.append(Segment2((0, 0), (2, 0)))
        assert chain.isclosed()

    def test___repr__(self):
        assert repr(self.chain) == 'Chain(Point2(0, 0),Point2(2, 0),2)'

    def test_bbox(self):
        # chain = Chain()
        # assert_equal(expected, chain.bbox())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_start(self):
        assert self.chain.start == Point2(0, 0)

    def test_end(self):
        assert self.chain.end == Point2(2, 0)

    def test_from_dxf(self):
        # chain = Chain()
        # assert_equal(expected, chain.from_dxf(trans))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_to_dxf(self):
        # chain = Chain()
        # assert_equal(expected, chain.to_dxf(split, **attr))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_from_svg(self):
        # chain = Chain(data)
        # assert_equal(expected, chain.from_svg())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_from_pdf(self):
        # chain = Chain(data)
        # assert_equal(expected, chain.from_pdf(color))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_contiguous(self):
        # chain = Chain(data)
        # assert_equal(expected, chain.contiguous(edge, tol, allow_swap))
        pytest.skip("not yet implemented")  # TODO: implement


class TestDrawing:
    @classmethod
    def setup_class(self):
        self.dxf = Drawing(path+'/data/drawing.dxf')
        self.svg = Drawing(path+'/data/drawing.svg')
        self.pdf = Drawing(path+'/data/drawing.pdf')

        seg = Segment2((1, 0), (2, 3))
        arc = Arc2((1, 1), (0, 0), radians(120))
        circle = Circle((1, 1), 2)
        self.simple = Drawing(data=[seg, arc, circle])

    def test_load(self):
        return
        cube = Drawing(path+'/data/cubeecraft_template.pdf')
        cube.save(results+'cubeecraft.dxf')

    def test_save(self):
        for ext in ['png', 'svg', 'pdf', 'dxf']:
            if self.dxf:
                self.dxf.save(results+'drawing.dxf.%s' % ext)
            self.svg.save(results+'drawing.svg.%s' % ext)
            self.pdf.save(results+'drawing.pdf.%s' % ext)

    def test___init__(self):
        pass  # tested above

    def test_bbox(self):
        # drawing = Drawing(filename, options, **kwargs)
        # assert_equal(expected, drawing.bbox(layers, ignore))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_read_dxf(self):
        pass  # tested above

    def test_read_svg(self):
        puzzle = Drawing(path+'/data/jigsaw.svg')
        puzzle.save(results+'jigsaw.dxf')
        suisse = Drawing(path+'/data/switzerlandLow.svg')
        suisse.save(results+'switzerlandLow.png')

    def test_read_pdf(self):
        pantone = Drawing(path+'/data/Pantone Fan.pdf')
        pantone.save(results+'Pantone_Fan_out.pdf')

    def test_draw(self):
        # drawing = Drawing(filename, **kwargs)
        # assert_equal(expected, drawing.draw(fig, **kwargs))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_figure(self):
        # drawing = Drawing(filename, **kwargs)
        # assert_equal(expected, drawing.figure(**kwargs))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_render(self):
        assert b'!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"' in self.simple.render(
            'svg')


class TestSpline:
    def test___init__(self):
        # spline = Spline(points)
        pytest.skip("not yet implemented")  # TODO: implement

    def test_bbox(self):
        # spline = Spline(points)
        # assert_equal(expected, spline.bbox())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_end(self):
        # spline = Spline(points)
        # assert_equal(expected, spline.end())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_start(self):
        # spline = Spline(points)
        # assert_equal(expected, spline.start())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_swap(self):
        # spline = Spline(points)
        # assert_equal(expected, spline.swap())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_xy(self):
        # spline = Spline(points)
        # assert_equal(expected, spline.xy())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_length(self):
        # spline = Spline(points)
        # assert_equal(expected, spline.length())
        pytest.skip("not yet implemented")  # TODO: implement

    def test___copy__(self):
        # spline = Spline(points)
        # assert_equal(expected, spline.__copy__())
        pytest.skip("not yet implemented")  # TODO: implement


class TestRect:
    @classmethod
    def setup_class(self):
        # see IPython notebook for graphical examples
        self.r1 = Rect((0, 0), (-1, 1))
        self.r2 = Rect((1, -1), (2, 2))

    def test___init__(self):
        pass  # tested above

    def test_connect(self):
        s1 = self.r1.connect(self.r2)
        assert s1 == Segment2(Point2(0, 0), Point2(1, 0))
        c1 = Circle(Point2(4, 1), 1)
        s2 = self.r2.connect(c1)
        assert s2 == Segment2(Point2(2, 1), Point2(3, 1))

    def test_distance(self):
        assert self.r1.distance(self.r2) == 1

    def test___repr__(self):
        # rect = Rect(*args)
        # assert_equal(expected, rect.__repr__())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_p1(self):
        # rect = Rect(*args)
        # assert_equal(expected, rect.p1())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_p2(self):
        # rect = Rect(*args)
        # assert_equal(expected, rect.p2())
        pytest.skip("not yet implemented")  # TODO: implement


class TestText:
    def test___init__(self):
        # text = Text(text, point, size, rotation)
        pytest.skip("not yet implemented")  # TODO: implement

    def test_bbox(self):
        # text = Text(text, point, size, rotation)
        # assert_equal(expected, text.bbox())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_patches(self):
        # text = Text(text, point, size, rotation)
        # assert_equal(expected, text.patches(**kwargs))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_to_dxf(self):
        # text = Text(text, point, size, rotation)
        # assert_equal(expected, text.to_dxf(**attr))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_intersect(self):
        # text = Text(text, point, size, rotation)
        # assert_equal(expected, text.intersect(other))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_length(self):
        # text = Text(text, point, size, rotation)
        # assert_equal(expected, text.length())
        pytest.skip("not yet implemented")  # TODO: implement


class TestInstance:
    def test___init__(self):
        # instance = Instance(group, trans, name)
        pytest.skip("not yet implemented")  # TODO: implement

    def test___iter__(self):
        # instance = Instance(group, trans, name)
        # assert_equal(expected, instance.__iter__())
        pytest.skip("not yet implemented")  # TODO: implement

    def test___repr__(self):
        # instance = Instance(group, trans, name)
        # assert_equal(expected, instance.__repr__())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_from_dxf(self):
        # instance = Instance()
        # assert_equal(expected, instance.from_dxf(blocks, mat3))
        pytest.skip("not yet implemented")  # TODO: implement


class TestCalcBulge:
    def test_calc_bulge(self):
        # assert_equal(expected, calcBulge(p1, bulge, p2))
        pytest.skip("not yet implemented")  # TODO: implement


class TestChains:
    def test_chains(self):
        # assert_equal(expected, chains(group, tol, mergeable))
        pytest.skip("not yet implemented")  # TODO: implement


class test__Group:
    def test_bbox(self):
        # __group = _Group()
        # assert_equal(expected, __group.bbox(filter))
        # TODO: implement  # implement your test here
        pytest.skip("not yet implemented")

    def test_connect(self):
        # __group = _Group()
        # assert_equal(expected, __group.connect(other))
        # TODO: implement  # implement your test here
        pytest.skip("not yet implemented")

    def test_intersect(self):
        # __group = _Group()
        # assert_equal(expected, __group.intersect(other))
        # TODO: implement  # implement your test here
        pytest.skip("not yet implemented")

    def test_length(self):
        # __group = _Group()
        # assert_equal(expected, __group.length())
        # TODO: implement  # implement your test here
        pytest.skip("not yet implemented")

    def test_patches(self):
        # __group = _Group()
        # assert_equal(expected, __group.patches(**kwargs))
        # TODO: implement  # implement your test here
        pytest.skip("not yet implemented")

    def test_to_dxf(self):
        # __group = _Group()
        # assert_equal(expected, __group.to_dxf(**kwargs))
        # TODO: implement  # implement your test here
        pytest.skip("not yet implemented")


if __name__ == "__main__":
    runmodule(level=logging.WARNING)
