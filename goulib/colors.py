"""
color conversion in various colorspaces and palettes
"""

__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2012-, Philippe Guglielmetti"
__license__ = "LGPL"
__credits__ = ['Colormath https://pypi.python.org/pypi/colormath/',
               'Bruno Nuttens Pantone color table http://blog.brunonuttens.com/206-conversion-couleurs-pantone-lab-rvb-hexa-liste-sql-csv/',
               ]

# get https://pypi.python.org/pypi/colormath/ if you need more

import os
import sys
import numpy
import networkx
from collections import OrderedDict

from goulib import math2, itertools2, image, graph
import goulib.table as Gtable

# color conversion

# redefine some converters in current module to build converters dict below
import skimage.color as skcolor

import matplotlib.colors as mplcolors


def rgb2hex(c, illuminant='ignore'):
    return mplcolors.rgb2hex(c)


def hex2rgb(c, illuminant='ignore'):
    return mplcolors.hex2color(c)


def rgb2cmyk(rgb, **kwargs):
    """
    :param rgb: 3-tuple of floats of red,green,blue in [0..1] range
    :return: 4-tuple of floats (cyan, magenta, yellow, black) in [0..1] range
    """
    # http://stackoverflow.com/questions/14088375/how-can-i-convert-rgb-to-cmyk-and-vice-versa-in-python

    r, g, b = rgb

    c = 1 - r
    m = 1 - g
    y = 1 - b

    k = min(c, m, y)
    if k == 1:
        return (0, 0, 0, 1)
    c = (c - k) / (1 - k)
    m = (m - k) / (1 - k)
    y = (y - k) / (1 - k)
    return (c, m, y, k)


def cmyk2rgb(cmyk, **kwargs):
    """
    :param cmyk: 4-tuple of floats (cyan, magenta, yellow, black) in [0..1] range
    :result: 3-tuple of floats (red,green,blue)
    warning : rgb is out the [0..1] range for some cmyk

    """
    c, m, y, k = cmyk
    w = 1 - k
    return ((1 - c) * w, (1 - m) * w, (1 - y) * w)


def xyz2xyy(xyz, **kwargs):
    """
    Convert from XYZ to xyY

    Based on formula from http://brucelindbloom.com/Eqn_XYZ_to_xyY.html

    Implementation Notes:
    1. Watch out for black, where X = Y = Z = 0. In that case, x and y are set
       to the chromaticity coordinates of the reference whitepoint.
    2. The output Y value is in the nominal range [0.0, Y[XYZ]].

    """
    s = sum(xyz)
    if s == 0:
        # We can't check for X == Y == Z == 0 because they may actually add up
        # to 0, thus resulting in ZeroDivisionError later
        x, y, _ = xyz2xyy(color['white'].xyz)
        return (x, y, 0.0)
    return (xyz[0] / s, xyz[1] / s, xyz[1])


def xyy2xyz(xyY, **kwargs):
    """
    Convert from xyY to XYZ to

    Based on formula from http://brucelindbloom.com/Eqn_xyY_to_XYZ.html

    Implementation Notes:

    1. Watch out for the case where y = 0.
       In that case, you may want to set X = Y = Z = 0.
    2. The output XYZ values are in the nominal range [0.0, 1.0].

    """
    x, y, Y = xyY
    if y == 0:
        return (0, 0, 0)
    X = x * Y / y
    Z = (1 - x - y) * Y / y
    return (X, Y, Z)

# skimage.color has several useful color conversion routines, but for images
# so here is a generic adapter that allows to call them with colors


def _skadapt(f, **kwargs):

    def adapted(arr, **kwargs):
        arr = numpy.asanyarray(arr)
        if arr.ndim == 1:
            a = arr.reshape(1, 1, arr.shape[-1])
            try:
                res = f(a, **kwargs)
            except TypeError:  # unsupported params. retry without
                res = f(a)
            return res.reshape(arr.shape[-1])
        else:
            return f(arr, **kwargs)

    return adapted


# supported colorspaces. need more ? just add it :-)
colorspaces = (
    'CMYK',
    'XYZ',
    'xyY',  # for CIE Chromaticity plots
    'Lab',
    'Luv',
    'HSV',
    'RGB',
    'HEX',
)

# build a graph of available converters
# as in https://github.com/gtaylor/python-colormath

