"""
image processing with PIL's ease and skimage's power

:requires:

* `scikit-image <http://scikit-image.org/>`_
* `PIL or Pillow <http://pypi.python.org/pypi/pillow/>`_

:optional:

* `pdfminer.six <http://pypi.python.org/pypi/pdfminer.six/>`_ for pdf input

"""

__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2015, Philippe Guglielmetti"
__credits__ = ['Brad Montgomery http://bradmontgomery.net']
__license__ = "LGPL"

# http://python-prepa.github.io/ateliers/image_tuto.html

import logging
import functools
import base64
import math
import sys
import io
import os
import skimage.color as skcolor
import skimage

from urllib import request
from urllib.parse import urlparse
import PIL.Image as PILImage

import numpy as np
from goulib import itertools2, math2, plot, drawing, graph
from goulib import colors as Gcolors

# import warnings
# warnings.filterwarnings("ignore")  # because too many are generated

urlopen = request.urlopen


class Mode(object):

    def __init__(self, name, nchannels, type, min, max):
        self.name = name.lower()
        self.nchannels = nchannels
        self.type = type
        self.min = min
        self.max = max

    def __repr__(self):
        return "Mode('%s',%dx%s,[%d-%d]" % (self.name, self.nchannels, self.type, self.min, self.max)


modes = {
    # http://pillow.readthedocs.io/en/3.1.x/handbook/concepts.html#concept-modes
    # + some others
    '1': Mode('bool', 1, np.uint8, 0, 1),  # binary
    'F': Mode('gray', 1, float, 0, 1),  # gray level
    'U': Mode('gray', 1, np.uint16, 0, 65535),  # skimage gray level
    'I': Mode('gray', 1, np.int16, -32768, 32767),  # skimage gray level
    'L': Mode('gray', 1, np.uint8, 0, 255),  # single layer or RGB(A)
    'P': Mode('ind', 1, np.uint16, 0, 65535),  # indexed color (palette)
    'RGB': Mode('rgb', 3, float, 0, 1),  # not uint8 as in PIL
    'RGBA': Mode('rgba', 4, float, 0, 1),  # not uint8 as in PIL
    'CMYK': Mode('cmyk', 4, float, 0, 1),  # not uint8 as in PIL
    'LAB': Mode('lab', 3, float, -1, 1),
    # https://en.wikipedia.org/wiki/CIE_1931_color_space
    'XYZ': Mode('xyz', 3, float, 0, 1),
    # https://en.wikipedia.org/wiki/HSL_and_HSV
    'HSV': Mode('hsv', 3, float, 0, 1),
}

# hash methods
AVERAGE = 0
PERCEPTUAL = 1


def nchannels(arr):
    return 1 if len(arr.shape) == 2 else arr.shape[-1]


def guessmode(arr):
    n = nchannels(arr)
    if n > 1:
        return 'RGBA'[:n]
    if arr.dtype == bool:
        return '1'
    if np.issubdtype(arr.dtype, float):
        return 'F'
    if arr.dtype == np.uint8:
        return 'L' if arr.max() > 1 else '1'
    if arr.dtype == np.uint16:
        return 'U'
    return 'I'


def adapt_rgb(func):
    """Decorator that adapts to RGB(A) images to a gray-scale filter.

    :param func: function that returns a filtered image from an image-filter and RGB
        image. This will only be called if the image is RGB-like.
    """

    # adapted from https://github.com/scikit-image/scikit-image/blob/master/skimage/color/adapt_rgb.py
    @functools.wraps(func)
    def _adapter(image, *args, **kwargs):
        if image.nchannels > 1 or image.mode == 'P':
            channels = image.split('RGB')
            for i in range(3):  # RGB. If there is an A, it is untouched
                channels[i] = func(channels[i], *args, **kwargs)
            return Image(channels, 'RGB')
        else:
            return func(image, *args, **kwargs)

    return _adapter


