from goulib.tests import *
from goulib.plot import *
import tempfile
import os


class DummyPlot(Plot):
    def _plot(self, ax, **kwargs):
        ax.plot([0, 1], [0, 1])
        return ax


class TestPlot:
    def test_render(self):
        p = DummyPlot()
        data = p.render('svg')
        assert b'<svg' in data
        data2 = render([p, p], 'png', xlim=(0, 1), ylim=(0, 1))
        assert len(data2) > 0

    def test_save(self):
        p = DummyPlot()
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            filename = f.name
        try:
            p.save(filename)
            assert os.path.getsize(filename) > 0
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    def test_repr_html(self):
        p = DummyPlot()
        html = p._repr_html_()
        assert html is not None

    def test_repr_svg(self):
        p = DummyPlot()
        svg_str = p._repr_svg_()
        assert '<svg' in svg_str

    def test_repr_png(self):
        p = DummyPlot()
        png_bytes = p._repr_png_()
        assert len(png_bytes) > 0

    def test_png(self):
        p = DummyPlot()
        img = p.png()
        assert img is not None

    def test_svg(self):
        p = DummyPlot()
        s = p.svg()
        assert s is not None

    def test_plot(self):
        p = DummyPlot()
        s = p.plot()
        assert s is not None


class TestPng:
    def test_png(self):
        p = DummyPlot()
        img = png([p])
        assert img is not None


class TestSvg:
    def test_svg(self):
        p = DummyPlot()
        s = svg([p])
        assert s is not None


class TestSave:
    def test_save(self):
        p = DummyPlot()
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            filename = f.name
        try:
            save([p], filename)
            assert os.path.getsize(filename) > 0
        finally:
            if os.path.exists(filename):
                os.remove(filename)