# a nx.DiGraph() would suffice, but my DiGraph are better
converters = graph.DiGraph(multi=False)
for source in colorspaces:
    for target in colorspaces:
        key = (source.lower(), target.lower())
        if key[0] == key[1]:
            continue
        else:
            convname = '%s2%s' % key
            converter = getattr(sys.modules[__name__], convname, None)
            if converter is None:
                converter = getattr(skcolor, convname, None)
                if converter:  # adapt it:
                    converter = _skadapt(converter)
        if converter:
            converters.add_edge(key[0], key[1], f=converter)


def convert(color, source, target):
    """convert a color between colorspaces,
    eventually using intermediary steps
    """
    source, target = source.lower(), target.lower()
    if source == target:
        return color
    path = converters.shortest_path(source, target)
    for u, v in itertools2.pairwise(path):
        color = converters[u][v][0]['f'](color)
    return color  # isn't it beautiful ?


class Color(object):
    """A color with math operations and conversions
    Color is immutable (._values caches representations)
    """

    def __init__(self, value, space='RGB', name=None, illuminant='D65'):
        """constructor
        :param value: string color name, hex string, or values tuple
        :param space: string defining the color space of value
        :param name: string for color name
        :param illuminant: string in {“A”, “D50”, “D55”, “D65”, “D75”, “E”} 
            * D65 is used by default in skimage, see http://scikit-image.org/docs/dev/api/skimage.color.html
            * D50 is used in Pantone and other graphic arts
        """
        self._name = name
        self.illuminant = illuminant
        space = space.lower()  # for easier conversions

        if isinstance(value, Color):  # copy constructor
            self._copy_from_(value)
            return
        if isinstance(value, str):
            if value in pantone:
                self._copy_from_(pantone[value])
                return
            value = value.lower()
            if value in color:
                self._copy_from_(color[value])
                return
            elif len(value) == 7 and value[0] == '#':
                if value in color_lookup:
                    self._copy_from_(color_lookup[value])
                    return
                else:
                    space = 'hex'
            else:
                raise (ValueError("Couldn't create Color(%s,%s)" % (value, space)))

        self.space = space  # "native" space in which the color was created

        if space == 'rgb':
            if max(value) > 1:
                value = tuple(_ / 255. for _ in value)
            # rgb only, not whiter than white...
            value = math2.sat(value[:3], 0, 1)
        if space != 'hex':  # force to floats
            value = tuple(float(_) for _ in value)
        self._values = OrderedDict()  # so native space is always first
        self._values[space] = value

    def _copy_from_(self, c):
        self.space = c.space
        self.illuminant = c.illuminant
        self._name = c._name
        self._values = c._values

    @property
    def name(self):
        if self._name is None:
            if self.hex in color_lookup:
                self._name = color_lookup[self.hex].name
            else:
                self._name = '~' + nearest_color(self).name
        return self._name

    def convert(self, target, **kwargs):
        """ 
        :param target: str of desired colorspace, or none for default
        :return: color in target colorspace
        """
        target = target.lower() if target else self.space
        if target not in self._values:
            try:
                path = converters.shortest_path(self.space, target)
            except networkx.NetworkXNoPath:
                raise NotImplementedError(
                    'no conversion between %s and %s color spaces'
                    % (self.space, target)
                )
            # to avoid incoherent cached values
            kwargs['illuminant'] = self.illuminant
            for u, v in itertools2.pairwise(path):
                if v not in self._values:
                    edge = converters[u][v][0]
                    c = edge['f'](self._values[u], **kwargs)

                    if itertools2.isiterable(c):  # but not a string
                        c = tuple(map(float, c))
                    self._values[v] = c
        return self._values[target]

    def str(self, mode=None):
        res = self.convert(mode)
        if not isinstance(res, str):
            res = ', '.join(map(math2.format, res))
        return res

    @property
    def native(self):
        return self.convert(None)

    @property
    def rgb(self):
        return self.convert('rgb')

    @property
    def hex(self):
        return self.convert('hex')

    @property
    def lab(self):
        return self.convert('lab')

    @property
    def luv(self):
        return self.convert('Luv')

    @property
    def cmyk(self):
        return self.convert('cmyk')

    @property
    def hsv(self):
        return self.convert('hsv')

    @property
    def xyz(self):
        return self.convert('xyz')

    @property
    def xyY(self):
        return self.convert('xyY')

    def __hash__(self):
        return hash(self.hex)

    def __repr__(self):
        return "Color('%s')" % (self.name)

    def _repr_html_(self):
        return '<span style="color:%s">%s</span>' % (self.hex, self.name)

    def compose(self, other, f, mode='rgb'):
        """ compose colors in given mode
        """
        if not isinstance(other, Color):
            other = Color(other, mode)
        res = f(self.convert(mode), other.convert(mode))
        min = -1 if mode == 'lab' else 0
        max = 1
        res = [math2.sat(_, min, max) for _ in res]
        return res

    def __add__(self, other):
        if isinstance(other, image.Image):
            return image.Image(size=other.size, color=self.native, mode=self.space) + other
        return Color(self.compose(other, math2.vecadd), illuminant=self.illuminant)

    def __radd__(self, other):
        """only to allow sum(colors) easily"""
        assert other == 0
        return self

    def __sub__(self, other):
        if isinstance(other, image.Image):
            mode = other.mode
            return image.Image(size=other.size, color=self.convert(mode), mode=mode) - other
        return Color(self.compose(other, math2.vecsub), illuminant=self.illuminant)

    def __mul__(self, factor):
        if factor < 0:
            return (-self) * (-factor)
        l, a, b = self.lab
        l *= factor
        res = Color((l, a, b), 'lab', illuminant=self.illuminant)
        return res

    def __neg__(self):
        """ complementary color"""
        return color['white'] - self

    def deltaE(self, other):
        """color difference according to CIEDE2000
        https://en.wikipedia.org/wiki/Color_difference
        """
        assert (self.illuminant == other.illuminant)
        return skcolor.deltaE_ciede2000(self.lab, other.lab)

    def isclose(self, other, abs_tol=1):
        """
        http://zschuessler.github.io/DeltaE/learn/
        <= 1.0    Not perceptible by human eyes.
        1 - 2    Perceptible through close observation.
        2 - 10    Perceptible at a glance.
        11 - 49    Colors are more similar than opposite
        100    Colors are exact opposite
        """
        dE = self.deltaE(other)
        if dE <= abs_tol:
            return True
        else:
            return False

    def __eq__(self, other):
        other = Color(other)
        if self.space == other.space:
            if self.native == other.native:
                return True
        # difference not perceptible to human eye
        return self.isclose(other, 1)


