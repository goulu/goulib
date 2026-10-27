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

    def test_aci_to_color(self):
        assert aci_to_color(1) == '#ff0000'
        assert aci_to_color(0, block_color='#123456') == '#123456'
        assert aci_to_color(256, layer_color='#654321') == '#654321'

    def test_xyy2xyz(self):
        assert xyy2xyz((0, 0, 0)) == (0, 0, 0)
        assert xyy2xyz((0.3127, 0.3290, 1.0)) == pytest.approx((0.950456, 1.0, 1.089058), abs=1e-3)


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
        assert Color('red').name == 'red'
        assert Color('#ff0000').name == 'red'

    def test___hash__(self):
        assert isinstance(hash(Color('blue')), int)

    def test___neg__(self):
        assert (-Color('red')).name == 'cyan'

    def test_deltaE(self):
        assert Color('red').deltaE(Color('red')) == pytest.approx(0)
        assert Color('red').deltaE(Color('blue')) > 10

    def test_str(self):
        c = self.blue
        res = '\n'.join('%s = %s' % (k, c.str(k)) for k in c._values)
        assert res

    def test_isclose(self):
        assert Color('red').isclose(Color('red'))
        assert not Color('red').isclose(Color('blue'))

    def test___mul__(self):
        white = Color('white')
        dim_white = white * 0.5
        assert dim_white.lab[0] < white.lab[0]
        assert (-white) == (white * -1)

    def test___radd__(self):
        assert 0 + self.blue == self.blue

    def test_compose(self):
        res = Color('red').compose(Color('lime'), math2.vecadd)
        assert len(res) == 3


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
        assert self.palette.index(self.palette[0]) == 0
        assert self.cmyk.index(self.cmyk['C']) == 'C'

    def test_update(self):
        p = Palette()
        p.update(['red', 'green', 'blue'])
        assert len(p) == 3

    def test_palette(self):
        p = Palette(['red', 'green', 'blue'], 'RGB')
        assert len(p) == 3

    def test_pil(self):
        assert len(self.cmyk.pil) == 12

    def test__repr_html_(self):
        res = self.palette._repr_html_()
        assert res  # TODO: more

    def test_sorted(self):
        s = self.cmyk.sorted()
        assert len(s) == 4

    def test___repr__(self):
        assert 'Palette of' in repr(self.palette)

    def test_patches(self):
        p = self.cmyk.patches(wide=2)
        assert p is not None


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
        assert deltaE('red', 'red') == pytest.approx(0)
        assert deltaE('red', 'blue') > 20


class TestColorTable:

    def test_color_table(self):
        t = ColorTable(color, width=5)
        assert t is not None


class TestBlackBody2Color:

    def test_blackbody2color(self):
        from goulib.table import Table, Cell
        from goulib.itertools2 import arange

        out = os.path.join(path, 'results', 'colors.blackbody.html')
        Table([Cell(str(t), style={'background-color': blackBody2Color(t).hex})
               for t in arange(500, 12000, 500)]).save(out)


class TestLambda:

    def test_lambda2RGB(self):
        for w in [390, 430, 460, 500, 540, 600, 670, 750, 300, 800]:
            rgb = lambda2RGB(w)
            assert len(rgb) == 3

    def test_RGB2lambda(self):
        assert RGB2lambda(255, 50, 0) > 0
        assert RGB2lambda(50, 255, 0) > 0
        assert RGB2lambda(0, 50, 255) > 0
        assert RGB2lambda(255, 0, 255) == 0

