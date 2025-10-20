from goulib.tests import *  # pylint: disable=wildcard-import, unused-wildcard-import
from goulib.colors import *  # pylint: disable=wildcard-import, unused-wildcard-import

import matplotlib

import os
path = os.path.dirname(os.path.abspath(__file__))


class TestConversions:

    def test_rgb2hex(self):
        assert rgb2hex((0, 16 / 255, 1)) == '#0010ff'

    def test_hex2rgb(self):
        assert hex2rgb('#0010ff') == (0, 16. / 255, 1)

    def test_rgb2cmyk(self):
        assert rgb2cmyk((0, 0, 0)) == (0, 0, 0, 1)
        assert pytest.approx(rgb2cmyk((.8, .6, .4))) == (0, 0.25, .5, 0.2)

    def test_cmyk2rgb(self):
        rgb = cmyk2rgb((1, 0, 1, .5))
        assert rgb == (0, .5, 0)

    def test_color_to_aci(self):
        assert color_to_aci('red') == 1
        assert color_to_aci(acadcolors[123]) == 123
        c = color_to_aci('#414142', True)
        assert acadcolors[c].hex == '#414141'

    @pytest.mark.skip(reason="not implemented")
    def test_aci_to_color(self):
        # assert_equal(expected, aci_to_color(x, block_color, layer_color))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_xyy2xyz(self):
        # assert_equal(expected, xyy2xyz(xyY))
        pytest.skip("not yet implemented")  # TODO: implement


class TestNearestColor:

    def test_nearest_color(self):
        assert nearest_color('#414142') == color['darkslategray']
        cmyk = Color((.45, .12, .67, .05), space='cmyk')
        p = nearest_color(cmyk, pantone)
        assert p.name == '802C'
        dE = deltaE


class TestColorRange:

    def test_color_range(self):
        c = color_range(5, 'red', 'blue')
        assert c[0] == color['red']
        assert c[1] == color['yellow']
        assert c[2] == color['lime']
        assert c[3] == color['cyan']
        assert c[4] == color['blue']


class TestColor:

    @classmethod
    def setup_class(self):
        self.blue = Color('blue')
        self.blues = [  # many ways to define the same color
            self.blue,
            Color('#0000ff'),
            Color((0, 0, 1)),
            Color((0, 0, 255)),
            Color(self.blue),
        ]

        self.red = Color('red')
        self.green = Color('lime')  # 'green' has hex 80 value, not ff

        self.white = color['white']

        # a random cmyk color
        self.cmyk = Color((.45, .12, .67, .05), space='cmyk')

    def test___init__(self):
        # check all constructors make the same color
        for b in self.blues:
            assert b == self.blue

    def test___add__(self):

        assert self.red + self.green + self.blue == 'white'
        assert self.red + self.green + self.blue == 'white'

    def test___sub__(self):
        white = Color('white')
        green = Color('lime')  # 'green' has hex 80 value, not ff
        blue = Color('blue')
        assert white - green - blue == 'red'

    def test___eq__(self):
        pass  # tested above

    def test___repr__(self):
        assert repr(Color('blue')) == "Color('blue')"

    def test__repr_html_(self):
        assert (Color('blue')._repr_html_() ==
                '<span style="color:#0000ff">blue</span>')

    def test_native(self):
        pass  # tested in convert

    def test_rgb(self):
        pass  # tested above

    def test_hex(self):
        assert self.cmyk.hex == '#85d550'

    def test_hsv(self):
        pass  # tested in convert

    def test_lab(self):
        pass  # tested in convert

    def test_luv(self):
        pass  # tested in convert

    def test_xyY(self):
        pass  # tested in convert

    def test_xyz(self):
        pass  # tested in convert

    def test_cmyk(self):
        assert Color('black').cmyk == (0, 0, 0, 1)
        assert Color('blue').cmyk == (1, 1, 0, 0)
        assert Color((0, .5, .5)).cmyk == (1, 0, 0, .5)  # teal

    def test_convert(self):
        """ test all possible round trip conversions for selected colors"""
        for color in ('green', 'red', 'blue', 'yellow', 'magenta', 'cyan', 'black', 'white'):
            c = Color(color)
            for startmode in colorspaces:
                start = Color(c.convert(startmode), startmode)
                for destmode in colorspaces:
                    dest = Color(start.convert(destmode), destmode)
                    back = Color(dest.convert(startmode), startmode)
                    if not back.isclose(start):
                        logging.error('round trip of %s from %s to %s failed with dE=%s' %
                                      (color, startmode, destmode,
                                       back.deltaE(start))
                                      )

    def test_name(self):
        # color = Color(value, space, name)
        # assert_equal(expected, color.name())
        pytest.skip("not yet implemented")  # TODO: implement

    def test___hash__(self):
        # color = Color(value, space, name)
        # assert_equal(expected, color.__hash__())
        pytest.skip("not yet implemented")  # TODO: implement

    def test___neg__(self):
        # color = Color(value, space, name)
        # assert_equal(expected, color.__neg__())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_deltaE(self):
        # color = Color(value, space, name)
        # assert_equal(expected, color.deltaE(other))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_str(self):
        c = self.blue
        res = '\n'.join('%s = %s' % (k, c.str(k)) for k in c._values)
        assert res

    def test_isclose(self):
        # color = Color(value, space, name)
        # assert_equal(expected, color.isclose(other, abs_tol))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___mul__(self):
        # color = Color(value, space, name)
        # assert_equal(expected, color.__mul__(factor))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___radd__(self):
        # color = Color(value, space, name)
        # assert_equal(expected, color.__radd__(other))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_compose(self):
        # color = Color(value, space, name)
        # assert_equal(expected, color.compose(other, f, mode))
        pytest.skip("not yet implemented")  # TODO: implement