class Image(plot.Plot):

    def __init__(self, data=None, mode=None, **kwargs):
        """
        :param data: can be either:

            * `PIL.Image` : makes a copy
            * string : path of image to load OR PNG encoded image
            * memoryview (extracted from a db blob)
            * None : creates an empty image with kwargs parameters:

                - size : (y,x) pixel size tuple
                - mode : 'F' (gray) by default
                - color: to fill None=black by default
                - colormap: Palette or matplotlib colormap
        """

        if isinstance(data, bytes):  # check if encoded string
            t = b'\x89PNG'
            if data[:4] == t:
                data = io.BytesIO(data)

        if isinstance(data, memoryview):
            data = io.BytesIO(data)

        if isinstance(data, io.BytesIO):
            data = PILImage.open(data)

        if data is None:
            mode = mode or 'F'
            n = modes[mode].nchannels
            size = tuple(kwargs.get('size', (0, 0)))
            if n > 1:
                size = size + (n,)
            c = kwargs.get('color', 'black')
            if isinstance(c, (tuple, list)) and len(c) == n:
                color = c
            else:
                c = Gcolors.Color(c)
                if mode == 'RGBA':
                    color = c.rgb + (1.0,)
                elif mode == 'CMYK':
                    color = c.cmyk
                elif n == 1:
                    color = c.rgb[0]
                else:
                    color = c.rgb
            data = np.ones(size, dtype=modes[mode].type) * color
            self._set(data, mode)
        elif isinstance(data, Image):  # copy constructor
            self.mode = data.mode
            self.array = data.array
            self.palette = data.palette
        elif isinstance(data, str):  # assume a path
            self.load(data, **kwargs)
        elif isinstance(data, tuple):  # (image,palette) tuple return by convert
            self._set(data[0], 'P')
            self.setpalette(data[1])
        else:  # assume some kind of array
            try:  # list of Images ?
                data = [im.array for im in data]
            except:
                pass
            self._set(data, mode)
        # make sure the image has a palette attribute
        try:
            self.palette
        except AttributeError:
            self.palette = None
            for arg in ['colormap', 'palette', 'colors']:  # aliases
                try:
                    self.setpalette(kwargs[arg])
                    break  # found it
                except (AssertionError, KeyError):
                    pass

    def _set(self, data, mode=None, copy=False):
        data = np.asanyarray(data)
        if copy:
            data = data.copy()
        if mode == 'LAB' and np.max(data) > 1:
            data = data / 100
        elif mode != '1' and data.dtype == np.uint8 and np.max(data) == 1:
            data = data * 255
        s = data.shape
        if len(s) == 3:
            if s[0] < 10 and s[1] > 10 and s[2] > 10:
                data = np.transpose(data, (1, 2, 0))
        self.mode = mode or guessmode(data)
        self.array=convert_type(data,modes[self.mode].type)

    @property
    def shape(self):
        # always return y,x,nchannels
        s = self.array.shape
        if len(s) == 2:
            s = (s[0], s[1], 1)
        return s

    @property
    def size(self):
        return self.shape[:2]

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def nchannels(self):
        return self.shape[2]

    @property
    def npixels(self):
        return math2.mul(self.size)

    def __nonzero__(self):
        return self.npixels > 0

    def __lt__(self, other):
        """ is smaller"""
        return self.npixels < other.npixels

    def load(self, path):
        from skimage import io
        if not io.util.is_url(path):
            path = os.path.abspath(path)
        self.path = path
        ext = path[-3:].lower()
        if ext == 'pdf':
            data = read_pdf(path)
        else:
            with io.util.file_or_url_context(path) as context:
                data = io.imread(context)
        mode = guessmode(data)
        self._set(data, mode)
        return self

    def save(self, path, autoconvert=True, format=None):
        """saves an image
        :param path: string with path/filename.ext
        :param autoconvert: bool, if True converts color planes formats to RGB
        :param format_str: str of file format. set to 'PNG' by skimage.io.imsave
        :param kwargs: optional params passed to skimage.io.imsave:
        :return: self for chaining
        """
        mode = self.mode
        if autoconvert:
            if self.nchannels == 1 and self.mode != 'P':
                mode = 'L'
            elif self.mode not in 'RGBA':  # modes we can save directly
                mode = 'RGB'
        a = self.convert(mode).array  # makes sure we don't change self.array
        if format is None and isinstance(path, str):
            ext = path.split('.')[-1].lower()
            if ext in ('jpg', 'jpeg'):
                format = 'JPEG'
            else:
                format = ext[:3]
        if format.upper() == 'TIF':
            skimage.io.imsave(path, skimage.img_as_uint(a))
        else:
            Image(a).pil.save(path, format=format)
        return self

    def _repr_svg_(self, **kwargs):
        raise NotImplementedError()  # and should never be ...
        # ... because it causes _repr_png_ to be called by Plot._repr_html_
        # instead of render below

    def render(self, fmt='PNG'):
        buffer = io.BytesIO()
        im=self.pil
        im.save(buffer, fmt)
        return buffer.getvalue()

    # methods for PIL.Image compatibility (see http://effbot.org/imagingbook/image.htm )

    @staticmethod
    def open(path):
        """PIL(low) compatibility"""
        return Image(path)

    @staticmethod
    def new(mode, size, color='black'):
        """PIL(low) compatibility"""
        return Image(mode=mode, size=size, color=color)

    @property
    def pil(self):
        """convert to PIL(low) Image
        :see: http://effbot.org/imagingbook/concepts.htm
        """
        a = self.getdata()
        im = PILImage.fromarray(a)
        if self.mode == 'P':
            im.putpalette(self.palette.pil)
        return im

    def getdata(self, dtype=np.uint8, copy=True):
        a = self.array
        if a.dtype == dtype:
            if copy:  # to be coherent
                a = np.copy(self.array)
        elif dtype == float:
            a = skimage.img_as_float(a, copy)
        elif dtype == np.int16:
            a = skimage.img_as_int(a, copy)
        elif dtype == np.uint16:
            a = skimage.img_as_uint(a, copy)
        elif dtype == np.uint8:
            a = skimage.img_as_ubyte(a, copy)
        else:
            pass  # keep the wrong type for now and see what happens
        return a

    def split(self, mode=None):
        if mode:
            mode = mode.upper()
        if mode and mode != self.mode:
            im = self.convert(mode)
        else:
            im = self
        if self.nchannels == 1:
            return [self]  # for coherency

        return [Image(im._get_channel(i)) for i in range(im.nchannels)]

    def getpixel(self, yx):
        if self.nchannels == 1:
            return self.array[yx[0], yx[1]]
        else:
            return self.array[yx[0], yx[1], :]

    def putpixel(self, yx, value):
        if isinstance(value, Gcolors.Color):
            value = value.convert(self.mode)
        if self.nchannels == 1:
            self.array[yx[0], yx[1]] = value
        else:
            self.array[yx[0], yx[1], :] = value

    def getpalette(self, maxcolors=256):
        if self.mode == 'P':
            return self.palette
        return Gcolors.Palette(self.getcolors(maxcolors))

    def setpalette(self, p):
        assert (self.mode == 'P')
        self.palette = Gcolors.Palette(p)

    def getcolors(self, maxcolors=256):
        """
        :return: an unsorted list of (count, color) tuples,
            where count is the number of times the corresponding color occurs in the image.

        If the maxcolors value is exceeded, the method stops counting and returns None.
        The default maxcolors value is 256.
        To make sure you get all colors in an image, you can pass in size[0]*size[1]
        (but make sure you have lots of memory before you do that on huge images).
        """
        if self.mode == 'P':
            im = self
        else:
            im = self.convert('P', colors=maxcolors)
        count = np.bincount(im.array.flatten())
        return zip(count, im.palette)  # return palette KEYS

    def replace(self, pairs):
        """replace a color by another
        currently works only for indexed color images
        :param pairs: iterable of (from,to) ints
        """
        # http://stackoverflow.com/questions/3403973/fast-replacement-of-values-in-a-numpy-array
        assert (self.mode == 'P')  # TODO: support other modes
        a = np.copy(self.array)
        for c in pairs:
            self.array[a == c[0]] = c[1]
        return self

    def optimize(self, maxcolors=256):
        """remove unused colors from the palette
        """
        assert (self.mode == 'P')
        hist = self.getcolors(maxcolors)
        # replace palette indices by in indices
        hist2 = []
        for i, c in enumerate(hist):
            hist2.append(tuple((i, c[1], c[0])))  # index, key, count
        # sort by decreasing occurences
        hist = sorted(hist2, key=lambda c: c[2], reverse=True)
        new = Gcolors.Palette()
        pairs = []
        for old, key, count in hist:
            i = len(new)
            if count == 0:
                break  # hist is in decreasing order, so it's over
            if i < maxcolors:
                new[key] = self.palette[key]  # copy useful color
                j = i
            else:  # find nearest color in new palette
                j = new.index(self.palette[key], 0)
                j = list(new.keys()).index(j)  # convert to numeric index
            pairs.append((old, j))  # add index substitution
        self.replace(pairs)
        self.palette = new
        return self

    def crop(self, lurb):
        """
        :param lurl: 4-tuple with left,up,right,bottom int coordinates
        :return: Image
        """
        l, u, r, b = lurb
        if self.nchannels == 1:
            a = self.array[u:b, l:r]
        else:
            a = self.array[u:b, l:r, :]
        return Image(a, self.mode)

    def __getitem__(self, slice):
        try:
            a = self.getpixel(slice)
        except TypeError:
            pass
        else:
            s = a.shape
            if len(s[:2]) <= 1:  # single pixel
                return a
            else:
                return Image(a, self.mode)

        l, u, r, b = slice[1].start, slice[0].start, slice[1].stop, slice[0].stop
        # calculate box module size so we handle negative coords like in slices
        w, h = self.size
        u = u % h if u else 0
        b = b % h if b else h
        l = l % w if l else 0
        r = r % w if r else w

        return self.crop((l, u, r, b))

    @property
    def ratio(self):
        return self.size[0] / self.size[1]

    def resize(self, size, filter=PILImage.BILINEAR, **kwargs):
        """Resize image

        :return: a resized copy of image.
        :param size: int tuple (width, height) requested size in pixels
        :param filter:
            * NEAREST (use nearest neighbour),
            * BILINEAR (linear interpolation in a 2x2 environment),
            * BICUBIC (cubic spline interpolation in a 4x4 environment)
            * LANCZOS (a high-quality downsampling filter)
        :param kwargs: extra parameters passed to skimage.transform.resize
        """

        if not kwargs:  # faster using PIL:
            return Image(self.pil.resize(size, filter))

        from skimage.transform import resize
        order = 0 if filter in (
            None, PILImage.NEAREST) else 1 if filter == PILImage.BILINEAR else 3
        order = kwargs.pop('order', order)
        array = resize(self.array, size, order, **
                       kwargs)  # preserve_range=True ?
        return Image(array, self.mode)

    def rotate(self, angle, **kwargs):
        """Rotate image

        :return: a rotated copy of image.
        :param angle: float rotation angle in degrees in counter-clockwork direction
        :param kwargs: extra parameters passed to skimage.transform.rotate
        """
        from skimage.transform import rotate
        # gives the best results in most cases
        kwargs.setdefault('mode', 'edge')
        array = rotate(self.array, angle, **kwargs)
        return Image(array, self.mode)

    def flip(self, flipx=True, flipy=False):
        """Flip image

        :return: a flipped copy of image.
        :param flipx: bool flip X direction
        :param flipy: bool flip Y direction
        :param kwargs: extra parameters passed to skimage.transform.rotate
        """
        array = self.array
        if flipx:
            array = np.fliplr(array)
        if flipy:
            array = np.flipud(array)
        return Image(array, self.mode)

    def paste(self, image, box=None, mask=None):
        """Pastes another image into this image.

        :param image: image to paste, or color given as a single numerical value
            for single-band images, and a tuple for multi-band images.
        :param box: 2-tuple giving the upper left corner
            or 4-tuple defining the left, upper, right, and lower pixel coordinate,
            or None (same as (0, 0)).
            If a 4-tuple is given, the size of the pasted image must match the size of the region.
        :param mask: optional image to update only the regions indicated by the mask.
            You can use either “1”, “L” or “RGBA” images (in the latter case, the alpha band is used as mask).
            Where the mask is 255, the given image is copied as is.
            Where the mask is 0, the current value is preserved.
            Intermediate values can be used for transparency effects.
            Note that if you paste an “RGBA” image, the alpha band is ignored.
            You can work around this by using the same image as both source image and mask.
        """
        if mask is not None:
            raise (NotImplementedError('masking not yet implemented'))
        if box is None:
            l, u = 0, 0
        else:
            # ignore r,b if they're specified, recalculated below
            l, u = box[0:2]
        h, w = image.size
        r, b = l + w, u + h
        try:
            self.array[u:b, l:r] = image.array
        except:
            self.array[u:b, l:r] = image.array
        return self

    def threshold(self, level=None):
        from skimage.filters import threshold_otsu
        if level is None:
            level = threshold_otsu(self.array)
        return Image(self.array > level, '1')

    def quantize(self, colors=256, method=None, kmeans=0, palette=None):
        """(PIL.Image compatible)
        Convert the image to 'P' mode with the specified number of colors.

        :param colors: The desired number of colors, <= 256
        :param method: 0 = median cut, 1 = maximum coverage, 2 = fast octree, 3 = libimagequant
        :param kmeans: Integer
        :param palette: Quantize to the :py:class:`PIL.ImagingPalette` palette.
        :returns: A new image
        """
        a = quantize(self.array, colors)
        return Image(a, 'P')

    def convert(self, mode, **kwargs):
        """convert image mode
        :param mode: string destination mode
        :param kwargs: optional params passed to converter(s). can contain:
        * palette : to force using a palette instead of the image's one for indexed images
        :return: image in desired mode
        """
        mode = mode.upper()
        if self.mode == 'P':
            kwargs.setdefault('palette', self.palette)
        a = convert(self.array, self.mode, mode, **kwargs)
        return Image(a, mode=mode)

    def _get_channel(self, channel):
        """Return a specific dimension out of the raw image data slice."""
        # https://github.com/scikit-image/scikit-image/blob/master/skimage/novice/_novice.py
        a = self.array[:, :, channel]
        return a

    def _set_channel(self, channel, value):
        """Set a specific dimension in the raw image data slice."""
        # https://github.com/scikit-image/scikit-image/blob/master/skimage/novice/_novice.py
        self.array[:, :, channel] = value

    # representations, data extraction and conversions

    def __repr__(self):
        s = getattr(self, 'shape', 'unknown')
        return "%s(mode=%s shape=%s type=%s)" % (
            self.__class__.__name__, self.mode, s, self.array.dtype.name
        )

    # hash and distance

    # http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
    # https://github.com/JohannesBuchner/imagehash/blob/master/imagehash/__init__.py

    def _hash_prepare(self, img_size=8):
        """common code for image hash methods below"""
        if self.nchannels > 1:
            image = self.grayscale()
        else:
            image = self
        while image.npixels > (img_size * 16) ** 2:
            s = image.size
            image = image.resize((s[0] // 8, s[1] // 8), PILImage.NEAREST)

        self.thumb = image.resize((img_size, img_size), PILImage.LANCZOS)
        return np.array(self.thumb.array, dtype=float).reshape((img_size, img_size))

    @staticmethod
    def _hash_result(result):
        return math2.num_from_digits(itertools2.flatten(result), 2)

    def average_hash(self, hash_size=8):
        """Average Hash

        :see: http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html

        :param hash_size: int sqrt of the hash size. 8 (64 bits) is perfect for usual photos
        :return: int of hash_size**2 bits
        """
        pixels = self._hash_prepare(hash_size)
        return Image._hash_result(pixels > pixels.mean())

    def perceptual_hash(self, hash_size=8, highfreq_factor=4):
        """Perceptual Hash

        :see: http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html

        :param hash_size: int sqrt of the hash size. 8 (64 bits) is perfect for usual photos
        :return: int of hash_size**2 bits
        """
        import scipy.fftpack
        pixels = self._hash_prepare(hash_size * highfreq_factor)
        dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
        dctlowfreq = dct[:hash_size, :hash_size]
        return Image._hash_result(dctlowfreq > np.median(dctlowfreq))

    def dist(self, other, method=AVERAGE, hash_size=8, symmetries=False):
        """ distance between images

        :param hash_size: int sqrt of the hash size. 8 (64 bits) is perfect for usual photos
        :return: float
            =0 if images are equal or very similar (same average_hash)
            =1 if images are completely decorrelated (half of the hash bits are the same by luck)
            =2 if images are inverted
        """
        def h(im):
            return [im.average_hash, im.perceptual_hash][method](hash_size)

        h1 = h(self)

        def diff(im):
            h2 = h(im)
            if h1 == h2:
                return 0
            # http://stackoverflow.com/questions/9829578/fast-way-of-counting-non-zero-bits-in-python
            d = bin(h1 ^ h2).count("1")  # ^is XOR
            return 2 * d / (hash_size * hash_size)

        d = diff(other)

        if d == 0 or not symmetries:
            return d

        other = other.thumb  # generated at _hash_prepare above

        res = []
        # try all 4 main rotations
        for sym in [itertools2.identity, lambda x: x.flip(True)]:
            im = sym(other)
            for rot in [
                itertools2.identity,
                lambda x: x.rotate(90), lambda x: x.rotate(90),
                # Y flip is faster + better than 180° rotation
                lambda x: x.flip(False, True)
            ]:
                r = diff(rot(im))
                if r < 0.01:
                    return r
                res.append(r)

        return min(res)

    def __hash__(self):
        return self.average_hash(8)

    def __abs__(self):
        """:return: float Frobenius norm of image"""
        return np.linalg.norm(self.array)

    def invert(self):
        return Image(modes[self.mode].max - self.array, self.mode)

    __neg__ = __inv__ = __invert__ = invert  # aliases

    def grayscale(self, mode=None):
        """convert (color) to grayscale
        :param mode: string target mode (should be in 'FUIL') or automatic if none
        """
        if mode is None:
            mode = 'F' if np.issubdtype(self.array.dtype, float) else 'L'
        return self.convert(mode)

    def colorize(self, color0, color1=None):
        """colorize a grayscale image

        :param color0,color1: 2 colors.
            - If only one is specified, image is colorized from white (for 0) to the specified color (for 1)
            - if 2 colors are specified, image is colorized from color0 (for 0) to color1 (for 1)
        :return: RGB(A) color
        """
        if color1 is None:
            color1 = color0
            color0 = 'white'
        color0 = Gcolors.Color(color0).rgb
        color1 = Gcolors.Color(color1).rgb
        a = gray2rgb(self.array, color0, color1)
        return Image(a, 'RGB')

    @adapt_rgb
    def dither(self, method=None, n=2):
        if method is None:
            method = FLOYDSTEINBERG
        a = dither(self.array, method, N=n)
        if n == 2:
            return Image(a, '1')
        else:
            return Image(a / (n - 1), 'F')

    def normalize(self, newmax=None, newmin=None):
        # http://stackoverflow.com/questions/7422204/intensity-normalization-of-image-using-pythonpil-speed-issues
        # warning : this normalizes each channel independently, so we don't use @adapt_rgb here
        newmax = newmax or modes[self.mode].max
        newmin = newmin or modes[self.mode].min
        arr = normalize(self.array, newmax, newmin)
        return Image(arr)

    @adapt_rgb
    def filter(self, f):
        try:  # scikit-image filter or similar ?
            a = f(self.array)
            return Image(a)
        except Exception:
            pass
        im = self.pil
        im = im.filter(f)
        return Image(im, mode=self.mode)

    def correlation(self, other):
        """Compute the correlation between two, single-channel, grayscale input images.
        The second image must be smaller than the first.
        :param other: the Image we're looking for
        """
        from scipy import signal
        input = self.array
        match = other.array
        c = signal.correlate2d(input, match)
        return Image(c)

    def scale(self, s):
        """resize image by factor s

        :param s: (sx, sy) tuple of float scaling factor, or scalar s=sx=sy
        :return: Image scaled
        """
        try:
            s[1]
        except:
            s = [s, s]

        if self.mode == 'P':
            a = self.array
            for axis, r in enumerate(s):
                a = np.repeat(a, r, axis=axis)
            return Image(a, 'P', colors=self.palette)

        w, h = self.size
        return self.resize((int(w * s[0] + 0.5), int(h * s[1] + 0.5)))

    @adapt_rgb
    def shift(self, dx, dy, **kwargs):
        from scipy.ndimage import shift as shift2
        a = shift2(self.array, (dy, dx), **kwargs)
        return Image(a, self.mode)

    def expand(self, size, ox=None, oy=None):
        """
        :return: image in larger canvas size, pasted at ox,oy
        """
        im = Image(None, self.mode, size=size, colormap=self.palette)
        (h, w) = self.size
        if w * h == 0:  # resize empty image...
            return im
        if ox is None:  # center
            ox = (size[1] - w) // 2
        elif ox < 0:  # from the right
            ox = size[1] - w + ox
        if oy is None:  # center
            oy = (size[0] - h) // 2
        elif oy < 0:  # from bottom
            oy = size[0] - h + oy
        if math2.is_integer(ox) and math2.is_integer(oy):
            im.paste(self, tuple(map(math2.rint, (ox, oy, ox + w, oy + h))))
        elif ox >= 0 and oy >= 0:
            im.paste(self, (0, 0, w, h))
            im = im.shift(ox, oy)
        else:
            # TODO; something for negative offsets...
            raise NotImplementedError()
        return im

    def compose(self, other, a=0.5, b=0.5, mode=None):
        """compose new image from a*self + b*other
        """
        mode = mode or 'F' if self.nchannels == 1 else 'RGB'
        if self:
            d1 = self.convert(mode).array
        else:
            d1 = None
        if other:
            d2 = other.convert(mode).array
        else:
            d2 = None
        if d1 is not None:
            if d2 is not None:
                return Image(a * d1 + b * d2, mode)
            else:
                return Image(a * d1, mode)
        else:
            return Image(b * d2, mode)

    def add(self, other, pos=(0, 0), alpha=1, mode=None):
        """ simply adds other image at px,py (subbixel) coordinates
        """
        # TOD: use http://stackoverflow.com/questions/9166400/convert-rgba-png-to-rgb-with-pil
        if self.npixels == 0:
            return Image(other * alpha)
        px, py = pos
        assert px >= 0 and py >= 0
        im1, im2 = self, other
        size = (max(im1.size[0], int(im2.size[0] + py + 0.999)),
                max(im1.size[1], int(im2.size[1] + px + 0.999)))
        if not im1.mode:  # empty image
            im1.mode = im2.mode
        im1 = im1.expand(size, 0, 0)
        im2 = im2.expand(size, px, py)
        return im1.compose(im2, 1, alpha, mode)

    def __add__(self, other):
        return self.add(other)

    def __radd__(self, other):
        """only to allow sum(images) easily"""
        assert other == 0
        return self

    def sub(self, other, pos=(0, 0), alpha=1, mode=None):
        return self.add(other, pos, -alpha, mode)

    def __sub__(self, other):
        return self.sub(other)
    
    def __eq__(self, other):
        if isinstance(other, Image):
            return np.all(self.array == other.array)
        return False

    def deltaE(self, other):
        import skimage.color as skcolor
        a = skcolor.deltaE_ciede2000(
            self.convert('LAB').array,
            other.convert('LAB').array,
        )
        return Image(a, 'F')

    def __mul__(self, other):
        if isinstance(other, str):
            return self.colorize('black', other)
        if math2.is_number(other):
            return self.compose(None, other)
        if other.nchannels > self.nchannels:
            return other * self
        if other.nchannels == 1:
            if self.nchannels == 1:
                return self.compose(None, other.array)
            rgba = list(self.split('RGBA'))
            rgba[-1] = rgba[-1] * other
            return Image(rgba, 'RGBA')
        raise NotImplementedError('%s * %s' % (self, other))

    def __div__(self, f):
        return self * (1 / f)

    __truediv__ = __div__


def alpha_composite(front, back):
    """Alpha composite two RGBA images.

    Source: http://stackoverflow.com/a/9166671/284318

    Keyword Arguments:
    front -- PIL RGBA Image object
    back -- PIL RGBA Image object

    The algorithm comes from http://en.wikipedia.org/wiki/Alpha_compositing

    """
    front = np.asarray(front)
    back = np.asarray(back)
    result = np.empty(front.shape, dtype=float)
    alpha = np.index_exp[:, :, 3:]
    rgb = np.index_exp[:, :, :3]
    falpha = front[alpha] / 255.0
    balpha = back[alpha] / 255.0
    result[alpha] = falpha + balpha * (1 - falpha)
    old_setting = np.seterr(invalid='ignore')
    result[rgb] = (front[rgb] * falpha + back[rgb] *
                   balpha * (1 - falpha)) / result[alpha]
    np.seterr(**old_setting)
    result[alpha] *= 255
    np.clip(result, 0, 255)
    # astype('uint8') maps np.nan and np.inf to 0
    result = result.astype(np.uint8)
    result = PILImage.fromarray(result, 'RGBA')
    return result


def alpha_composite_with_color(image, color=(255, 255, 255)):
    """Alpha composite an RGBA image with a single color image of the
    specified color and the same size as the original image.

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 255, 255, 255)

    """
    back = PILImage.new('RGBA', size=image.size, color=color + (255,))
    return alpha_composite(image, back)


def pure_pil_alpha_to_color_v1(image, color=(255, 255, 255)):
    """Alpha composite an RGBA Image with a specified color.

    NOTE: This version is much slower than the
    alpha_composite_with_color solution. Use it only if
    numpy is not available.

    Source: http://stackoverflow.com/a/9168169/284318

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 255, 255, 255)

    """

    def blend_value(back, front, a):
        return (front * a + back * (255 - a)) / 255

    def blend_rgba(back, front):
        result = [int(round(blend_value(back[i], front[i], front[3]))) for i in (0, 1, 2)]
        return tuple(result + [255])

    im = image.copy()  # don't edit the reference directly
    p = im.load()  # load pixel array
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            p[x, y] = blend_rgba(color + (255,), p[x, y])

    return im


def pure_pil_alpha_to_color_v2(image, color=(255, 255, 255)):
    """Alpha composite an RGBA Image with a specified color.

    Simpler, faster version than the solutions above.

    Source: http://stackoverflow.com/a/9459208/284318

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 255, 255, 255)

    """
    image.load()  # needed for split()
    background = PILImage.new('RGB', image.size, color)
    background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
    return background


def disk(radius, antialias=PILImage.LANCZOS):
    from skimage.draw import disk as skdisk
    size = math2.rint(2 * radius)
    size = (size, size)
    img = np.zeros(size, dtype=np.double)
    rr, cc = skdisk((radius, radius), radius)
    img[rr, cc] = 1
    # antialiased perimeter works only with ints ?
    """
    rr, cc, val = circle_perimeter_aa(radius,radius,radius)
    img[rr, cc] = val
    """
    return Image(img)


def fspecial(name, **kwargs):
    """mimics the Matlab image toolbox fspecial function
    http://www.mathworks.com/help/images/ref/fspecial.html?refresh=true
    """
    if name == 'disk':
        return disk(kwargs.get('radius', 5))  # 5 is default in Matlab
    raise NotImplementedError()


def normalize(a, newmax=255, newmin=0):
    # http://stackoverflow.com/questions/7422204/intensity-normalization-of-image-using-pythonpil-speed-issues
    # warning : don't use @adapt_rgb here as it would normalize each channel independently
    array = np.array(a)
    t = array.dtype
    if len(array.shape) == 2:  # single channel
        n = 1
        minval = array.min()
        maxval = array.max()
        array += newmin - minval
        if maxval is not None and minval != maxval:
            array = array.astype(float)
            array *= newmax / (maxval - minval)
    else:
        n = min(array.shape[2], 3)  # if RGBA, ignore A channel
        minval = array[:, :, 0:n].min()
        maxval = array[:, :, 0:n].max()
        array = array.astype(float)
        for i in range(n):
            array[..., i] += newmin - minval
            if maxval is not None and minval != maxval:
                array[..., i] *= newmax / (maxval - minval)
    return array.astype(t)


def read_pdf(filename, **kwargs):
    """ reads a bitmap graphics on a .pdf file
    only the first page is parsed
    """
    from pdfminer.pdfparser import PDFParser
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfinterp import PDFResourceManager
    from pdfminer.pdfinterp import PDFPageInterpreter
    from pdfminer.pdfdevice import PDFDevice
    # PDF's are fairly complex documents organized hierarchically
    # PDFMiner parses them using a stack and calls a "Device" to process entities
    # so here we define a Device that processes only "paths" one by one:

    class _Device(PDFDevice):

        def render_image(self, name, stream):
            try:
                self.im = PILImage.open(io.BytesIO(stream.rawdata))
            except Exception as e:
                logging.error(e)

    # then all we have to do is to launch PDFMiner's parser on the file
    fp = open(filename, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser, fallback=False)
    rsrcmgr = PDFResourceManager()
    device = _Device(rsrcmgr)
    device.im = None  # in case we can't find an image in file
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        break  # handle one page only

    im = device.im

    if im is None:  # it's maybe a drawing
        fig = drawing.Drawing(filename).draw(**kwargs)
        im = fig2img(fig)

    return im


def fig2img(fig):
    """
    Convert a Matplotlib figure to a PIL Image in RGBA format and return it

    :param fig: matplotlib figure
    :return: PIL image
    """
    # http://www.icare.univ-lille1.fr/wiki/index.php/How_to_convert_a_matplotlib_figure_to_a_numpy_array_or_a_PIL_image

    fig.canvas.draw()

    # Get the RGBA buffer from the figure
    w, h = fig.canvas.get_width_height()
    buf = np.fromstring(fig.canvas.tostring_argb(), dtype=np.uint8)
    buf.shape = (w, h, 4)

    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = np.roll(buf, 3, axis=2)
    w, h, _ = buf.shape
    return PILImage.frombytes("RGBA", (w, h), buf.tostring())

# from https://github.com/scikit-image/skimage-demos/blob/master/dither.py
# see https://bitbucket.org/kuraiev/halftones for more


def quantize(image, N=2, L=None):
    """Quantize a gray image.
    :param image: ndarray input image.
    :param N: int number of quantization levels.
    :param L: float max value.
    """
    L = L or modes[guessmode(image)].max  # max level of image
    T = np.linspace(0, L, N, endpoint=False)[1:]
    return np.digitize(image.flat, T).reshape(image.shape)


def randomize(image, N=2, L=None):
    L = L or modes[guessmode(image)].max  # max level of image
    img_dither_random = image + \
        np.abs(np.random.normal(size=image.shape, scale=L / (3 * N)))
    return quantize(img_dither_random, N, L)


class Ditherer(object):

    def __init__(self, name, method):
        self.name = name
        self.method = method

    def __call__(self, image, N=2):
        return self.method(image, N)

    def __repr__(self):
        return self.name


class ErrorDiffusion(Ditherer):

    def __init__(self, name, positions, weights, wsum=None):
        Ditherer.__init__(self, name, None)
        if not wsum:
            wsum = sum(weights)
        weights = math2.vecdiv(weights, wsum)
        self.matrix = list(zip(positions, weights))

    def __call__(self, image, N=2):
        image = skimage.img_as_float(image, True)  # normalize to [0..1]
        T = np.linspace(0., 1., N, endpoint=False)[1:]
        out = np.zeros_like(image, dtype=int)

        rows, cols = image.shape
        for i in range(rows):
            for j in range(cols):
                # Quantize
                out[i, j], = np.digitize(
                    [image[i, j]], T)  # pylint: disable=unsupported-assignment-operation

                # Propagate quantization noise
                d = (image[i, j] - out[i, j] / (N - 1))
                for (ii, jj), w in self.matrix:
                    ii = i + ii
                    jj = j + jj
                    if ii < rows and jj < cols:
                        image[ii, jj] += d * w

        return out


class FloydSteinberg(ErrorDiffusion):

    def __init__(self):
        ErrorDiffusion.__init__(self, 'floyd-steinberg',
                                positions=[(0, 1), (1, -1), (1, 0), (1, 1)],
                                weights=[7, 3, 5, 1]
                                )

    def __call__(self, image, N=2):
        return ErrorDiffusion.__call__(self, image, N)

# PIL+SKIMAGE dithering methods


NEAREST = PILImage.NEAREST
FLOYDSTEINBERG = PILImage.FLOYDSTEINBERG
PHILIPS = FLOYDSTEINBERG + 1
SIERRA = PHILIPS + 1
STUCKI = SIERRA + 1
JARVIS = STUCKI + 1
ATKINSON = JARVIS + 1
BURKES = ATKINSON + 1
RANDOM = JARVIS + 10

dithering = {
    NEAREST: Ditherer('nearest', quantize),
    RANDOM: Ditherer('random', randomize),
    # ORDERED : 'ordered', # Not yet implemented in Pillow
    # RASTERIZE : 'rasterize', # Not yet implemented in Pillow
    FLOYDSTEINBERG: FloydSteinberg(),
    PHILIPS: ErrorDiffusion('philips',
                            [(0, 0)], [1]),  # http://www.google.com/patents/WO2002039381A2
    SIERRA: ErrorDiffusion('sierra lite',
                           [(0, 1), (1, -1), (1, 0)], [2, 1, 1]),
    STUCKI: ErrorDiffusion('stucki',
                           positions=[(0, 1), (0, 2),
                                      (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
                                      (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)],
                           weights=[8, 4,
                                    2, 4, 8, 4, 2,
                                    1, 2, 4, 2, 1]
                           ),
    JARVIS: ErrorDiffusion('Jarvis, Judice, and Ninke',
                           # http://www.tannerhelland.com/4660/dithering-eleven-algorithms-source-code/
                           positions=[(0, 1), (0, 2),
                                      (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
                                      (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)],
                           weights=[7, 5,
                                    3, 5, 7, 5, 3,
                                    1, 3, 4, 3, 1]
                           ),
    ATKINSON: ErrorDiffusion('Atkinson',
                             positions=[(0, 1), (0, 2),
                                        (1, -1), (1, 0), (1, 1),
                                        (2, 0)],
                             weights=[1, 1, 1, 1, 1, 1],
                             wsum=8
                             ),

    BURKES: ErrorDiffusion('Burkes',
                           positions=[(0, 1), (0, 2),
                                      (1, -2), (1, -1), (1, 0), (1, 1), (1, 2)],
                           weights=[8, 4, 2, 4, 8, 4, 2]
                           ),
}


def dither(image, method=FLOYDSTEINBERG, N=2):
    """Quantize a gray image, using dithering.
    :param image: ndarray input image.
    :param method: key in dithering dict
    :param N: int number of quantization levels.
    References
    ----------
    http://www.efg2.com/Lab/Library/ImageProcessing/DHALF.TXT
    """
    if method in dithering:
        return dithering[method](image, N)
    logging.warning(
        'dithering method %s not yet implemented. fallback to Floyd-Steinberg' % dithering[method])
    return dither(image, FLOYDSTEINBERG, N)

# converter functions complementing those in skimage.color are defined below
# function should be named "source2dest" in order to be inserted in converters graph


gray2bool = dither


def rgb2cmyk(rgb):
    from skimage.color.colorconv import _prepare_colorarray
    arr = _prepare_colorarray(rgb)

    cmy = 1 - arr

    k = np.amin(cmy, axis=2)
    w = 1  # -k
    c = (cmy[:, :, 0] - k) / w
    m = (cmy[:, :, 1] - k) / w
    y = (cmy[:, :, 2] - k) / w

    return np.concatenate([x[..., np.newaxis] for x in [c, m, y, k]], axis=-1)


def cmyk2rgb(cmyk):
    cmyk = np.asanyarray(cmyk)
    cmyk = skimage.img_as_float(cmyk)

    k = 1 - cmyk[:, :, 3]
    w = 1  # -k
    r = k - cmyk[:, :, 0] * w
    g = k - cmyk[:, :, 1] * w
    b = k - cmyk[:, :, 2] * w

    return np.concatenate([x[..., np.newaxis] for x in [r, g, b]], axis=-1)


def gray2rgb(im, color0=(0, 0, 0), color1=(1, 1, 1)):
    im = skimage.img_as_float(im)
    color0 = np.asarray(color0, float)
    color1 = np.asarray(color1, float)
    d = color1 - color0
    a = np.outer(im, d)
    a = a.reshape([im.shape[0], im.shape[1], d.shape[0]]) + color0

    return a


bool2rgb = gray2rgb  # works also


def bool2gray(im):
    return im * 255


def rgb2rgba(array):
    s = array.shape
    if s[2] == 4:  # already RGBA
        return array
    a = np.ones((s[0], s[1], 1), array.dtype)
    array = np.append(array, a, 2)
    return array


try:
    skcolor.rgba2rgb  # will be available soon
except:

    def rgba2rgb(array):
        # trivial version ignoring alpha channel for now
        return array[:, :, :3]


def palette(im, ncolors, tol=1 / 100):
    """extract the color palette of image array
    (in its own colorspace. use Lab for best results)
    :param im: nparray (x,y,n) containing image
    :param ncolors: int number of colors
    :param tol: tolerance for precision/speed compromise.
    1/100 means about 100 points per color are taken for kmeans segmentation
    :return: array of ncolors most used in image (center of kmeans centroids)
    """
    # http://scikit-learn.org/stable/auto_examples/cluster/plot_color_quantization.html
    # but without scipy-learn (for now)
    from scipy.cluster.vq import kmeans
    w, h, d = im.shape
    s = w * h  # number of pixels
    im = np.reshape(im, (s, d))  # flatten for kmeans
    # keep only ~100 points per color for speed
    decimate = int(tol * s / ncolors)
    if decimate > 1:
        im = im[::decimate]
    return kmeans(im, ncolors)[0]


def lab2ind(im, colors=256):
    """convert a Lab image to indexed colors
    :param a: nparray (x,y,n) containing image
    :param colors: int number of colors or predefined Palette
    :ref: http://scikit-learn.org/stable/auto_examples/cluster/plot_color_quantization.html
    """
    # http://stackoverflow.com/questions/10818546/finding-index-of-nearest-point-in-numpy-arrays-of-x-and-y-coordinates
    if isinstance(colors, int):
        p = palette(im, colors)  #
        pal = [Gcolors.Color(c, 'lab') for c in p]
    else:
        pal = colors
        p = [c.lab for c in itertools2.flatten(pal)]
    w, h, d = im.shape
    s = w * h  # number of pixels
    flat = np.reshape(im, (s, d))
    from scipy.spatial import cKDTree as KDTree  # compiled is MUCH faster
    mytree = KDTree(p)
    _, indexes = mytree.query(flat)
    im = indexes.reshape(w, h)
    return im, pal


def ind2any(im, palette, dest):
    palette = [c.convert(dest) for c in palette.values()]
    w, h = im.shape
    image = np.zeros((w, h, 3))
    for i in range(w):
        for j in range(h):
            image[i, j] = palette[im[i, j]]
    return image


def ind2rgb(im, palette):
    return ind2any(im, palette, 'rgb')

# build a graph of available converters
# inspired by https://github.com/gtaylor/python-colormath
# WATCH OUT! converters must be defined above this line...


# a nx.DiGraph() would suffice, but my DiGraph are better
converters = graph.DiGraph(multi=False, tol=0)
for source in modes:
    for target in modes:
        key = (modes[source].name, modes[target].name)
        if key[0] == key[1]:
            continue
        convname = '%s2%s' % key

        converter = getattr(sys.modules[__name__], convname, None)
        if converter is None:
            converter = getattr(skcolor, convname, None)

        if converter:
            converters.add_edge(key[0], key[1], f=converter)

def convert_type(data, type):
    """convert inner format of image
    :param data: nparray (x,y,n) containing image
    :param type: target np.type
    :return: nparray (x,y,n) with new type
    replaces outdated skimage.util.dtype.convert using 
    https://scikit-image.org/docs/0.24.x/api/skimage.html#utility-functions
    """
    if type==np.uint8:
        return skimage.img_as_ubyte(data)
    elif type==np.uint16:
        return skimage.img_as_uint(data)
    elif type==np.int16:
        return skimage.img_as_int(data)
    elif type==float:
        return skimage.img_as_float(data)
    elif type==np.float32:
        return skimage.img_as_float32(data)
    elif type==np.float64:
        return skimage.img_as_float64(data)
    else:
        raise ValueError('unsupported type %s'%type)

def convert(a, source:Mode, target:Mode, **kwargs):
    """convert an image between modes, eventually using intermediary steps
    :param a: nparray (x,y,n) containing image
    :param source: string : key of source image mode in modes
    :param target: string : key of target image mode in modes
    """
    import networkx as nx  # http://networkx.github.io/
    source, target = modes[source.upper()], modes[target.upper()]
    a = np.copy(a)  # Ensure the array is writable
    a = np.clip(a, source.min, source.max, out=a)
    a = np.clip(a, source.min, source.max, out=a)
    try:
        path = converters.shortest_path(source.name, target.name)
    except nx.exception.NetworkXError:
        raise NotImplementedError(
            'no conversion between %s and %s modes'
            % (source.name, target.name)
        )

    for u, v in itertools2.pairwise(path):
        if u == v:
            continue  # avoid converting from gray to gray
        try:
            edge = converters[u][v][0]
        except:
            path = converters.shortest_path(source.name, target.name)
            pass  # but something is wrong...
        f = edge['f']
        try:
            a = f(a, **kwargs)
        except TypeError as e:
            if kwargs:  # maybe the converter doesn't support args ? retry!
                a = f(a)
            else:
                raise (e)

    try:
        a = convert_type(a, target.type)
    except ValueError as e:  # probably a tuple (indexed, palette)
        pass  # do not force int type here
        # a=tuple((skimage.util.dtype.convert(a[0],target.type),a[1]))
    return a  # isn't it beautiful ?