class Palette(OrderedDict):
    """dict of Colors indexed by anything"""

    def __init__(self, data=[], keys=256):
        # mandatory http://stackoverflow.com/questions/11174702/how-to-subclass-an-ordereddict
        super(Palette, self).__init__()
        if data:
            self.update(data, keys)

    def update(self, data, keys=256):
        """updates the dictionary with new colors
        :param data: colors to add
        :param keys: keys to use in dict, or int to discretize the Colormap
        """
        if isinstance(data, mplcolors.Colormap):
            for i in range(keys):
                self[i] = Color(data(i / (keys - 1)))  # RGB
        elif isinstance(keys, int):
            for i, v in itertools2.enumerates(data):
                self[i] = Color(v)  # v.space of RGB
        else:
            for i, v in zip(keys, data):
                self[i] = Color(v)  # v.space of RGB

        return None

    def index(self, c, dE=5):
        """
        :return: key of c or nearest color, None if distance is larger than deltaE
        """
        c = Color(c)
        k, v = itertools2.index_min(self, key=lambda c2: deltaE(c, c2))
        if k is None or (dE > 0 and deltaE(c, v) > dE):
            return None
        return k

    def __repr__(self):
        return '%s of %d colors' % (self.__class__.__name__, len(self))

    def _repr_html_(self):

        def tooltip(k):
            c = self[k]
            res = '[%s] %s (%s)\n' % (k, c.name, c.illuminant)
            return res + '\n'.join('%s = %s' % (k, c.str(k)) for k in c._values)

        mode = 'inline' if len(self) > 256 else 'flex'

        labels = (color['black'], color['white'])  # possible colors for labels
        res = '<div style="display:%s; width:100%%;">' % mode
        style = 'display:%s-block; min-width: 1px; ' % mode
        style += ' flex-basis: 90%%;'
        style += ' background:%s; color:%s;'
        cell = '<div style="' + style + '" title="%s">&nbsp;</div>'
        for k in self:
            c = self[k]
            # c2=nearest_color(c,labels,opt=max) #chose the label color with max difference to pantone color
            res += cell % (c.hex, c.hex, tooltip(k))
        return res + '</div>'

    def patches(self, wide=64, size=(16, 16)):
        """Image made of each palette color
        """
        n = len(self)
        data = itertools2.reshape(range(n), (n // wide, wide))
        res = image.Image(data, 'P', palette=self)
        res = res.scale(size)
        return res

    @property
    def pil(self):
        """
        :return: a sequence of integers, or a string containing a binary 
        representation of the palette.
        In both cases, the palette contents should be ordered (r, g, b, r, g, b, …). 
        The palette can contain up to 768 entries (3*256). 
        If a shorter palette is given, it is padded with zeros.
        #http://effbot.org/zone/creating-palette-images.htm
        """
        res = []
        for c in self.values():
            r, g, b = c.rgb
            res.append(math2.rint(r * 255))
            res.append(math2.rint(g * 255))
            res.append(math2.rint(b * 255))
        return res

    def sorted(self, key=lambda c: c[1].lab[0]):
        # http://stackoverflow.com/questions/8031418/how-to-sort-ordereddict-of-ordereddict-python
        return Palette(dict(sorted(self.items(), key=key)))


def ColorTable(colors, key=None, width=10):

    def tooltip(c):
        return '\n'.join('%s = %s' % (k, v) for k, v in c._values.items())

    labels = (color['black'], color['white'])  # possible colors for labels
    t = []
    colors = colors.values()
    if key:
        colors = list(colors)
        colors.sort(key=key)
    for c in colors:
        # chose the label color with max difference to pantone color
        c2 = nearest_color(c, labels, opt=max)
        s = '<span title="%s" style="color:%s">%s</span>' % (
            tooltip(c), c2.hex, c.name)
        t.append(Gtable.Cell(s, style={'background-color': c.hex}))
    return Gtable.Table(itertools2.reshape(t, (0, width)))

# dictionaries of standardized colors


path = os.path.dirname(os.path.abspath(__file__))

# http://blog.brunonuttens.com/206-conversion-couleurs-pantone-lab-rvb-hexa-liste-sql-csv/
table = Gtable.Table(path + '/colors.csv')
table.applyf('hex', lambda x: x.lower())
table = table.groupby('System')

color = Palette()  # dict of HTML / matplotlib colors, which seem to be the same
color_lookup = Palette()  # reverse color dict indexed by hex
pantone = Palette()  # dict of pantone colors

# http://www.w3schools.com/colors/colors_names.asp

for _ in table['websafe'].asdict():
    id = _['name'].lower()
    hex = _['hex']
    _ = Color(hex, name=id, illuminant='D65')
    color[id] = _
    color_lookup[_.hex] = _

for _ in table['Pantone'].asdict():
    id = _['name']
    pantone[id] = Color((_['L'], _['a'], _['b']),
                        space='Lab', name=id, illuminant='D50')
    # pantones are defined with D50 illuminant

acadcolors = [None] * 256  # table of Autocad indexed colors
for _ in table['autocad'].asdict():
    id = _['name']
    # color name is a 0..255 number
    acadcolors[id] = Color(_['hex'], name=id, illuminant='D65')


def color_to_aci(x, nearest=True):
    """
    :return: int Autocad Color Index of color x
    """
    if x is None:
        return -1
    x = Color(x)
    try:
        return acadcolors.index(x)
    except ValueError:
        pass
    if nearest:
        return nearest_color(x, acadcolors).name  # name = int id
    return -1


def aci_to_color(x, block_color=None, layer_color=None):
    if x == 0:
        return block_color
    if x == 256:
        return layer_color
    return acadcolors[x].hex


def deltaE(c1, c2):
    # http://scikit-image.org/docs/dev/api/skimage.color.html#skimage.color.deltaE_ciede2000
    if not isinstance(c1, Color):
        c1 = Color(c1)
    if not isinstance(c2, Color):
        c2 = Color(c2)
    return skcolor.deltaE_ciede2000(c1.lab, c2.lab)


def nearest_color(c, l=None, opt=min, comp=deltaE):
    """
    :param x: Color
    :param l: list or dict of Color, color by default
    :param opt: with opt=max you can find the most different color ...
    :return: nearest Color of x in  l
    """
    if not isinstance(c, Color):
        c = Color(c)
    l = l or color
    if isinstance(l, dict):
        l = l.values()
    return opt(l, key=lambda c2: comp(c, c2))

# http://stackoverflow.com/questions/876853/generating-color-ranges-in-python


def color_range(n, start, end, space='hsv'):
    """:param n: int number of colors to generate
    :param start: string hex color or color name
    :param end: string hex color or color name
    :result: list of n Color interpolated between start and end, included
    """

    start = Color(start).convert(space)
    end = Color(end).convert(space)
    return [Color(v, space=space) for v in itertools2.linspace(start, end, n)]


"""some (astro) physics calculators"""

_cmf = None


def blackBody2Color(tempK):
    """:param wavelength: black body temperature in K (Sun is 5780)
    :result: Color
    """
    from scipy.constants import h, c, k

    global _cmf
    if _cmf is None:
        _cmf = numpy.loadtxt(path + '/cie-cmf.txt', usecols=(1, 2, 3))

    # http://www.vendian.org/mncharity/dir3/blackbody/
    # https://scipython.com/blog/converting-a-spectrum-to-a-colour/#rating-26
    def planck(lam, T):
        """ Returns the spectral radiance of a black body at temperature T.
        Returns the spectral radiance, B(lam, T), in W.sr-1.m-2 of a black body
        at temperature T (in K) at a wavelength lam (in nm), using Planck's law.
        """

        lam_m = lam / 1.e9
        fac = h * c / lam_m / k / T
        B = 2 * h * c ** 2 / lam_m ** 5 / (numpy.exp(fac) - 1)
        return B

    def spec_to_xyz(spec):
        """Convert a spectrum to an xyz point.
        The spectrum must be on the same grid of points as the colour-matching
        function, self.cmf: 380-780 nm in 5 nm steps.
        """

        XYZ = numpy.sum(spec[:, numpy.newaxis] * _cmf, axis=0)
        den = numpy.sum(XYZ)
        if den == 0.:
            return XYZ
        return XYZ / den

    # The grid of visible wavelengths corresponding to the grid of colour-matching
    # functions used by the ColourSystem instance.
    lam = numpy.arange(380., 781., 5)

    return Color(spec_to_xyz(planck(lam, tempK)), 'xyz')


def lambda2RGB(w):
    """:param w: float wavelength in nanometers (between 380 and 780)
    :result: [R,G,B] float
    """
    # http://codingmess.blogspot.com/2009/05/conversion-of-nm-in-nanometers.html

    # colour
    if w >= 380 and w < 440:
        R = -(w - 440.) / (440. - 350.)
        G = 0.0
        B = 1.0
    elif w >= 440 and w < 490:
        R = 0.0
        G = (w - 440.) / (490. - 440.)
        B = 1.0
    elif w >= 490 and w < 510:
        R = 0.0
        G = 1.0
        B = -(w - 510.) / (510. - 490.)
    elif w >= 510 and w < 580:
        R = (w - 510.) / (580. - 510.)
        G = 1.0
        B = 0.0
    elif w >= 580 and w < 645:
        R = 1.0
        G = -(w - 645.) / (645. - 580.)
        B = 0.0
    elif w >= 645 and w <= 780:
        R = 1.0
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0

    # intensity correction
    if w >= 380 and w < 420:
        SSS = 0.3 + 0.7 * (w - 350) / (420 - 350)
    elif w >= 420 and w <= 700:
        SSS = 1.0
    elif w > 700 and w <= 780:
        SSS = 0.3 + 0.7 * (780 - w) / (780 - 700)
    else:
        SSS = 0.0
    SSS *= 255

    return [int(SSS * R), int(SSS * G), int(SSS * B)]


def RGB2lambda(R, G, B):
    # http://codingmess.blogspot.com/2010/02/transforming-rgb-data-to-wavelength.html
    """Returns 0 if indeciferable"""
    # selects range by maximum component
    # if max is blue - range is 380 - 489
    # if max is green - range is 490 - 579
    # if max is red - range is 580 - 645

    # which colour has highest intensity?
    high = float(R)
    highind = 1
    if G > high:
        high = float(G)
        highind = 2
    if B > high:
        high = float(B)
        highind = 3

    # normalize highest to 1.0
    RGBnorm = [R / high, G / high, B / high]

    # start decoding
    RGBlambda = 0
    if highind == 1:  # red is highest
        if B >= G:  # there is more blue than green
            return 0  # max red and more blue than green shouldn't happen
        # wavelength linearly changes from 645 to 580 as green increases
        RGBlambda = 645 - RGBnorm[1] * (645. - 580.)

    elif highind == 2:  # green is max, range is 510 - 579
        if R > B:  # range is 510 - 579
            RGBlambda = 510 + RGBnorm[0] * (580 - 510)
        else:  # blue is higher than red, range is 490 - 510
            RGBlambda = 510 - RGBnorm[2] * (510 - 490)

    elif highind == 3:  # blue is max, range is 380 - 490
        if G > R:  # range is 440 - 490
            RGBlambda = RGBnorm[1] * (490 - 440) + 440
        else:  # there is more red than green, range is 380 - 440
            RGBlambda = 440 - RGBnorm[0] * (440 - 380)

    return RGBlambda