class TestPalette:

    @classmethod
    def setup_class(self):
        self.palette = Palette(matplotlib.colormaps['nipy_spectral'])
        # indexed by letters
        self.cmyk = Palette(['cyan', 'magenta', 'yellow', 'black'], 'CMYK')
        self.cmyk_int = Palette(
            ['cyan', 'magenta', 'yellow', 'black'])  # indexed by ints

    def test___init__(self):
        assert len(self.palette) == 256
        assert len(self.cmyk) == 4
        assert self.cmyk['M'].name == 'magenta'
        assert self.cmyk_int[2].name == 'yellow'

    def test_index(self):
        # palette = Palette(data, n)
        # assert_equal(expected, palette.index(c, dE))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_update(self):
        # palette = Palette(data, n)
        # assert_equal(expected, palette.update(data, n))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_palette(self):
        # assert_equal(expected, palette(im, ncolors))
        pytest.skip("not yet implemented")  # TODO: implement

    def test_pil(self):
        # palette = Palette(data, n)
        # assert_equal(expected, palette.pil())
        pytest.skip("not yet implemented")  # TODO: implement

    def test__repr_html_(self):
        res = self.palette._repr_html_()
        assert res  # TODO: more

    def test_sorted(self):
        # palette = Palette(data, n)
        # assert_equal(expected, palette.sorted(key))
        pytest.skip("not yet implemented")  # TODO: implement

    def test___repr__(self):
        # palette = Palette(data, n)
        # assert_equal(expected, palette.__repr__())
        pytest.skip("not yet implemented")  # TODO: implement

    def test_patches(self):
        # palette = Palette(data, n)
        # assert_equal(expected, palette.patches(wide, size))
        pytest.skip("not yet implemented")  # TODO: implement


class TestColorLookup:

    def test_color_lookup(self):
        c = color['blue']
        c2 = color_lookup[c.hex]
        assert c == c2


class TestPantone:

    def test_pantone(self):
        from goulib.table import Table, Cell
        from goulib.itertools2 import reshape

        t = [Cell(name, style={'background-color': pantone[name].hex})
             for name in sorted(pantone)]
        t = Table(reshape(t, (0, 10)))
        out = os.path.join(path, 'results', 'colors.pantone.html')
        with open(out, 'w') as f:
            f.write(t.html())


class TestDeltaE:

    def test_delta_e(self):
        # assert_equal(expected, deltaE(c1, c2))
        pytest.skip("not yet implemented")  # TODO: implement


class TestColorTable:

    def test_color_table(self):
        # assert_equal(expected, ColorTable(colors, key, width))
        pytest.skip("not yet implemented")  # TODO: implement


class TestBlackBody2Color:

    def test_blackbody2color(self):
        from goulib.table import Table, Cell
        from goulib.itertools2 import arange

        out = os.path.join(path, 'results', 'colors.blackbody.html')
        Table([Cell(str(t), style={'background-color': blackBody2Color(t).hex})
               for t in arange(500, 12000, 500)]).save(out)
